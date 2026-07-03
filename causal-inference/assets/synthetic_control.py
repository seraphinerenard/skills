# pip install numpy
"""Synthetic control for geo experiments: simplex-constrained ridge weights
plus placebo (permutation) inference.

Weights solve
    min_w ||y1_pre - Y0_pre w||^2 + ridge * ||w||^2
    s.t.  w >= 0, sum(w) = 1
via accelerated projected gradient with an exact Euclidean projection onto the
simplex (Duchi, Shalev-Shwartz, Singer, Chandra, ICML 2008). The ridge term
stabilizes weights when donors are collinear; ridge is scaled to the data so
the default works across metrics of different magnitude.

Inference follows Abadie, Diamond, Hainmueller (JASA 2010): re-run the fit
with every donor as a pseudo-treated unit and rank the treated unit's
post/pre RMSPE ratio among the placebos. With J donors the smallest
achievable p-value is 1/(J+1); a geo test with 12 donors can never reach
p < 0.05 by this test. Plan the donor pool before promising significance.

Run the demo: python3 synthetic_control.py
"""
from __future__ import annotations

import numpy as np


def project_simplex(v: np.ndarray) -> np.ndarray:
    """Euclidean projection of v onto {w : w >= 0, sum(w) = 1}."""
    u = np.sort(v)[::-1]
    css = np.cumsum(u)
    idx = np.arange(1, len(v) + 1)
    rho = np.nonzero(u * idx > (css - 1.0))[0][-1]
    tau = (css[rho] - 1.0) / (rho + 1.0)
    return np.maximum(v - tau, 0.0)


def fit_weights(Y0_pre: np.ndarray, y1_pre: np.ndarray, ridge: float = 1e-4,
                n_iter: int = 2000, tol: float = 1e-10) -> np.ndarray:
    """Simplex-constrained ridge weights. Y0_pre is (T_pre, J), y1_pre (T_pre,).

    ridge is relative: the penalty used is ridge * mean(diag(Y0'Y0)).
    """
    Y0 = np.asarray(Y0_pre, dtype=float)
    y1 = np.asarray(y1_pre, dtype=float)
    J = Y0.shape[1]
    G = Y0.T @ Y0
    lam = ridge * float(np.trace(G)) / J
    G = G + lam * np.eye(J)
    b = Y0.T @ y1
    L = float(np.linalg.eigvalsh(G)[-1])
    w = np.full(J, 1.0 / J)
    z, t = w.copy(), 1.0
    for _ in range(n_iter):
        w_new = project_simplex(z - (G @ z - b) / L)
        t_new = (1.0 + np.sqrt(1.0 + 4.0 * t * t)) / 2.0
        z = w_new + ((t - 1.0) / t_new) * (w_new - w)
        if np.max(np.abs(w_new - w)) < tol:
            return w_new
        w, t = w_new, t_new
    return w


def rmspe(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(x, dtype=float) ** 2)))


def sc_gaps(Y_pre: np.ndarray, Y_post: np.ndarray, treated: int,
            donors: np.ndarray, ridge: float = 1e-4):
    """Fit weights on the pre period and return (weights, gap_pre, gap_post)."""
    w = fit_weights(Y_pre[:, donors], Y_pre[:, treated], ridge=ridge)
    gap_pre = Y_pre[:, treated] - Y_pre[:, donors] @ w
    gap_post = Y_post[:, treated] - Y_post[:, donors] @ w
    return w, gap_pre, gap_post


