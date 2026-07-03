#!/usr/bin/env python3
# pip install: numpy "jax[cpu]" numpyro   (demo tested on numpyro 0.21, jax 0.10)
"""Elasticity recovery shootout on synthetic data with known ground truth.

One synthetic world, five estimators. The world has the two diseases real
price-quantity panels have:

  1. Simultaneity: the category manager raises price when demand runs hot
     (log p loads on the same demand shock d that drives log q), so naive
     within-cell regression recovers the manager's rule, with the wrong sign.
  2. Cross-sectional confounding: premium SKUs carry different baselines,
     so pooled OLS without fixed effects mixes a cross-sectional pseudo-
     elasticity into the estimate.

There is one honest source of identifying variation: a wholesale-cost
shifter z that moves price and stays out of the demand equation.

Estimators, in the order a consultant should distrust them:
  A. pooled OLS log-log                 (both diseases)
  B. cell fixed-effects OLS             (cures 2, not 1)
  C. pooled 2SLS with cost IV + FE      (cures both; one number for all cells)
  D. per-cell 2SLS, no pooling          (unbiased-ish, drowns in noise)
  E. hierarchical Bayes + control function (numpyro): first-stage price
     residual v_hat enters the demand equation, so the price coefficient is
     identified from the cost-driven variation, while partial pooling across
     SKU and region shrinks cell noise.

Output: a recovery table (mean estimate, cell-level RMSE, sign errors) plus
90% credible-interval coverage for E. Truth: mean elasticity -1.80,
promo lift +0.55 on log quantity. Runs in a few minutes on CPU.
"""

import numpy as np

import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro import diagnostics
from numpyro.infer import MCMC, NUTS

numpyro.set_host_device_count(2)


def make_world(J=30, S=6, T=52, seed=3):
    """Panel of J SKUs x S regions x T weeks with known cell elasticities."""
    rng = np.random.default_rng(seed)
    mu_beta = -1.80
    beta = (mu_beta
            + rng.normal(0, 0.45, J)[:, None]          # SKU spread
            + rng.normal(0, 0.20, S)[None, :]          # region spread
            + rng.normal(0, 0.10, (J, S)))             # idiosyncratic
    lp0 = np.log(60.0) + rng.normal(0, 0.30, J)        # SKU price level
    alpha = (3.5 - 0.5 * (lp0 - np.log(60.0))[:, None] # premium -> lower base
             + rng.normal(0, 0.30, (J, S)))

    z = rng.normal(0, 0.15, (J, T))                    # log cost shifter
    d = rng.normal(0, 0.35, (J, S, T))                 # demand shock
    promo = rng.binomial(1, 0.15, (J, S, T)).astype(float)
    gamma = 0.55                                       # promo lift, log scale

    # Manager's pricing rule: cost pass-through + reaction to demand heat.
    log_p = (lp0[:, None, None] + 0.6 * z[:, None, :] + 0.20 * d
             + rng.normal(0, 0.05, (J, S, T)))
    log_q = (alpha[:, :, None] + beta[:, :, None] * log_p + gamma * promo
             + d + rng.normal(0, 0.25, (J, S, T)))

    sku, reg = np.meshgrid(np.arange(J), np.arange(S), indexing="ij")
    flat = dict(
        log_p=log_p.reshape(-1), log_q=log_q.reshape(-1),
        promo=promo.reshape(-1),
        z=np.broadcast_to(z[:, None, :], (J, S, T)).reshape(-1),
        sku=np.repeat(sku.reshape(-1), T), reg=np.repeat(reg.reshape(-1), T),
        cell=np.repeat(np.arange(J * S), T),
    )
    return flat, beta.reshape(-1), gamma, J, S, T


