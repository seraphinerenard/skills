# pip install numpy
"""CUPED variance reduction for randomized experiments.

Implements the covariate adjustment of Deng, Xu, Kohavi, Walker (WSDM 2013):
    theta   = cov(y, x) / var(x)
    y_cuped = y - theta * (x - mean(x))
where x is a pre-experiment covariate (best: the same metric measured on the
same unit before assignment). Because assignment is independent of x, the
adjustment leaves the treatment-effect estimand unchanged and cuts the
variance of the difference-in-means by a factor of (1 - rho^2), where rho is
the correlation between x and y.

theta is estimated on the pooled sample (both arms). With randomized
assignment this is unbiased; estimating theta per-arm reintroduces bias.

Run the demo: python3 cuped.py
"""
from __future__ import annotations

import numpy as np


def cuped_theta(y: np.ndarray, x: np.ndarray) -> float:
    """OLS slope of y on x, pooled across arms."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    vx = x.var(ddof=1)
    if vx == 0.0:
        return 0.0
    return float(np.cov(y, x, ddof=1)[0, 1] / vx)


def cuped_adjust(y: np.ndarray, x: np.ndarray, theta: float | None = None) -> np.ndarray:
    """Return the CUPED-adjusted outcome. Uses the pooled mean of x, so the
    mean of y is preserved and lift estimates stay on the original scale."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if theta is None:
        theta = cuped_theta(y, x)
    return y - theta * (x - x.mean())


def diff_in_means(y: np.ndarray, treat: np.ndarray) -> dict:
    """Two-sample difference in means with Welch standard error."""
    y = np.asarray(y, dtype=float)
    treat = np.asarray(treat, dtype=bool)
    y1, y0 = y[treat], y[~treat]
    est = y1.mean() - y0.mean()
    se = float(np.sqrt(y1.var(ddof=1) / len(y1) + y0.var(ddof=1) / len(y0)))
    z = est / se if se > 0 else 0.0
    # two-sided normal p-value; sample sizes here make t vs normal immaterial
    from math import erf, sqrt
    p = 2.0 * (1.0 - 0.5 * (1.0 + erf(abs(z) / sqrt(2.0))))
    return {"estimate": float(est), "se": se, "z": float(z), "p": p,
            "ci95": (float(est - 1.96 * se), float(est + 1.96 * se))}


def analyze(y: np.ndarray, treat: np.ndarray, x: np.ndarray | None = None) -> dict:
    """Difference in means, raw and (if x is given) CUPED-adjusted.

    Returns both results plus the realized variance-reduction factor
    var(y_cuped)/var(y), which converges to 1 - corr(x, y)^2.
    """
    out = {"raw": diff_in_means(y, treat)}
    if x is not None:
        y_adj = cuped_adjust(y, x)
        out["cuped"] = diff_in_means(y_adj, treat)
        out["variance_ratio"] = float(np.var(y_adj, ddof=1) / np.var(y, ddof=1))
        out["rho"] = float(np.corrcoef(y, x)[0, 1])
    return out


def _demo() -> None:
    rng = np.random.default_rng(7)
    n = 20_000
    true_lift = 0.50  # dollars per user per week, on a base near 25

    # User-level persistent spend propensity drives both the pre-period
    # covariate and the experiment outcome, giving corr(x, y) near 0.7.
    propensity = rng.normal(25.0, 6.0, size=n)
    x = propensity + rng.normal(0.0, 3.93, size=n)          # pre-period spend
    treat = rng.random(n) < 0.5
    y = propensity + rng.normal(0.0, 3.93, size=n) + true_lift * treat

    res = analyze(y, treat, x)
    raw, cup = res["raw"], res["cuped"]
    vr = res["variance_ratio"]

    print("CUPED demo: n=%d per test, true lift = %.2f" % (n, true_lift))
    print("corr(pre-period x, outcome y) = %.3f" % res["rho"])
    print()
    print("%-8s %10s %10s %22s %10s" % ("method", "estimate", "se", "95% CI", "p"))
    for name, r in (("raw", raw), ("cuped", cup)):
        print("%-8s %10.3f %10.3f      [%6.3f, %6.3f] %10.2g"
              % (name, r["estimate"], r["se"], r["ci95"][0], r["ci95"][1], r["p"]))
    print()
    print("variance ratio var(y_cuped)/var(y) = %.3f  (theory: 1 - rho^2 = %.3f)"
          % (vr, 1.0 - res["rho"] ** 2))
    print("sample-size equivalent: CUPED with n=%d matches a raw test with n=%d"
          % (n, int(round(n / vr))))
    assert abs(cup["estimate"] - true_lift) < 3 * cup["se"], "estimate off truth"
    assert vr < 0.65, "expected at least a 35% variance cut at rho ~ 0.7"
    print("smoke test passed: CUPED CI covers truth and variance fell by %.0f%%"
          % (100 * (1 - vr)))


if __name__ == "__main__":
    _demo()