def placebo_test(Y_pre: np.ndarray, Y_post: np.ndarray, treated: int,
                 ridge: float = 1e-4, max_pre_ratio: float | None = None) -> dict:
    """Synthetic-control estimate with placebo inference.

    Y_pre is (T_pre, N), Y_post is (T_post, N); column `treated` is the
    treated geo. Every other column is refit as a pseudo-treated unit against
    the remaining donors (the true treated column is excluded from every
    placebo fit). max_pre_ratio, if set, drops placebos whose pre-period
    RMSPE exceeds that multiple of the treated unit's pre-period RMSPE
    (Abadie et al. use 2x to 5x); dropping poor fits sharpens the reference
    distribution and shrinks the achievable p floor accordingly.
    """
    N = Y_pre.shape[1]
    donors = np.array([j for j in range(N) if j != treated])
    w, gap_pre, gap_post = sc_gaps(Y_pre, Y_post, treated, donors, ridge)
    att = float(np.mean(gap_post))
    pre_r = rmspe(gap_pre)
    ratio = rmspe(gap_post) / max(pre_r, 1e-12)

    placebo_ratios, placebo_pre = [], []
    for j in donors:
        dj = np.array([k for k in donors if k != j])
        _, gpre, gpost = sc_gaps(Y_pre, Y_post, j, dj, ridge)
        placebo_pre.append(rmspe(gpre))
        placebo_ratios.append(rmspe(gpost) / max(rmspe(gpre), 1e-12))
    placebo_ratios = np.array(placebo_ratios)
    placebo_pre = np.array(placebo_pre)

    keep = np.ones(len(donors), dtype=bool)
    if max_pre_ratio is not None:
        keep = placebo_pre <= max_pre_ratio * pre_r
    kept = placebo_ratios[keep]
    p = (1.0 + float(np.sum(kept >= ratio))) / (len(kept) + 1.0)

    return {"weights": w, "donors": donors, "att": att,
            "pre_rmspe": pre_r, "ratio": float(ratio),
            "placebo_ratios": placebo_ratios, "n_placebos_kept": int(len(kept)),
            "p_value": float(p), "gap_post": gap_post}


def _demo() -> None:
    rng = np.random.default_rng(11)
    N, T_pre, T_post = 25, 70, 10
    true_lift = 0.05  # +5% on the treated geo in the post period

    # Two-factor model: geos share national shocks with geo-specific loadings,
    # so a weighted donor combination can reproduce the treated geo.
    loadings = rng.uniform(0.5, 1.5, size=(N, 2))
    factors = np.vstack([
        10.0 + 2.0 * np.sin(np.arange(T_pre + T_post) * 2 * np.pi / 52.0)
        + rng.normal(0, 1.0, T_pre + T_post),
        rng.normal(0, 1.0, T_pre + T_post) + 5.0,
    ])
    base = rng.uniform(40.0, 90.0, size=N)
    Y = base[None, :] + (loadings @ factors).T + rng.normal(0, 1.0, (T_pre + T_post, N))

    treated = 0
    Y_post = Y[T_pre:].copy()
    Y_post[:, treated] *= (1.0 + true_lift)
    Y_pre = Y[:T_pre]

    res = placebo_test(Y_pre, Y_post, treated)
    sc_level = float(np.mean(Y_post[:, treated] - res["gap_post"]))
    lift_pct = res["att"] / sc_level

    order = np.argsort(res["weights"])[::-1][:5]
    print("Synthetic control demo: %d geos, %d pre / %d post weeks, true lift +%.1f%%"
          % (N, T_pre, T_post, 100 * true_lift))
    print("pre-period RMSPE: %.3f (treated level ~%.0f)" % (res["pre_rmspe"], sc_level))
    print("estimated ATT: %+.3f per week  (%+.2f%%; truth %+.2f%%)"
          % (res["att"], 100 * lift_pct, 100 * true_lift))
    print("post/pre RMSPE ratio: %.2f;  placebo p-value: %.3f  (floor 1/%d = %.3f)"
          % (res["ratio"], res["p_value"], N, 1.0 / N))
    print("top-5 donor weights: " +
          ", ".join("geo%02d=%.2f" % (res["donors"][j], res["weights"][j]) for j in order))
    assert abs(lift_pct - true_lift) < 0.02, "lift estimate off by > 2 points"
    assert res["p_value"] <= 0.05, "expected detection at 5% with this design"
    print("smoke test passed: recovered %+.2f%% vs truth %+.2f%%, p=%.3f"
          % (100 * lift_pct, 100 * true_lift, res["p_value"]))


if __name__ == "__main__":
    _demo()