def ols(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def within(v, cell, n_cells):
    """Demean by cell (fixed-effects transform)."""
    means = np.bincount(cell, v, n_cells) / np.bincount(cell, None, n_cells)
    return v - means[cell]


def tsls(y, x_endog, Z, X_exog):
    """2SLS: instrument x_endog with Z, exogenous controls X_exog."""
    W = np.column_stack([Z, X_exog])
    F = np.column_stack([x_endog, X_exog])
    fitted = W @ ols(W, F)
    b = ols(fitted, y)
    return b[0]


def fit_hb_control_function(flat, J, S, n_cells):
    """Hierarchical Bayes demand model with a control function for price."""
    # First stage: within-cell price on cost shifter; residual carries the
    # demand-shock part of price.
    lp_w = within(flat["log_p"], flat["cell"], n_cells)
    z_w = within(flat["z"], flat["cell"], n_cells)
    pi = ols(z_w[:, None], lp_w)
    v_hat = lp_w - z_w * pi[0]

    # The slope regressor is within-cell centred log price. Raw log price has
    # level ~4.1 against within-cell sd ~0.12, which welds each cell's
    # intercept to its slope along a ridge (a_c ~= ybar_c - beta_c * 4.1) and
    # stalls NUTS on mu_beta; centring makes intercept and slope near-
    # orthogonal. The intercept then absorbs alpha_c + beta_c * mean(log p)_c,
    # which costs nothing: elasticity is identified from within variation.
    lq, lp = jnp.array(flat["log_q"]), jnp.array(lp_w)
    promo, vh = jnp.array(flat["promo"]), jnp.array(v_hat)
    cell = jnp.array(flat["cell"])

    def model():
        mu_b = numpyro.sample("mu_beta", dist.Normal(-1.5, 1.0))
        sd_sku = numpyro.sample("sd_sku", dist.HalfNormal(0.5))
        sd_reg = numpyro.sample("sd_reg", dist.HalfNormal(0.3))
        sd_cell = numpyro.sample("sd_cell", dist.HalfNormal(0.2))
        with numpyro.plate("skus", J):
            zb_j = numpyro.sample("zb_j", dist.Normal(0, 1))
        with numpyro.plate("regions", S):
            zb_s = numpyro.sample("zb_s", dist.Normal(0, 1))
        with numpyro.plate("cells", n_cells):
            zb_c = numpyro.sample("zb_c", dist.Normal(0, 1))
            a_c = numpyro.sample("a_c", dist.Normal(0, 3))
        beta_c = numpyro.deterministic(
            "beta_cell", mu_b + sd_sku * zb_j[jnp.arange(n_cells) // S]
            + sd_reg * zb_s[jnp.arange(n_cells) % S] + sd_cell * zb_c)
        gamma = numpyro.sample("gamma", dist.Normal(0.5, 0.5))
        rho = numpyro.sample("rho", dist.Normal(0, 2))
        sigma = numpyro.sample("sigma", dist.HalfNormal(0.5))
        mu = a_c[cell] + beta_c[cell] * lp + gamma * promo + rho * vh
        numpyro.sample("obs", dist.Normal(mu, sigma), obs=lq)

    mcmc = MCMC(NUTS(model, target_accept_prob=0.9), num_warmup=700,
                num_samples=700, num_chains=2, chain_method="sequential",
                progress_bar=False)
    mcmc.run(jax.random.PRNGKey(0))
    post = mcmc.get_samples()
    grouped = mcmc.get_samples(group_by_chain=True)
    stats = diagnostics.summary(grouped, prob=0.9)
    max_rhat = max(float(np.max(v["r_hat"])) for v in stats.values())
    return post, pi[0], max_rhat


if __name__ == "__main__":
    flat, beta_true, gamma_true, J, S, T = make_world()
    n_cells = J * S
    mean_true = beta_true.mean()
    print(f"world: {J} SKUs x {S} regions x {T} weeks, "
          f"true mean elasticity {mean_true:+.2f}\n")

    rows = []

    def score(name, est_cells):
        rmse = float(np.sqrt(np.mean((est_cells - beta_true) ** 2)))
        sign = int(np.sum(est_cells >= 0))
        rows.append((name, float(np.mean(est_cells)), rmse, sign))

    # A. pooled OLS
    Xa = np.column_stack([np.ones_like(flat["log_p"]), flat["log_p"],
                          flat["promo"]])
    bA = ols(Xa, flat["log_q"])[1]
    score("A pooled OLS", np.full(n_cells, bA))

    # B. cell-FE OLS
    yw = within(flat["log_q"], flat["cell"], n_cells)
    pw = within(flat["log_p"], flat["cell"], n_cells)
    prw = within(flat["promo"], flat["cell"], n_cells)
    bB = ols(np.column_stack([pw, prw]), yw)[0]
    score("B cell-FE OLS", np.full(n_cells, bB))

    # C. pooled 2SLS with cost IV, cell FE
    zw = within(flat["z"], flat["cell"], n_cells)
    bC = tsls(yw, pw, zw[:, None], prw[:, None])
    score("C pooled 2SLS+FE", np.full(n_cells, bC))

    # D. per-cell 2SLS
    bD = np.empty(n_cells)
    for cidx in range(n_cells):
        m = flat["cell"] == cidx
        one = np.ones(m.sum())
        bD[cidx] = tsls(flat["log_q"][m], flat["log_p"][m],
                        flat["z"][m][:, None],
                        np.column_stack([one, flat["promo"][m]]))
    score("D per-cell 2SLS", bD)

    # E. hierarchical Bayes + control function
    post, pi1, max_rhat = fit_hb_control_function(flat, J, S, n_cells)
    bE = np.asarray(post["beta_cell"].mean(axis=0))
    score("E HB + control fn", bE)

    print(f"{'method':<20}{'mean est':>10}{'cell RMSE':>11}{'sign errs':>11}")
    for name, mean_est, rmse, sign in rows:
        print(f"{name:<20}{mean_est:>+10.2f}{rmse:>11.2f}{sign:>11d}")

    lo = np.percentile(np.asarray(post["beta_cell"]), 5, axis=0)
    hi = np.percentile(np.asarray(post["beta_cell"]), 95, axis=0)
    cover = float(np.mean((beta_true >= lo) & (beta_true <= hi)))
    g = np.asarray(post["gamma"])
    print(f"\nE extras: 90% CI coverage of truth {cover:.2f} (target 0.90); "
          f"promo lift {g.mean():+.2f} +/- {g.std():.2f} "
          f"(truth {gamma_true:+.2f}); first-stage pass-through {pi1:.2f} "
          f"(truth 0.60); max r_hat {max_rhat:.3f}")
    print("\nreading: A and B are catastrophically wrong with tight standard "
          "errors; C fixes the mean and misses the spread; D is honest and "
          "unusable; E is the deployable one.")
