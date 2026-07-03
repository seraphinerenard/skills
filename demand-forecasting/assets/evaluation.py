"""Forecast evaluation: MASE, RMSSE, WRMSSE, pinball loss, empirical coverage.

pip install: numpy pandas

Long-format convention throughout: columns unique_id, ds, y (actuals) and
unique_id, ds, yhat (point forecasts) or q_* columns (quantile forecasts).
Scaled metrics take the TRAINING series separately because the scaling
denominator must come from data available before the forecast origin;
computing it on the test window rewards forecasts on volatile test periods.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _naive_scale(y_train: np.ndarray, season: int, squared: bool) -> float:
    """In-sample seasonal-naive error. M5 convention: season=1 and the series
    starts at its first non-zero observation (leading zeros are pre-launch)."""
    first_nz = np.argmax(y_train != 0)
    y = y_train[first_nz:]
    if len(y) <= season:
        return np.nan
    d = y[season:] - y[:-season]
    return float(np.mean(d**2)) if squared else float(np.mean(np.abs(d)))


def mase(y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray,
         season: int = 1) -> float:
    scale = _naive_scale(np.asarray(y_train, float), season, squared=False)
    if not scale or np.isnan(scale):  # constant or too-short training series
        return np.nan
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))) / scale)


def rmsse(y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray,
          season: int = 1) -> float:
    scale = _naive_scale(np.asarray(y_train, float), season, squared=True)
    if not scale or np.isnan(scale):
        return np.nan
    return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred))**2) / scale))


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Kept for demonstrating its failure mode near zero; do not select models
    with it on intermittent series (see SKILL.md, Evaluation)."""
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2
    ok = denom > 0
    return float(np.mean(np.abs(y_true[ok] - y_pred[ok]) / denom[ok]) * 100)


def wrmsse(train: pd.DataFrame, actual: pd.DataFrame, forecast: pd.DataFrame,
           season: int = 1, weight_window: int = 28,
           weights: pd.Series | None = None) -> tuple[float, pd.DataFrame]:
    """M5-style weighted RMSSE across series.

    Default weights are each series' share of total y over the last
    weight_window training rows. M5 weighted by dollar sales (units x price);
    pass precomputed dollar weights via `weights` (indexed by unique_id) to
    reproduce that. Returns (wrmsse, per-series detail frame).
    """
    if weights is None:
        tail = train.groupby("unique_id").tail(weight_window)
        w = tail.groupby("unique_id")["y"].sum()
        weights = w / w.sum()

    merged = actual.merge(forecast, on=["unique_id", "ds"], how="inner")
    rows = []
    for uid, g in merged.groupby("unique_id"):
        tr = train.loc[train["unique_id"] == uid, "y"].to_numpy()
        r = rmsse(g["y"].to_numpy(), g["yhat"].to_numpy(), tr, season)
        rows.append({"unique_id": uid, "rmsse": r,
                     "weight": float(weights.get(uid, 0.0))})
    detail = pd.DataFrame(rows)
    valid = detail.dropna(subset=["rmsse"])
    score = float((valid["rmsse"] * valid["weight"]).sum() / valid["weight"].sum())
    return score, detail


def pinball(y_true: np.ndarray, y_pred: np.ndarray, q: float) -> float:
    """Mean pinball (quantile) loss. Lower is better; a forecast minimizes it
    only by being the true conditional q-quantile."""
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    diff = y_true - y_pred
    return float(np.mean(np.maximum(q * diff, (q - 1) * diff)))


