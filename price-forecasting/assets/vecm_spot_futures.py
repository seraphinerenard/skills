"""Johansen cointegration test and VECM forecast for a spot-futures pair.

pip install numpy pandas statsmodels
Tested with statsmodels 0.14.6, numpy 2.5, pandas 3.0.

Workflow this module encodes:
  1. select_order on the levels chooses the VAR lag p; the VECM uses
     k_ar_diff = p - 1 (lags of the DIFFERENCED series, a common off-by-one).
  2. select_coint_rank runs the Johansen trace test at 5%.
  3. VECM(..., deterministic="ci") puts the constant inside the cointegrating
     relation, the right choice for a spot-futures basis that mean-reverts to
     a non-zero level (carry, risk premium). "co" instead would let the pair
     drift apart deterministically.
  4. Read alpha with care. When the shared stochastic trend's variance
     dwarfs the basis variance (the usual case for storable commodities:
     daily trend moves of 1-2% against basis noise of a few tenths), the
     individual adjustment coefficients are weakly identified and their signs
     wander across samples. The well-identified quantity is the spread
     adjustment rate, alpha_fut - alpha_spot for beta = [1, -1], which sets
     the basis half-life. Price-discovery attributions from daily alphas
     overreach; they need intraday data.

Johansen critical values in statsmodels cover at most 12 series; for wide
systems test pairs or use bootstrap critical values. On statsmodels 0.14.6
with numpy 2.x, coint_johansen emits ComplexWarning (eigenvalues with tiny
imaginary parts cast to real); the demo filters it, the results are fine.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.vector_ar.vecm import (
    VECM, coint_johansen, select_coint_rank, select_order,
)


def simulate_pair(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Cointegrated log spot / log futures with a mean-reverting basis.

    Both legs share one stochastic trend. The basis (futures minus spot)
    reverts to 2% with a 20-day half-life, and spot does 80% of the
    adjusting, matching the price-discovery pattern in storable commodities.
    """
    trend = np.cumsum(rng.normal(0.0, 0.012, size=n)) + np.log(70.0)
    b = np.exp(-np.log(2.0) / 20.0)          # 20-day basis half-life
    basis = np.empty(n)
    basis[0] = 0.02
    for t in range(1, n):
        basis[t] = 0.02 + (basis[t - 1] - 0.02) * b + rng.normal(0.0, 0.004)
    spot = trend - 0.8 * basis
    fut = trend + 0.2 * basis
    idx = pd.bdate_range("2022-01-03", periods=n)
    return pd.DataFrame({"log_spot": spot, "log_fut": fut}, index=idx)


def fit_vecm(data: pd.DataFrame, det: str = "ci", signif: float = 0.05):
    """Lag selection, Johansen rank test, and VECM fit. Returns (res, rank)."""
    p = select_order(data, maxlags=10, deterministic=det).aic
    k_ar_diff = max(p, 1)
    rank_res = select_coint_rank(data, det_order=0, k_ar_diff=k_ar_diff,
                                 method="trace", signif=signif)
    res = VECM(data, k_ar_diff=k_ar_diff, coint_rank=rank_res.rank,
               deterministic=det).fit()
    return res, rank_res


def ec_half_life(res, data: pd.DataFrame) -> float:
    """Half-life of the estimated error-correction term via its AR(1) fit."""
    beta = res.beta[:, 0]
    ect = data.to_numpy() @ beta
    y, xl = ect[1:], ect[:-1]
    xl_c = xl - xl.mean()
    b = (xl_c @ (y - y.mean())) / (xl_c @ xl_c)
    if b >= 1.0:
        return float("inf")
    return float(np.log(2.0) / -np.log(b))


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=np.exceptions.ComplexWarning)
    rng = np.random.default_rng(7)
    data = simulate_pair(750, rng)

    jo = coint_johansen(data, det_order=0, k_ar_diff=1)
    print("Johansen trace stats:", np.round(jo.lr1, 2),
          " 5% critical values:", np.round(jo.cvt[:, 1], 2))

    res, rank_res = fit_vecm(data)
    print(f"selected cointegration rank: {rank_res.rank} (expected 1)")

    beta = res.beta[:, 0] / res.beta[0, 0]   # normalize on log_spot
    print(f"cointegrating vector (normalized): "
          f"[1, {beta[1]:.3f}]  (true: [1, -1])")
    a_spot, a_fut = res.alpha[0, 0], res.alpha[1, 0]
    spread_rate = a_fut - a_spot
    print(f"alpha: spot {a_spot:+.4f}, futures {a_fut:+.4f} "
          f"(individually noisy: the common trend dominates)")
    print(f"identified spread-adjustment rate alpha_fut - alpha_spot: "
          f"{spread_rate:+.4f}/day -> half-life {np.log(2) / spread_rate:.1f} d")
    print(f"error-correction half-life via AR(1) on the ECT: "
          f"{ec_half_life(res, data):.1f} days (true: 20)")

    h = 20
    fc, lo, hi = res.predict(steps=h, alpha=0.10)
    last = data.iloc[-1]
    print(f"\n{h}-day forecast (log levels, 90% band):")
    print(f"  spot now {last['log_spot']:.4f} -> {fc[-1, 0]:.4f} "
          f"[{lo[-1, 0]:.4f}, {hi[-1, 0]:.4f}]")
    print(f"  fut  now {last['log_fut']:.4f} -> {fc[-1, 1]:.4f} "
          f"[{lo[-1, 1]:.4f}, {hi[-1, 1]:.4f}]")
    basis_now = last["log_fut"] - last["log_spot"]
    basis_fc = fc[-1, 1] - fc[-1, 0]
    print(f"  basis {basis_now:+.4f} -> {basis_fc:+.4f} "
          f"(reverting toward +0.02)")
