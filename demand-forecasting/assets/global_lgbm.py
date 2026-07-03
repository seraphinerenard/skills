"""Global LightGBM demand pipeline: leak-safe origin-based features, quantile
objectives, rolling-origin cross-validation.

pip install: lightgbm pandas numpy

Framing: one model serves every series and every horizon step. Each training
row is (series, forecast origin o, step h): the features are computed from data
observed at or before o, the step h is itself a feature, and the target is
y[o + h]. This is the direct multi-horizon design used by mlforecast's
max_horizon mode and by Amazon's MQ-class models. Leak safety holds by
construction because no feature reads past the origin; the only columns allowed
from the target date are covariates that are genuinely known in advance
(promo calendar, planned price, calendar structure).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import lightgbm as lgb

from evaluation import mase, pinball, coverage

LAGS = (0, 1, 2, 3, 7, 12, 25, 51)  # periods back from the origin, 0 = origin
WINDOWS = (4, 13)
FUTURE_KNOWN = ("promo", "price")   # must be plannable; sales-derived columns never qualify


def origin_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Per (series, origin) features from data observed up to the origin."""
    g = panel.sort_values(["unique_id", "ds"]).copy()
    grp = g.groupby("unique_id")["y"]
    for j in LAGS:
        g[f"y_back_{j}"] = grp.shift(j)
    for w in WINDOWS:
        g[f"roll_mean_{w}"] = grp.transform(lambda s: s.rolling(w).mean())
    g[f"roll_std_{WINDOWS[-1]}"] = grp.transform(
        lambda s: s.rolling(WINDOWS[-1]).std())
    return g.rename(columns={"ds": "origin"}).drop(columns=["y", *FUTURE_KNOWN])


