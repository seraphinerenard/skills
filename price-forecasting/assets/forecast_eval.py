"""Forecast evaluation: pinball loss, CRPS, Diebold-Mariano, directional traps.

pip install numpy scipy
Tested with numpy 2.5, scipy 1.16.

Contents:
  pinball(y, q, tau)            quantile (pinball) loss, the score for one decile
  crps_ensemble(y, ens)         CRPS from ensemble members, fair (unbiased) form
  dm_test(e1, e2, h, loss)      Diebold-Mariano with the Harvey-Leybourne-
                                Newbold small-sample correction; e1, e2 are
                                forecast ERRORS from two competing forecasts
                                of the same target
  pt_test(actual, forecast)     Pesaran-Timmermann directional-ability test

The DM statistic tests the null that two forecasts have equal expected loss.
It requires the loss differential series d_t = L(e1_t) - L(e2_t), a
long-run-variance estimate (Newey-West with h-1 lags for h-step forecasts),
and, at multi-step horizons on short samples, the HLN correction

    HLN factor = sqrt((n + 1 - 2h + h(h-1)/n) / n)

with the t(n-1) reference distribution in place of the normal. Skipping the
correction overstates significance at h > 1.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def pinball(y: np.ndarray, q: np.ndarray, tau: float) -> float:
    """Mean pinball loss of quantile forecasts q at level tau against y."""
    y, q = np.asarray(y, float), np.asarray(q, float)
    diff = y - q
    return float(np.mean(np.where(diff >= 0, tau * diff, (tau - 1.0) * diff)))


def crps_ensemble(y: np.ndarray, ens: np.ndarray, fair: bool = True) -> float:
    """Mean CRPS of an ensemble forecast.

    y: (n_obs,) outcomes. ens: (n_obs, m) ensemble members per observation.
    CRPS = E|X - y| - 0.5 E|X - X'|. The fair form divides the spread term by
    m(m-1) and is unbiased for the underlying distribution's CRPS; the
    classic form divides by m^2 and rewards under-dispersed ensembles.
    """
    y = np.asarray(y, float).reshape(-1, 1)
    ens = np.asarray(ens, float)
    n, m = ens.shape
    term1 = np.mean(np.abs(ens - y), axis=1)
    es = np.sort(ens, axis=1)
    # sum_{i<j} (x_j - x_i) computed via sorted weights, O(m log m) per row
    w = 2.0 * np.arange(1, m + 1) - m - 1.0
    pair_sum = (es * w).sum(axis=1)
    denom = m * (m - 1) if fair else m * m
    return float(np.mean(term1 - pair_sum / denom))


def dm_test(e1: np.ndarray, e2: np.ndarray, h: int = 1,
            loss: str = "squared") -> dict:
    """Diebold-Mariano test with the HLN small-sample correction.

    e1, e2: forecast errors (actual minus forecast) from the two forecasts.
    h: forecast horizon in steps (sets the Newey-West lag h-1).
    loss: 'squared' or 'absolute'.
    Negative statistic means forecast 1 has the lower loss.
    """
    e1, e2 = np.asarray(e1, float), np.asarray(e2, float)
    if loss == "squared":
        d = e1 ** 2 - e2 ** 2
    elif loss == "absolute":
        d = np.abs(e1) - np.abs(e2)
    else:
        raise ValueError("loss must be 'squared' or 'absolute'")
    n = len(d)
    dbar = d.mean()
    dc = d - dbar
    gamma0 = dc @ dc / n
    lrv = gamma0
    for k in range(1, h):
        gk = dc[k:] @ dc[:-k] / n
        lrv += 2.0 * gk                       # rectangular kernel, h-1 lags
    if lrv <= 0:
        lrv = gamma0                          # NW variance can go negative
    dm = dbar / np.sqrt(lrv / n)
    hln = np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    stat = dm * hln
    p = 2.0 * stats.t.sf(abs(stat), df=n - 1)
    return {"dm": float(dm), "stat_hln": float(stat), "p_value": float(p),
            "mean_loss_1": float(np.mean(e1**2 if loss == "squared" else np.abs(e1))),
            "mean_loss_2": float(np.mean(e2**2 if loss == "squared" else np.abs(e2))),
            "n": n}


def pt_test(actual_change: np.ndarray, forecast_change: np.ndarray) -> dict:
    """Pesaran-Timmermann test of directional forecasting ability.

    Tests whether the hit rate exceeds what the two sign frequencies produce
    under independence. A forecast that always says "up" on an upward-drifting
    series posts a high hit rate and a PT statistic near zero.
    """
    a = (np.asarray(actual_change) > 0).astype(float)
    f = (np.asarray(forecast_change) > 0).astype(float)
    n = len(a)
    phat = float(np.mean(a == f))
    pa, pf = a.mean(), f.mean()
    pstar = pa * pf + (1 - pa) * (1 - pf)
    v_phat = pstar * (1 - pstar) / n
    v_pstar = ((2 * pf - 1) ** 2 * pa * (1 - pa) / n
               + (2 * pa - 1) ** 2 * pf * (1 - pf) / n
               + 4 * pa * pf * (1 - pa) * (1 - pf) / n ** 2)
    denom = v_phat - v_pstar
    if denom <= 0:
        return {"hit_rate": phat, "expected_by_chance": pstar,
                "stat": 0.0, "p_value": 1.0}
    stat = (phat - pstar) / np.sqrt(denom)
    return {"hit_rate": phat, "expected_by_chance": float(pstar),
            "stat": float(stat), "p_value": float(stats.norm.sf(stat))}


if __name__ == "__main__":
    rng = np.random.default_rng(21)

    print("=== Pinball, worked ===")
    # One observation: P90 forecast 620, outcome 585. Loss = (1-0.9)*(620-585)=3.5
    print(f"P90=620, outcome 585 -> pinball {pinball([585.], [620.], 0.9):.2f} "
          "(under the quantile costs tau*miss, over costs (1-tau)*miss)")

    print("\n=== CRPS: sharp-and-right vs wide vs sharp-and-wrong ===")
    n, m = 400, 200
    y = rng.normal(100.0, 5.0, n)
    good = rng.normal(y[:, None], 5.0, (n, m))       # correct dispersion
    wide = rng.normal(y[:, None], 15.0, (n, m))      # over-dispersed
    biased = rng.normal(y[:, None] + 6.0, 5.0, (n, m))
    for name, ens in [("calibrated", good), ("over-dispersed", wide),
                      ("biased +6", biased)]:
        print(f"  {name:>14}: CRPS {crps_ensemble(y, ens):.3f}")

    print("\n=== Diebold-Mariano, worked ===")
    # Target: AR(1) with persistence 0.95. Forecast A knows the model,
    # forecast B is a random walk (predicts no change).
    T = 220
    x = np.empty(T)
    x[0] = 0.0
    for t in range(1, T):
        x[t] = 0.95 * x[t - 1] + rng.normal(0, 1)
    h = 5
    idx = np.arange(T - h)
    fa = 0.95 ** h * x[idx]                          # model-based h-step
    fb = x[idx]                                      # random walk
    actual = x[idx + h]
    r = dm_test(actual - fa, actual - fb, h=h)
    print(f"  n={r['n']}, h={h}: MSE(model)={r['mean_loss_1']:.2f} "
          f"MSE(rw)={r['mean_loss_2']:.2f}")
    print(f"  DM={r['dm']:.2f}, HLN-corrected={r['stat_hln']:.2f}, "
          f"p={r['p_value']:.4f} (negative favours the model)")

    print("\n=== Directional-accuracy trap ===")
    steps = rng.normal(0.4, 1.0, 300)                # drifting series
    always_up = np.ones(300)
    r = pt_test(steps, always_up)
    print(f"  'always up' on a drifting series: hit rate {r['hit_rate']:.1%}, "
          f"chance level {r['expected_by_chance']:.1%}, "
          f"PT stat {r['stat']:.2f} (p={r['p_value']:.2f}) -> no skill")
