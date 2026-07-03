"""Ornstein-Uhlenbeck calibration and half-life for mean-reverting price series.

pip install numpy
Tested with numpy 2.5, Python 3.12+.

Model: dX = kappa * (theta - X) dt + sigma dW, usually on log price or on a
basis/spread. Sampled at interval dt the process is an exact AR(1):

    X[t+1] = c + b * X[t] + e,   e ~ N(0, s2)
    b  = exp(-kappa * dt)
    c  = theta * (1 - b)
    s2 = sigma^2 * (1 - b^2) / (2 * kappa)

Inverting the OLS estimates:

    kappa     = -ln(b) / dt
    theta     = c / (1 - b)
    sigma^2   = s2 * 2 * kappa / (1 - b^2)
    half-life = ln(2) / kappa        (same time units as dt)

Small-sample bias: OLS underestimates b by roughly (1 + 3b) / n (Kendall 1954),
so kappa is overestimated and the half-life comes out too short. With n = 250
daily observations and a true b = 0.977 (30-day half-life) the bias term is
(1 + 3 * 0.977) / 250 = 0.0157, which drags the fitted half-life toward
ln(2) / -ln(0.961) = 17 days. fit_ou reports both the raw and the
Kendall-corrected estimate; the demo measures the bias by Monte Carlo.
"""

from __future__ import annotations

import numpy as np


def simulate_ou(kappa: float, theta: float, sigma: float, x0: float,
                dt: float, n: int, rng: np.random.Generator) -> np.ndarray:
    """Simulate n+1 points of an OU path with the exact discretization."""
    b = np.exp(-kappa * dt)
    sd = sigma * np.sqrt((1.0 - b * b) / (2.0 * kappa))
    x = np.empty(n + 1)
    x[0] = x0
    shocks = rng.normal(0.0, sd, size=n)
    for t in range(n):
        x[t + 1] = theta + (x[t] - theta) * b + shocks[t]
    return x


def fit_ou(x: np.ndarray, dt: float) -> dict:
    """Calibrate OU parameters from a sampled path via AR(1) OLS.

    Returns raw and Kendall-corrected estimates. Raises if the fitted AR(1)
    coefficient is >= 1 (no mean reversion in sample: the half-life is
    undefined and an OU model is the wrong tool for this series).
    """
    x = np.asarray(x, dtype=float)
    y, xl = x[1:], x[:-1]
    n = len(y)
    A = np.column_stack([np.ones(n), xl])
    (c, b), res_ss = np.linalg.lstsq(A, y, rcond=None)[:2]
    if b >= 1.0:
        raise ValueError(f"AR(1) coefficient {b:.4f} >= 1: series is not "
                         "mean-reverting in this sample")
    resid = y - c - b * xl
    s2 = resid @ resid / (n - 2)
    se_b = np.sqrt(s2 / np.sum((xl - xl.mean()) ** 2))

    def invert(bb: float) -> dict:
        kappa = -np.log(bb) / dt
        return {
            "b": bb,
            "kappa": kappa,
            "theta": c / (1.0 - bb),
            "sigma": np.sqrt(s2 * 2.0 * kappa / (1.0 - bb * bb)),
            "half_life": np.log(2.0) / kappa,
        }

    out = invert(b)
    out["se_b"] = se_b
    b_corr = min(b + (1.0 + 3.0 * b) / n, 0.999999)  # Kendall (1954)
    out["corrected"] = invert(b_corr)
    return out


def half_life_ci(x: np.ndarray, dt: float, n_boot: int = 500,
                 rng: np.random.Generator | None = None,
                 level: float = 0.90) -> tuple[float, float]:
    """Parametric-bootstrap percentile interval for the half-life.

    Simulates from the fitted parameters, refits each path, and returns the
    percentile interval. Paths that fail to mean-revert (b >= 1) count as an
    infinite half-life, so the upper bound is honest about weak evidence.
    """
    rng = rng or np.random.default_rng(0)
    fit = fit_ou(x, dt)
    hl = np.full(n_boot, np.inf)
    for i in range(n_boot):
        path = simulate_ou(fit["kappa"], fit["theta"], fit["sigma"],
                           x[0], dt, len(x) - 1, rng)
        try:
            hl[i] = fit_ou(path, dt)["half_life"]
        except ValueError:
            pass
    lo, hi = np.quantile(hl, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(lo), float(hi)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    # True process: 30-day half-life on a log-price series around log(500).
    true_hl = 30.0
    kappa = np.log(2.0) / true_hl          # 0.02310 per day
    theta, sigma, dt = np.log(500.0), 0.015, 1.0

    print("=== Single-path calibration, n = 504 daily obs (~2 years) ===")
    x = simulate_ou(kappa, theta, sigma, theta, dt, 504, rng)
    fit = fit_ou(x, dt)
    print(f"true:   b = {np.exp(-kappa * dt):.4f}  kappa = {kappa:.5f}"
          f"  half-life = {true_hl:.1f} d  sigma = {sigma:.4f}")
    print(f"fitted: b = {fit['b']:.4f}  kappa = {fit['kappa']:.5f}"
          f"  half-life = {fit['half_life']:.1f} d  sigma = {fit['sigma']:.4f}")
    c = fit["corrected"]
    print(f"Kendall-corrected: b = {c['b']:.4f}  half-life = {c['half_life']:.1f} d")
    lo, hi = half_life_ci(x, dt, n_boot=300, rng=rng)
    print(f"90% bootstrap CI for half-life: [{lo:.1f}, {hi:.1f}] days")

    print("\n=== Bias check: 400 Monte Carlo paths per sample size ===")
    print(f"{'n':>6} {'median HL (raw)':>16} {'median HL (corr)':>17}")
    for n in (125, 250, 504, 2016):
        raw, corr = [], []
        for _ in range(400):
            p = simulate_ou(kappa, theta, sigma, theta, dt, n, rng)
            try:
                f = fit_ou(p, dt)
                raw.append(f["half_life"])
                corr.append(f["corrected"]["half_life"])
            except ValueError:
                raw.append(np.inf)
                corr.append(np.inf)
        print(f"{n:>6} {np.median(raw):>14.1f} d {np.median(corr):>15.1f} d")
    print(f"true half-life: {true_hl:.1f} d. The raw estimate shortens as the "
          "sample shrinks; the correction removes most of the gap.")
