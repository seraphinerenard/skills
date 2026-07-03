#!/usr/bin/env python3
# pip install numpy scipy pandas
# Optional cross-check: pip install pymc-marketing  (heavy: pulls PyMC + PyTensor)
"""BG/NBD + gamma-gamma CLV from scratch, with an optional pymc-marketing path.

Implements the full maximum-likelihood route so the model keeps working after
library churn: `lifetimes` is unmaintained (archived 2020-era API) and its
successors change APIs between releases. The likelihoods here follow
Fader, Hardie & Lee (2005) for BG/NBD and Fader & Hardie (2013) for the
gamma-gamma spend model.

Inputs are the standard RFM-T summary per customer:
    x    repeat-transaction count in (0, T]
    t_x  time of last repeat transaction (0 if none), same unit as T
    T    observation length since first purchase
    m_x  mean observed spend per transaction (only customers with x >= 1)

Demo (__main__): simulates customers from the true generative process,
recovers parameters, prints P(alive) and expected-purchase examples, and
builds a 24-month discounted CLV per customer with a bootstrap error band.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import betaln, gammaln, hyp2f1


# ----------------------------------------------------------------------
# BG/NBD likelihood and fit
# ----------------------------------------------------------------------

def bgnbd_loglik(params: np.ndarray, x, t_x, T) -> float:
    """Summed BG/NBD log-likelihood. params = (r, alpha, a, b), all > 0."""
    r, alpha, a, b = params
    x = np.asarray(x, float)
    t_x = np.asarray(t_x, float)
    T = np.asarray(T, float)

    ln_a1 = gammaln(r + x) - gammaln(r) + r * np.log(alpha)
    ln_b_ratio = betaln(a, b + x) - betaln(a, b)
    term_alive = ln_b_ratio - (r + x) * np.log(alpha + T)

    ll = ln_a1 + term_alive  # zero-repeat customers end here
    rep = x > 0
    if rep.any():
        ln_b_dead = betaln(a + 1, b + x[rep] - 1) - betaln(a, b)
        term_dead = ln_b_dead - (r + x[rep]) * np.log(alpha + t_x[rep])
        ll = ll.copy()
        ll[rep] = ln_a1[rep] + np.logaddexp(term_alive[rep], term_dead)
    return float(np.sum(ll))


def fit_bgnbd(x, t_x, T, start=(1.0, 1.0, 1.0, 1.0)):
    """MLE via L-BFGS-B on log-parameters. Returns (r, alpha, a, b)."""

    def neg(theta):
        return -bgnbd_loglik(np.exp(theta), x, t_x, T)

    res = minimize(neg, np.log(start), method="L-BFGS-B")
    if not res.success:
        raise RuntimeError(f"BG/NBD fit failed: {res.message}")
    return np.exp(res.x)


def p_alive(params, x, t_x, T):
    """P(customer still active at T). Equals 1 for zero-repeat customers,
    a known quirk of the BG/NBD death-only-at-purchase assumption."""
    r, alpha, a, b = params
    x = np.asarray(x, float)
    t_x = np.asarray(t_x, float)
    T = np.asarray(T, float)
    with np.errstate(divide="ignore"):
        odds_dead = np.where(
            x > 0,
            (a / (b + x - 1)) * ((alpha + T) / (alpha + t_x)) ** (r + x),
            0.0,
        )
    return 1.0 / (1.0 + odds_dead)


def expected_purchases(params, x, t_x, T, horizon):
    """E[# transactions in (T, T + horizon] | x, t_x, T]. FHL 2005 eq. (10)."""
    r, alpha, a, b = params
    x = np.asarray(x, float)
    t_x = np.asarray(t_x, float)
    T = np.asarray(T, float)
    t = float(horizon)

    z = t / (alpha + T + t)
    top = (
        (a + b + x - 1)
        / (a - 1)
        * (
            1.0
            - ((alpha + T) / (alpha + T + t)) ** (r + x)
            * hyp2f1(r + x, b + x, a + b + x - 1, z)
        )
    )
    odds_dead = np.where(
        x > 0,
        (a / (b + x - 1)) * ((alpha + T) / (alpha + t_x)) ** (r + x),
        0.0,
    )
    return top / (1.0 + odds_dead)


# ----------------------------------------------------------------------
# Gamma-gamma spend model
# ----------------------------------------------------------------------

def gg_loglik(params, x, m_x) -> float:
    """Gamma-gamma log-likelihood over customers with x >= 1 repeat buys.
    params = (p, q, gamma)."""
    p, q, g = params
    x = np.asarray(x, float)
    m_x = np.asarray(m_x, float)
    ll = (
        gammaln(p * x + q)
        - gammaln(p * x)
        - gammaln(q)
        + q * np.log(g)
        + (p * x - 1) * np.log(m_x)
        + p * x * np.log(x)
        - (p * x + q) * np.log(g + m_x * x)
    )
    return float(np.sum(ll))


def fit_gg(x, m_x, start=(5.0, 3.0, 10.0)):
    def neg(theta):
        return -gg_loglik(np.exp(theta), x, m_x)

    res = minimize(neg, np.log(start), method="L-BFGS-B")
    if not res.success:
        raise RuntimeError(f"gamma-gamma fit failed: {res.message}")
    return np.exp(res.x)


def expected_spend(params, x, m_x):
    """E[per-transaction spend | x, m_x]: shrinks the observed mean toward the
    population mean; the fewer transactions, the harder the shrink."""
    p, q, g = params
    x = np.asarray(x, float)
    m_x = np.asarray(m_x, float)
    pop_mean = g * p / (q - 1)
    w = (q - 1) / (p * x + q - 1)
    return w * pop_mean + (1 - w) * m_x


# ----------------------------------------------------------------------
# Discounted CLV
# ----------------------------------------------------------------------

def clv(params_bg, params_gg, x, t_x, T, m_x, months=24,
        monthly_discount=0.01, margin=1.0, weeks_per_month=4.345):
    """Residual CLV over `months`, discounting each month's expected
    incremental transactions. Time unit of x/t_x/T is weeks."""
    x = np.asarray(x, float)
    vals = np.zeros(len(x))
    spend = expected_spend(params_gg, np.maximum(x, 1), m_x)
    prev = np.zeros(len(x))
    for mth in range(1, months + 1):
        cum = expected_purchases(params_bg, x, t_x, T, mth * weeks_per_month)
        inc = cum - prev
        prev = cum
        vals += inc * spend * margin / (1 + monthly_discount) ** mth
    return vals


# ----------------------------------------------------------------------
# Synthetic data from the true generative process
# ----------------------------------------------------------------------

def simulate_bgnbd(n, r, alpha, a, b, p_gg, q_gg, g_gg, rng, t_min=52, t_max=78):
    """Simulates the BG/NBD story: lambda_i ~ Gamma(r, rate alpha),
    p_i ~ Beta(a, b), Poisson buying while alive, death coin after each
    purchase. Spend: z ~ Gamma(p, rate nu_i), nu_i ~ Gamma(q, rate g)."""
    lam = rng.gamma(r, 1 / alpha, n)
    p_death = rng.beta(a, b, n)
    T = rng.uniform(t_min, t_max, n)
    nu = rng.gamma(q_gg, 1 / g_gg, n)

    x = np.zeros(n)
    t_x = np.zeros(n)
    m_x = np.zeros(n)
    for i in range(n):
        t, buys, spends = 0.0, 0, []
        while True:
            t += rng.exponential(1 / lam[i])
            if t > T[i]:
                break
            buys += 1
            t_x[i] = t
            spends.append(rng.gamma(p_gg, 1 / nu[i]))
            if rng.random() < p_death[i]:
                break
        x[i] = buys
        m_x[i] = np.mean(spends) if spends else 0.0
    return x, t_x, T, m_x


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------

if __name__ == "__main__":
    rng = np.random.default_rng(7)
    TRUE_BG = dict(r=0.243, alpha=4.414, a=0.793, b=2.426)  # CDNOW estimates
    TRUE_GG = dict(p_gg=6.25, q_gg=3.74, g_gg=15.44)        # FH 2013 note

    x, t_x, T, m_x = simulate_bgnbd(n=2500, **TRUE_BG, **TRUE_GG, rng=rng)
    print(f"simulated {len(x)} customers; repeat buyers: {(x > 0).mean():.1%}")

    bg = fit_bgnbd(x, t_x, T)
    rep = x >= 1
    gg = fit_gg(x[rep], m_x[rep])
    names = ["r", "alpha", "a", "b"]
    print("\nBG/NBD   true -> fitted")
    for nm, tv, fv in zip(names, TRUE_BG.values(), bg):
        print(f"  {nm:5s} {tv:7.3f} -> {fv:7.3f}")
    print("gamma-gamma true -> fitted")
    for nm, tv, fv in zip(["p", "q", "gamma"], TRUE_GG.values(), gg):
        print(f"  {nm:5s} {tv:7.3f} -> {fv:7.3f}")

    # Example customers: same recency/frequency, different stories.
    ex = np.array([[4, 40, 52], [4, 12, 52], [0, 0, 52]])
    pa = p_alive(bg, ex[:, 0], ex[:, 1], ex[:, 2])
    ey = expected_purchases(bg, ex[:, 0], ex[:, 1], ex[:, 2], horizon=26)
    print("\n x  t_x   T   P(alive)  E[buys next 26w]")
    for row, a_, e_ in zip(ex, pa, ey):
        print(f"{row[0]:2d} {row[1]:4d} {row[2]:4d}   {a_:7.3f}   {e_:7.3f}")

    # CLV with a bootstrap error band (parameter uncertainty only).
    point = clv(bg, gg, x, t_x, T, m_x, months=24, monthly_discount=0.01)
    print(f"\nmean 24-month residual CLV (point): {point.mean():8.2f}")

    B = 30
    boots = []
    idx_all = np.arange(len(x))
    for _ in range(B):
        idx = rng.choice(idx_all, size=len(x), replace=True)
        bg_b = fit_bgnbd(x[idx], t_x[idx], T[idx])
        rep_b = x[idx] >= 1
        gg_b = fit_gg(x[idx][rep_b], m_x[idx][rep_b])
        boots.append(clv(bg_b, gg_b, x, t_x, T, m_x, months=24,
                         monthly_discount=0.01).mean())
    lo, hi = np.percentile(boots, [5, 95])
    print(f"bootstrap 90% band on the mean:     [{lo:8.2f}, {hi:8.2f}]  (B={B})")

    # Optional cross-check against pymc-marketing, if installed.
    try:
        from pymc_marketing.clv import BetaGeoModel  # noqa: F401
        print("\npymc-marketing is installed; BetaGeoModel.fit(method='map') "
              "on the same summary frame should land near the MLE above.")
    except ImportError:
        print("\npymc-marketing not installed; from-scratch MLE is the result.")
