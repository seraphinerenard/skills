#!/usr/bin/env python3
# pip install: numpy scipy
"""B2B quote pricing: win-rate curve, expected-margin optimum, guardrail bands.

Setting: an industrial supplier (aggregates, chemicals, distribution) quotes
each deal against a reference price r (the market level for that product,
region, and volume). Win probability falls with the premium charged over
reference. The pricing engine maximizes expected margin per quote:

    E[margin](p) = w(p) * (p - c),   w(p) = sigmoid(a - b * prem(p)),
    prem(p) = 100 * (p / r - 1)      (premium in percentage points)

First-order condition (derived in references/optimization-formulations.md):

    p* - c = r / (100 * b * (1 - w(p*)))

so the optimal dollar markup rises as the win curve flattens (small b) and
as the deal becomes harder to win anyway (w small -> markup shrinks? no:
1 - w small when w large -> markup grows when you are winning easily).

The demo does three things with known ground truth:
  1. Fits the win-rate logistic by MLE on clean synthetic quotes and shows
     parameter recovery with standard errors.
  2. Reproduces the classic endogeneity trap: salespeople cut price on deals
     they can see are competitive, which flips the naive price coefficient
     toward zero or positive ('price does not matter' fallacy). Adding the
     competitiveness proxy restores the true coefficient.
  3. Solves the FOC for a live deal, verifies it against a grid search, and
     prints the 95%-of-optimum guardrail band (floor / target / stretch)
     that a sales team can actually use.
"""

import numpy as np
from scipy import optimize


def sigmoid(u):
    return 1.0 / (1.0 + np.exp(-u))


def nll(theta, X, won):
    """Negative log-likelihood of logistic win model, X includes intercept."""
    u = X @ theta
    # log(sigmoid(u)) and log(1 - sigmoid(u)) via logaddexp for stability
    return np.sum(np.logaddexp(0.0, -u) * won + np.logaddexp(0.0, u) * (1 - won))


def fit_logistic(X, won):
    """MLE fit; returns (theta_hat, standard errors from inverse Hessian)."""
    theta0 = np.zeros(X.shape[1])
    res = optimize.minimize(nll, theta0, args=(X, won), method="BFGS")
    p = sigmoid(X @ res.x)
    W = p * (1 - p)
    H = X.T @ (X * W[:, None])          # observed information
    se = np.sqrt(np.diag(np.linalg.inv(H)))
    return res.x, se


def optimal_price(r, c, a, b, lo_prem=-15.0, hi_prem=40.0):
    """Solve the FOC  (p - c) * w'(p) + w(p) = 0  by bracketed root find.

    w(p) = sigmoid(a - b * prem),  dw/dp = -w(1-w) * b * 100 / r.
    FOC rearranged:  g(p) = w - (p - c) * w * (1 - w) * b * 100 / r = 0.
    """
    def g(p):
        prem = 100.0 * (p / r - 1.0)
        w = sigmoid(a - b * prem)
        return w - (p - c) * w * (1 - w) * b * 100.0 / r

    lo = r * (1 + lo_prem / 100.0)
    hi = r * (1 + hi_prem / 100.0)
    # g > 0 below the optimum (raising price still gains), g < 0 above.
    return optimize.brentq(g, max(lo, c + 1e-6), hi)


def exp_margin(p, r, c, a, b):
    prem = 100.0 * (p / r - 1.0)
    return sigmoid(a - b * prem) * (p - c)


