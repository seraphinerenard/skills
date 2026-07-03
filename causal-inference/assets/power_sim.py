# pip install numpy   (synthetic_control.py from this directory must sit alongside)
"""Simulation-based power analysis for geo experiments on the client's own
history (the GeoLift pattern).

The only honest power number for a geo test comes from replaying the analysis
on the client's historical panel: inject a synthetic lift into candidate
treatment geos over a pseudo-test window, run the exact analysis you will run
after launch, and count detections. Formula-based power calculators assume
independent units and understate the difficulty when geos share national
shocks.

Test statistic: mean post-period gap between the (aggregated) treated series
and its synthetic control, scaled by pre-period RMSPE. Inference is
randomization-based: the same statistic is computed for random placebo
assignments of the same size on unlifted data, and the one-sided p-value is
the rank of the treated statistic. At lift = 0 the detection rate equals
alpha by construction, which the demo verifies.

Run the demo: python3 power_sim.py   (about 1-2 min)
"""
from __future__ import annotations

import numpy as np

from synthetic_control import fit_weights, rmspe


def _analyze_once(panel: np.ndarray, treated: np.ndarray, t_start: int,
                  lift: float, n_placebo: int, rng: np.random.Generator,
                  ridge: float = 1e-4) -> float:
    """One replay: inject `lift` into `treated` geos from t_start on, return
    the one-sided randomization p-value."""
    T, N = panel.shape
    data = panel.copy()
    data[t_start:, treated] *= (1.0 + lift)
    all_idx = np.arange(N)
    donors = np.setdiff1d(all_idx, treated)

    def stat(cols: np.ndarray, source: np.ndarray) -> float:
        y = source[:, cols].mean(axis=1)
        pool = np.setdiff1d(all_idx, cols)
        # a looser fit tolerance is fine inside the power loop: detection
        # counts change well below the placebo-rank resolution of 1/50
        w = fit_weights(source[:t_start, pool], y[:t_start], ridge=ridge,
                        n_iter=500, tol=1e-8)
        gap_pre = y[:t_start] - source[:t_start, pool] @ w
        gap_post = y[t_start:] - source[t_start:, pool] @ w
        return float(np.mean(gap_post) / max(rmspe(gap_pre), 1e-12))

    s_treated = stat(treated, data)
    s_placebo = np.empty(n_placebo)
    for r in range(n_placebo):
        cols = rng.choice(donors, size=len(treated), replace=False)
        s_placebo[r] = stat(cols, panel)  # placebo geos carry no lift
    return (1.0 + float(np.sum(s_placebo >= s_treated))) / (n_placebo + 1.0)


def power_curve(panel: np.ndarray, treat_count: int, test_len: int,
                lifts: list[float], n_sims: int = 50, n_placebo: int = 49,
                alpha: float = 0.05, seed: int = 0) -> dict:
    """Detection rate per lift level. panel is (T, N) historical data with no
    experiment in it; the last test_len periods act as the pseudo-test window."""
    rng = np.random.default_rng(seed)
    T, N = panel.shape
    t_start = T - test_len
    out = {}
    for lift in lifts:
        hits = 0
        for _ in range(n_sims):
            treated = rng.choice(N, size=treat_count, replace=False)
            p = _analyze_once(panel, treated, t_start, lift, n_placebo, rng)
            hits += p <= alpha
        out[lift] = hits / n_sims
    return out


def mde_at(power: dict, target: float = 0.80) -> float:
    """Linear interpolation of the lift that reaches the target power."""
    pts = sorted(power.items())
    for (l0, p0), (l1, p1) in zip(pts, pts[1:]):
        if p0 < target <= p1:
            return l0 + (l1 - l0) * (target - p0) / (p1 - p0)
    return float("nan")


def _make_history(seed: int = 5, N: int = 25, T: int = 92) -> np.ndarray:
    """Synthetic stand-in for client history: shared national factor with
    geo-specific loadings, weekly seasonality, geo noise."""
    rng = np.random.default_rng(seed)
    national = 10.0 + 2.0 * np.sin(np.arange(T) * 2 * np.pi / 52.0) \
        + np.cumsum(rng.normal(0, 0.15, T))
    load = rng.uniform(0.6, 1.4, N)
    base = rng.uniform(50.0, 120.0, N)
    return base[None, :] + np.outer(national, load) + rng.normal(0, 1.2, (T, N))


def _demo() -> None:
    panel = _make_history()
    T, N = panel.shape
    test_len, k = 4, 5
    lifts = [0.0, 0.01, 0.02, 0.03, 0.05]
    print("Power simulation: %d geos x %d weeks of history, %d treated geos,"
          " %d-week test, alpha=0.05 one-sided" % (N, T, k, test_len))
    pw = power_curve(panel, treat_count=k, test_len=test_len, lifts=lifts,
                     n_sims=50, n_placebo=49, seed=1)
    print()
    print("  lift    power")
    for l, p in sorted(pw.items()):
        print("  %4.1f%%   %5.2f" % (100 * l, p))
    mde = mde_at(pw)
    print()
    print("MDE at 80%% power: %.1f%% lift" % (100 * mde))
    assert pw[0.0] <= 0.15, "false-positive rate should sit near alpha"
    assert pw[0.05] >= 0.8, "a 5% lift should be detectable in this design"
    print("smoke test passed: false-positive rate %.2f at zero lift,"
          " power %.2f at 5%% lift" % (pw[0.0], pw[0.05]))


if __name__ == "__main__":
    _demo()
