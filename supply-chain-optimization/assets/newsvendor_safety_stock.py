#!/usr/bin/env python3
"""Newsvendor from forecast quantiles, and safety stock from empirical
lead-time forecast-error quantiles.

pip install numpy

Two demos on synthetic data:

Demo A (newsvendor): the order quantity is the critical fractile of the
demand distribution, read straight off the forecast quantiles that a
demand-forecasting model produces (see the demand-forecasting skill). The
demo compares reading the fractile from the true (skewed) quantiles against
the common shortcut of fitting a normal to mean and sd, and prices the
difference by Monte Carlo.

Demo B (safety stock): the textbook formula z * sigma_1 * sqrt(H) assumes
one-step forecast errors are independent across the protection interval H.
Autocorrelated demand breaks that assumption: errors compound, the true
lead-time-total error spread is wider than sqrt(H) scaling, and the achieved
service level lands well under target. The fix used here needs no
distributional model: take the empirical quantile of realized H-period-total
forecast error from history and use that as the safety stock.
"""

import numpy as np


def critical_fractile(underage_cost: float, overage_cost: float) -> float:
    """Optimal service fractile q* = cu / (cu + co)."""
    return underage_cost / (underage_cost + overage_cost)


def order_from_quantiles(quantiles: dict, fractile: float) -> float:
    """Linear interpolation through a forecast's quantile grid."""
    qs = sorted(quantiles)
    if fractile <= qs[0]:
        return quantiles[qs[0]]
    if fractile >= qs[-1]:
        return quantiles[qs[-1]]
    return float(np.interp(fractile, qs, [quantiles[q] for q in qs]))


def expected_profit(order_q, demand_draws, price, cost, salvage):
    sold = np.minimum(order_q, demand_draws)
    left = order_q - sold
    return float(np.mean(price * sold + salvage * left - cost * order_q))


def demo_newsvendor(seed=11):
    rng = np.random.default_rng(seed)
    price, cost, salvage = 10.0, 6.0, 5.0          # cu = 4, co = 1
    frac = critical_fractile(price - cost, cost - salvage)

    # true demand: lognormal, median 90, high-variance slow mover (CV ~ 0.95)
    mu_ln, sigma_ln = np.log(90.0), 0.80
    grid = [0.1, 0.25, 0.5, 0.75, 0.8, 0.9, 0.95, 0.99]
    from math import erf, sqrt

    def z_of(p):  # probit via bisection on the normal CDF, avoids scipy
        lo, hi = -6.0, 6.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if 0.5 * (1 + erf(mid / sqrt(2))) < p:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    fq = {p: float(np.exp(mu_ln + sigma_ln * z_of(p))) for p in grid}

    q_quantile = order_from_quantiles(fq, frac)
    mean = np.exp(mu_ln + sigma_ln ** 2 / 2)
    sd = mean * np.sqrt(np.exp(sigma_ln ** 2) - 1)
    q_normal = mean + z_of(frac) * sd

    draws = rng.lognormal(mu_ln, sigma_ln, 200_000)
    pi_q = expected_profit(q_quantile, draws, price, cost, salvage)
    pi_n = expected_profit(q_normal, draws, price, cost, salvage)

    print("Demo A: newsvendor from forecast quantiles")
    print(f"  cu=4, co=1 -> critical fractile {frac:.3f}")
    print(f"  order from forecast quantiles : {q_quantile:7.1f}  "
          f"expected profit {pi_q:8.2f}")
    print(f"  order from normal approx      : {q_normal:7.1f}  "
          f"expected profit {pi_n:8.2f}")
    print(f"  cost of the normal shortcut   : {pi_q - pi_n:7.2f} per period "
          f"({100 * (pi_q - pi_n) / pi_q:.2f}% of profit)")


def demo_safety_stock(rho=0.6, mu=100.0, sigma_eps=20.0, lead=4, review=1,
                      target=0.95, n_hist=3_000, n_eval=200_000, seed=23):
    rng = np.random.default_rng(seed)
    H = lead + review  # protection interval for an order-up-to policy

    def ar1(n):
        d = np.empty(n)
        d[0] = mu
        eps = rng.normal(0, sigma_eps, n)
        for t in range(1, n):
            d[t] = mu + rho * (d[t - 1] - mu) + eps[t]
        return d

    hist = ar1(n_hist)
    # planner's forecast is the long-run mean (what most ERP parameterizations
    # reduce to); one-step error sd feeds the textbook formula
    sigma_1 = float(np.std(hist - mu))
    z95 = 1.6449
    ss_textbook = z95 * sigma_1 * np.sqrt(H)

    win = np.lib.stride_tricks.sliding_window_view(hist, H).sum(axis=1)
    err = win - H * mu
    ss_empirical = float(np.quantile(err, target))

    fresh = np.lib.stride_tricks.sliding_window_view(ar1(n_eval), H).sum(axis=1)

    def achieved(ss):
        return float(np.mean(fresh <= H * mu + ss))

    print("Demo B: safety stock under autocorrelated demand "
          f"(AR(1), rho={rho}, lead {lead} + review {review})")
    print(f"  one-step error sd measured    : {sigma_1:7.1f}")
    print(f"  textbook  z*sigma*sqrt(H)     : {ss_textbook:7.1f}  "
          f"-> achieved service {100 * achieved(ss_textbook):5.1f}%  "
          f"(target {100 * target:.0f}%)")
    print(f"  empirical H-period error q95  : {ss_empirical:7.1f}  "
          f"-> achieved service {100 * achieved(ss_empirical):5.1f}%")
    print(f"  stock understatement by the textbook formula: "
          f"{100 * (ss_empirical - ss_textbook) / ss_empirical:.0f}%")


if __name__ == "__main__":
    demo_newsvendor()
    print()
    demo_safety_stock()