def coverage(y_true: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> dict:
    """Empirical interval coverage and mean width. Compare coverage to the
    nominal level BEFORE admiring a narrow interval: narrow and under-covering
    means the model is lying about its uncertainty."""
    y_true = np.asarray(y_true, float)
    inside = (y_true >= np.asarray(lo, float)) & (y_true <= np.asarray(hi, float))
    return {"coverage": float(np.mean(inside)),
            "mean_width": float(np.mean(np.asarray(hi, float) - np.asarray(lo, float))),
            "n": int(len(y_true))}


def forecast_value_added(train: pd.DataFrame, actual: pd.DataFrame,
                         forecast: pd.DataFrame, season: int = 1) -> pd.DataFrame:
    """FVA vs seasonal naive, per series: positive means the model earns its
    complexity. Seasonal naive repeats the last observed seasonal cycle."""
    rows = []
    for uid, g in actual.groupby("unique_id"):
        tr = train.loc[train["unique_id"] == uid].sort_values("ds")["y"].to_numpy()
        h = len(g)
        snaive = np.array([tr[-season + (i % season)] for i in range(h)])
        f = forecast.loc[forecast["unique_id"] == uid].sort_values("ds")["yhat"].to_numpy()
        y = g.sort_values("ds")["y"].to_numpy()
        m_model = mase(y, f, tr, season)
        m_naive = mase(y, snaive, tr, season)
        rows.append({"unique_id": uid, "mase_model": m_model, "mase_snaive": m_naive,
                     "fva_pct": 100 * (1 - m_model / m_naive) if m_naive else np.nan})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    periods, horizon, season = 104, 13, 52
    ds = pd.date_range("2024-01-07", periods=periods + horizon, freq="W-MON")

    # Three archetypes: smooth seasonal, trending, intermittent.
    t = np.arange(periods + horizon)
    smooth = 200 + 60 * np.sin(2 * np.pi * t / 52) + rng.normal(0, 8, len(t))
    trend = 50 + 1.5 * t + rng.normal(0, 6, len(t))
    intermittent = rng.binomial(1, 0.2, len(t)) * rng.poisson(6, len(t))

    frames = []
    for uid, y in [("smooth", smooth), ("trend", trend), ("lumpy", intermittent)]:
        frames.append(pd.DataFrame({"unique_id": uid, "ds": ds, "y": y}))
    panel = pd.concat(frames, ignore_index=True)
    train = panel.groupby("unique_id").head(periods).reset_index(drop=True)
    actual = panel.groupby("unique_id").tail(horizon).reset_index(drop=True)

    # "Model": oracle plus noise, so metrics have something non-trivial to rank.
    forecast = actual.copy()
    forecast["yhat"] = forecast["y"] + rng.normal(0, 10, len(forecast))
    forecast.loc[forecast["unique_id"] == "lumpy", "yhat"] = (
        train.loc[train["unique_id"] == "lumpy", "y"].mean())  # flat rate forecast
    forecast = forecast[["unique_id", "ds", "yhat"]]

    print("Per-series MASE / RMSSE (season=1 scaling, M5 convention):")
    for uid in ["smooth", "trend", "lumpy"]:
        tr = train.loc[train["unique_id"] == uid, "y"].to_numpy()
        y = actual.loc[actual["unique_id"] == uid, "y"].to_numpy()
        f = forecast.loc[forecast["unique_id"] == uid, "yhat"].to_numpy()
        print(f"  {uid:8s} MASE={mase(y, f, tr):6.3f}  RMSSE={rmsse(y, f, tr):6.3f}"
              f"  sMAPE={smape(y, f):7.1f}%")

    score, detail = wrmsse(train, actual, forecast)
    print(f"\nWRMSSE (weights = last-28-row share of units): {score:.3f}")
    print(detail.to_string(index=False))

    print("\nFVA vs seasonal naive (season=52):")
    print(forecast_value_added(train, actual, forecast, season=52).to_string(index=False))

    # Pinball + coverage on the smooth series with a deliberately narrow interval.
    y = actual.loc[actual["unique_id"] == "smooth", "y"].to_numpy()
    f = forecast.loc[forecast["unique_id"] == "smooth", "yhat"].to_numpy()
    print(f"\nPinball q=0.9 (smooth): {pinball(y, f + 5, 0.9):.2f}")
    print("Nominal 80% interval, width +/-5 (too narrow):",
          coverage(y, f - 5, f + 5))
    print("Nominal 80% interval, width +/-13:",
          coverage(y, f - 13, f + 13))
