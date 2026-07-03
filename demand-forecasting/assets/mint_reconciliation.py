"""Hierarchical reconciliation with hierarchicalforecast: BottomUp vs MinT.

pip install: hierarchicalforecast statsforecast pandas numpy

Demo: a total -> region -> store hierarchy where bottom series are noisy and
aggregates are smooth. Independent base forecasts at every level are incoherent
(children do not sum to parents); reconciliation restores coherence and MinT
with shrinkage usually buys accuracy at the aggregate levels too, because it
maps the residual covariance structure into the projection. mint_shrink needs
in-sample fitted residuals, which is why the base run uses fitted=True.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import MSTL, AutoETS
from hierarchicalforecast.core import HierarchicalReconciliation
from hierarchicalforecast.methods import BottomUp, MinTrace
from hierarchicalforecast.utils import aggregate

from evaluation import rmsse


def bottom_panel(n_regions=4, stores_per_region=5, n_weeks=156, seed=17
                 ) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ds = pd.date_range("2023-01-02", periods=n_weeks, freq="W-MON")
    t = np.arange(n_weeks)
    frames = []
    for r in range(n_regions):
        phase = rng.uniform(0, 52)
        # Shared regional shock: sibling residuals correlate, which is the
        # structure MinT's covariance estimate can use and BottomUp cannot.
        shock = rng.lognormal(0, 0.12, n_weeks)
        for s in range(stores_per_region):
            base = rng.uniform(30, 90)
            season = 1 + 0.3 * np.sin(2 * np.pi * (t - phase) / 52)
            y = base * season * shock * rng.lognormal(0, 0.25, n_weeks)
            frames.append(pd.DataFrame({
                "total": "Total", "region": f"R{r}", "store": f"R{r}_S{s}",
                "ds": ds, "y": y}))
    return pd.concat(frames, ignore_index=True)


def main(horizon=13):
    spec = [["total"], ["total", "region"], ["total", "region", "store"]]
    Y_df, S_df, tags = aggregate(bottom_panel(), spec)

    train = Y_df.groupby("unique_id").head(156 - horizon).reset_index(drop=True)
    test = Y_df.groupby("unique_id").tail(horizon).reset_index(drop=True)

    sf = StatsForecast(
        models=[MSTL(season_length=52, trend_forecaster=AutoETS(model="ZZN"))],
        freq="W-MON", n_jobs=1)
    Y_hat = sf.forecast(df=train, h=horizon, fitted=True)
    Y_fitted = sf.forecast_fitted_values()

    hrec = HierarchicalReconciliation(reconcilers=[
        BottomUp(),
        MinTrace(method="ols"),
        MinTrace(method="mint_shrink")])
    # hierarchicalforecast >= 1.0 renamed the summing-matrix argument S -> S_df
    Y_rec = hrec.reconcile(Y_hat_df=Y_hat, Y_df=Y_fitted, S_df=S_df, tags=tags)
    Y_rec = Y_rec.reset_index() if "unique_id" not in Y_rec.columns else Y_rec

    method_cols = [c for c in Y_rec.columns if c.startswith("MSTL")]
    labels = {c: ("base" if c == "MSTL" else
                  c.split("/")[-1].replace("MinTrace_method-mint_shrink",
                                           "mint_shrink")
                  .replace("MinTrace_method-ols", "mint_ols")
                  .replace("BottomUp", "bottom_up")) for c in method_cols}
    merged = test.merge(Y_rec, on=["unique_id", "ds"])

    print(f"{S_df.shape[0]} series ({S_df.shape[1] - 1} bottom), h={horizon}."
          " Mean RMSSE by level:")
    print("  " + f"{'level':22s}" + "".join(f"{labels[c]:>18s}"
                                            for c in method_cols))
    for level, uids in tags.items():
        row = f"  {level:22s}"
        for m in method_cols:
            scores = []
            for uid in uids:
                tr = train.loc[train["unique_id"] == uid, "y"].to_numpy()
                g = merged[merged["unique_id"] == uid].sort_values("ds")
                scores.append(rmsse(g["y"].to_numpy(), g[m].to_numpy(), tr))
            row += f"{np.nanmean(scores):18.3f}"
        print(row)

    # Coherence check: children of each region must sum to the region.
    def coherence_gap(col: str) -> float:
        gaps = []
        for region_uid in tags["total/region"]:
            kids = [u for u in tags["total/region/store"]
                    if u.startswith(region_uid + "/")]
            parent = merged[merged["unique_id"] == region_uid].sort_values("ds")
            kid_sum = (merged[merged["unique_id"].isin(kids)]
                       .groupby("ds")[col].sum().to_numpy())
            gaps.append(np.max(np.abs(parent[col].to_numpy() - kid_sum)))
        return float(np.max(gaps))

    print("\nMax |parent - sum(children)| across regions:")
    for m in method_cols:
        print(f"  {labels[m]:22s} {coherence_gap(m):10.4f}")


if __name__ == "__main__":
    main()