def make_rows(panel: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Cross-join origin features with steps 1..horizon; attach the target and
    the future-known covariates AT THE TARGET DATE."""
    feats = origin_features(panel)
    steps = pd.DataFrame({"step": np.arange(1, horizon + 1)})
    rows = feats.merge(steps, how="cross")
    rows["target_ds"] = rows["origin"] + pd.to_timedelta(rows["step"] * 7, unit="D")
    target = panel[["unique_id", "ds", "y", *FUTURE_KNOWN]].rename(
        columns={"ds": "target_ds"})
    rows = rows.merge(target, on=["unique_id", "target_ds"], how="inner")
    woy = rows["target_ds"].dt.isocalendar().week.astype(float)
    rows["woy_sin"] = np.sin(2 * np.pi * woy / 52)
    rows["woy_cos"] = np.cos(2 * np.pi * woy / 52)
    rows["unique_id"] = rows["unique_id"].astype("category")
    return rows


FEATURE_COLS = None  # resolved on first fit


def _feature_cols(rows: pd.DataFrame) -> list[str]:
    drop = {"origin", "target_ds", "y"}
    return [c for c in rows.columns if c not in drop]


def fit_quantile_models(rows: pd.DataFrame, quantiles: tuple[float, ...],
                        ) -> dict[float, lgb.LGBMRegressor]:
    """One booster per quantile. The M5 accuracy winner used tweedie for the
    point forecast; for a full quantile set, per-quantile objectives remain the
    dependable route in LightGBM."""
    cols = _feature_cols(rows)
    models = {}
    for q in quantiles:
        m = lgb.LGBMRegressor(objective="quantile", alpha=q, n_estimators=400,
                              learning_rate=0.05, num_leaves=63,
                              min_child_samples=20, verbose=-1)
        m.fit(rows[cols], rows["y"], categorical_feature=["unique_id"])
        models[q] = m
    return models


def predict_from(models: dict, rows_at_origin: pd.DataFrame) -> pd.DataFrame:
    cols = _feature_cols(rows_at_origin)
    out = rows_at_origin[["unique_id", "target_ds", "y"]].copy()
    for q, m in models.items():
        out[f"q{int(q * 100)}"] = np.clip(m.predict(rows_at_origin[cols]), 0, None)
    # Enforce monotone quantiles: crossed quantiles are common with independent
    # per-quantile boosters and break downstream newsvendor logic.
    qcols = sorted([c for c in out.columns if c.startswith("q")],
                   key=lambda c: int(c[1:]))
    out[qcols] = np.sort(out[qcols].to_numpy(), axis=1)
    return out


def rolling_origin_cv(panel: pd.DataFrame, cutoffs: list[pd.Timestamp],
                      horizon: int, quantiles=(0.1, 0.5, 0.9)) -> pd.DataFrame:
    """Train strictly before each cutoff (target dates included), predict the
    window after it. Refitting per cutoff is the honest protocol; reusing one
    fit across cutoffs leaks the later windows into the earlier scores."""
    all_rows = make_rows(panel, horizon)
    preds = []
    for cutoff in cutoffs:
        train = all_rows[all_rows["target_ds"] <= cutoff]
        test = all_rows[all_rows["origin"] == cutoff]
        models = fit_quantile_models(train, quantiles)
        p = predict_from(models, test)
        p["cutoff"] = cutoff
        preds.append(p)
    return pd.concat(preds, ignore_index=True)


def synthetic_panel(n_stores=8, n_skus=5, n_weeks=156, seed=11) -> pd.DataFrame:
    """Retail-shaped panel: multiplicative seasonality, promo uplift with a
    post-promo trough (pantry loading), price discounts tied to promos."""
    rng = np.random.default_rng(seed)
    ds = pd.date_range("2023-01-02", periods=n_weeks, freq="W-MON")
    t = np.arange(n_weeks)
    season = 1 + 0.35 * np.sin(2 * np.pi * (t - 8) / 52)
    frames = []
    for s in range(n_stores):
        for k in range(n_skus):
            base = rng.uniform(20, 120)
            promo = rng.binomial(1, 0.10, n_weeks).astype(float)
            post = np.roll(promo, 1); post[0] = 0
            price = np.round(rng.uniform(2, 8) * (1 - 0.25 * promo), 2)
            lam = base * season * (1 + 1.8 * promo) * (1 - 0.25 * post)
            y = rng.poisson(np.maximum(lam, 0.1))
            frames.append(pd.DataFrame({
                "unique_id": f"store{s}_sku{k}", "ds": ds, "y": y.astype(float),
                "promo": promo, "price": price}))
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    panel = synthetic_panel()
    horizon = 8
    cutoffs = [pd.Timestamp("2025-06-30"), pd.Timestamp("2025-08-25"),
               pd.Timestamp("2025-10-20")]
    preds = rolling_origin_cv(panel, cutoffs, horizon)

    print(f"{len(panel['unique_id'].unique())} series, horizon {horizon}, "
          f"{len(cutoffs)} rolling origins, {len(preds)} forecast rows\n")
    for q in (10, 50, 90):
        print(f"pinball q{q}: {pinball(preds['y'], preds[f'q{q}'], q / 100):.3f}")
    print("nominal 80% interval:", coverage(preds["y"], preds["q10"], preds["q90"]))

    # FVA of the median against seasonal naive, aggregated over series/cutoffs.
    rows = []
    for (uid, cutoff), g in preds.groupby(["unique_id", "cutoff"], observed=True):
        tr = panel[(panel["unique_id"] == uid) & (panel["ds"] <= cutoff)]
        tr_y = tr.sort_values("ds")["y"].to_numpy()
        g = g.sort_values("target_ds")
        snaive = np.array([tr_y[-52 + (i % 52)] for i in range(len(g))])
        rows.append({"model": mase(g["y"], g["q50"], tr_y),
                     "snaive": mase(g["y"], snaive, tr_y)})
    fva = pd.DataFrame(rows).mean()
    print(f"\nmean MASE  model={fva['model']:.3f}  seasonal_naive={fva['snaive']:.3f}"
          f"  FVA={100 * (1 - fva['model'] / fva['snaive']):.1f}%")

    models = fit_quantile_models(make_rows(panel, horizon), (0.5,))
    imp = pd.Series(models[0.5].feature_importances_,
                    index=_feature_cols(make_rows(panel, horizon))).nlargest(8)
    print("\ntop features (gain-ordered split counts):")
    print(imp.to_string())
