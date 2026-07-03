"""Statistical baselines via statsforecast: MSTL/Theta for smooth weekly series,
Croston-family for intermittent demand, with evaluation tied to achieved
service level.

pip install: statsforecast pandas numpy

Two demos in __main__:
  A. Weekly seasonal panel: MSTL, AutoTheta, SeasonalNaive under rolling-origin
     cross-validation, scored by MASE. AutoETS is absent on purpose: state-space
     ETS caps seasonal period near 24, so weekly m=52 goes through MSTL
     decomposition with an ETS trend forecaster on the deseasonalized remainder.
  B. Intermittent panel: CrostonClassic, CrostonSBA, TSB, ADIDA against the
     zero forecast. The zero forecast wins MAE whenever the demand probability
     is under one half, which is exactly why MAE-family metrics are banned for
     intermittent series; the decision metric is the achieved service level of
     the stock position each rate forecast implies.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import (
    MSTL, AutoTheta, SeasonalNaive, AutoETS,
    CrostonClassic, CrostonSBA, TSB, ADIDA,
)

from evaluation import mase


def poisson_ppf(q: float, mu: float) -> int:
    """Smallest k with P(X <= k) >= q for X ~ Poisson(mu). Loop form avoids a
    scipy dependency."""
    if mu <= 0:
        return 0
    k, p, cdf = 0, np.exp(-mu), np.exp(-mu)
    while cdf < q and k < 10_000:
        k += 1
        p *= mu / k
        cdf += p
    return k


def negbin_ppf(q: float, mu: float, var: float) -> int:
    """Negative binomial quantile parameterized by mean and variance. Falls
    back to Poisson when the variance estimate carries no overdispersion."""
    if mu <= 0:
        return 0
    if var <= mu * 1.01:
        return poisson_ppf(q, mu)
    r = mu * mu / (var - mu)
    p = r / (r + mu)
    k, pmf, cdf = 0, p**r, p**r
    while cdf < q and k < 10_000:
        k += 1
        pmf *= (k + r - 1) / k * (1 - p)
        cdf += pmf
    return k


def smooth_panel(n_series=20, n_weeks=156, seed=3) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ds = pd.date_range("2023-01-02", periods=n_weeks, freq="W-MON")
    t = np.arange(n_weeks)
    frames = []
    for i in range(n_series):
        base = rng.uniform(80, 300)
        amp = rng.uniform(0.15, 0.4)
        phase = rng.uniform(0, 52)
        y = base * (1 + amp * np.sin(2 * np.pi * (t - phase) / 52))
        y = y + rng.normal(0, base * 0.05, n_weeks)
        frames.append(pd.DataFrame({"unique_id": f"s{i}", "ds": ds, "y": y}))
    return pd.concat(frames, ignore_index=True)


def intermittent_panel(n_series=30, n_weeks=130, seed=5) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ds = pd.date_range("2023-01-02", periods=n_weeks, freq="W-MON")
    frames = []
    for i in range(n_series):
        p = rng.uniform(0.08, 0.35)          # demand incidence per week
        size = rng.uniform(2, 12)            # mean size when demand occurs
        y = rng.binomial(1, p, n_weeks) * rng.poisson(size, n_weeks)
        frames.append(pd.DataFrame({"unique_id": f"part{i}", "ds": ds,
                                    "y": y.astype(float)}))
    return pd.concat(frames, ignore_index=True)


def demo_smooth() -> None:
    panel = smooth_panel()
    sf = StatsForecast(
        models=[MSTL(season_length=52, trend_forecaster=AutoETS(model="ZZN")),
                AutoTheta(season_length=52),
                SeasonalNaive(season_length=52)],
        freq="W-MON", n_jobs=1)
    cv = sf.cross_validation(df=panel, h=8, step_size=8, n_windows=3)
    cv = cv.reset_index() if "unique_id" not in cv.columns else cv

    model_cols = [c for c in cv.columns
                  if c not in ("unique_id", "ds", "cutoff", "y")]
    print("A. Weekly seasonal panel, 3 rolling origins, h=8, mean MASE:")
    for m in model_cols:
        scores = []
        for (uid, cutoff), g in cv.groupby(["unique_id", "cutoff"]):
            tr = panel[(panel["unique_id"] == uid) & (panel["ds"] <= cutoff)]
            scores.append(mase(g["y"].to_numpy(), g[m].to_numpy(),
                               tr["y"].to_numpy()))
        print(f"  {m:16s} {np.nanmean(scores):.3f}")


def demo_intermittent(target_service=0.95, review_weeks=2) -> None:
    panel = intermittent_panel()
    h = 26
    train = panel.groupby("unique_id").head(130 - h).reset_index(drop=True)
    test = panel.groupby("unique_id").tail(h).reset_index(drop=True)

    sf = StatsForecast(
        models=[CrostonClassic(), CrostonSBA(),
                TSB(alpha_d=0.2, alpha_p=0.2), ADIDA()],
        freq="W-MON", n_jobs=1)
    fc = sf.forecast(df=train, h=h)
    fc = fc.reset_index() if "unique_id" not in fc.columns else fc
    fc["ZeroForecast"] = 0.0

    methods = ["CrostonClassic", "CrostonSBA", "TSB", "ADIDA", "ZeroForecast"]
    print(f"\nB. Intermittent panel ({panel['unique_id'].nunique()} parts, "
          f"{h}-week test), target cycle service {target_service:.0%}:")
    print(f"  {'method':16s} {'MAE':>6s} {'serv_poisson':>13s} {'serv_nb':>8s} "
          f"{'stock_nb':>9s}")
    for m in methods:
        maes, stocks = [], []
        hits = {"pois": 0, "nb": 0}
        trials = 0
        for uid, g in test.groupby("unique_id"):
            rate = float(fc.loc[fc["unique_id"] == uid, m].iloc[0])
            y = g.sort_values("ds")["y"].to_numpy()
            maes.append(np.mean(np.abs(y - rate)))
            mu_lt = rate * review_weeks
            # Weekly demand variance from training data, scaled to the review
            # period assuming independence across weeks. Lumpy demand is
            # overdispersed, so Poisson sizing from the rate alone under-buys.
            var_w = float(train.loc[train["unique_id"] == uid, "y"].var())
            S = {"pois": poisson_ppf(target_service, mu_lt),
                 "nb": negbin_ppf(target_service, mu_lt, var_w * review_weeks)}
            stocks.append(S["nb"])
            for i in range(0, len(y) - review_weeks + 1, review_weeks):
                dem = y[i:i + review_weeks].sum()
                trials += 1
                for k in hits:
                    hits[k] += int(dem <= S[k])
        print(f"  {m:16s} {np.mean(maes):6.2f} {hits['pois'] / trials:13.1%} "
              f"{hits['nb'] / trials:8.1%} {np.mean(stocks):9.1f}")
    print("  The zero forecast posts the best-looking MAE and a service level"
          " equal to the demand-free share of review periods. Poisson sizing"
          " from the rate under-covers because burst sizes overdisperse the"
          " lead-time distribution; negative binomial sizing with the training"
          " variance reaches the target. Judge intermittent methods on"
          " inventory outcomes.")


if __name__ == "__main__":
    demo_smooth()
    demo_intermittent()