def guardrail_band(r, c, a, b, frac=0.95):
    """Floor and stretch prices where E[margin] = frac * max. The band is
    what sales gets; the point optimum stays inside the engine."""
    p_star = optimal_price(r, c, a, b)
    m_star = exp_margin(p_star, r, c, a, b)

    def hit(p):
        return exp_margin(p, r, c, a, b) - frac * m_star

    p_floor = optimize.brentq(hit, c + 1e-6, p_star)
    p_stretch = optimize.brentq(hit, p_star, r * 2.0)
    return p_floor, p_star, p_stretch, m_star


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    n = 4000

    # Ground truth: u = a0 + a1*tierA - (b0 + b1*large) * prem
    a0, a1 = 0.40, 0.60          # tier-A relationships win more at par
    b0, b1 = 0.12, 0.05          # premium sensitivity; large deals shop harder
    tierA = rng.binomial(1, 0.35, n)
    large = rng.binomial(1, 0.30, n)

    # --- 1. Clean world: historical premiums vary for exogenous reasons ----
    prem = rng.normal(2.0, 6.0, n)
    u = a0 + a1 * tierA - (b0 + b1 * large) * prem
    won = rng.binomial(1, sigmoid(u))
    X = np.column_stack([np.ones(n), tierA, prem, prem * large])
    th, se = fit_logistic(X, won)
    print("1. Recovery on clean quote history (truth in brackets)")
    for name, t, s, tr in zip(["intercept", "tierA", "prem", "prem*large"],
                              th, se, [a0, a1, -b0, -b1]):
        print(f"   {name:11s} {t:+.3f} (se {s:.3f})   [{tr:+.3f}]")

    # --- 2. Endogeneity trap: price cut when the rep smells competition ----
    z = rng.normal(0, 1, n)                    # unobserved competitiveness
    prem_e = rng.normal(2.0, 3.0, n) - 4.0 * z # reps discount hot deals
    u_e = a0 + a1 * tierA - b0 * prem_e - 1.1 * z
    won_e = rng.binomial(1, sigmoid(u_e))
    Xn = np.column_stack([np.ones(n), tierA, prem_e])
    th_n, se_n = fit_logistic(Xn, won_e)
    # A visible proxy for z: count of rival bidders recorded on the deal.
    bidders = np.round(2 + 2.0 * z + rng.normal(0, 0.25, n))
    Xc = np.column_stack([np.ones(n), tierA, prem_e, bidders])
    th_c, se_c = fit_logistic(Xc, won_e)
    print("\n2. Endogenous quote history (true premium coef -0.120)")
    print(f"   naive fit:          prem {th_n[2]:+.3f} (se {se_n[2]:.3f})"
          "   <- sign flipped by rep behaviour")
    print(f"   + bidder-count fit: prem {th_c[2]:+.3f} (se {se_c[2]:.3f})"
          "   <- sign and most of the scale back")
    print("   residual gap vs -0.120 is proxy noise: proxy controls "
          "under-correct, so validate b with a randomized price test")

    # --- 3. Price one live deal and hand sales a band ---------------------
    r, c = 100.0, 78.0            # reference $100/unit, marginal cost $78
    a_deal = a0 + a1              # tier-A customer, normal size
    b_deal = b0
    p_floor, p_star, p_stretch, m_star = guardrail_band(r, c, a_deal, b_deal)
    w_star = sigmoid(a_deal - b_deal * 100 * (p_star / r - 1))
    grid = np.linspace(c + 0.5, 1.4 * r, 20001)
    p_grid = grid[np.argmax(exp_margin(grid, r, c, a_deal, b_deal))]
    print("\n3. Live deal: r=$100.00, c=$78.00, tier A")
    print(f"   FOC optimum p* = ${p_star:.2f}  (grid check ${p_grid:.2f})")
    print(f"   win prob at p* = {w_star:.3f}, expected margin ${m_star:.2f}")
    print(f"   markup check: p*-c = ${p_star - c:.2f} vs "
          f"r/(100 b (1-w*)) = ${r / (100 * b_deal * (1 - w_star)):.2f}")
    print(f"   guardrail band (95% of optimum): floor ${p_floor:.2f} | "
          f"target ${p_star:.2f} | stretch ${p_stretch:.2f}")
    print(f"   band width = {100 * (p_stretch - p_floor) / p_star:.1f}% "
          "of target: the profit curve is flat near the top, which is why "
          "bands beat point prices for adoption")
