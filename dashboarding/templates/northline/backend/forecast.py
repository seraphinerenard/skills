"""Demand forecasting: Holt-Winters with a seasonal-naive baseline.

Contract (see references/architecture.md):
- Backtest on a trailing holdout; report MAPE for the model and the baseline.
- If Holt-Winters does not beat seasonal-naive on the holdout, serve naive and say so.
- Intervals from holdout residuals (empirical 10th/90th percentiles).

The series here is weekly order intake per bus model (yearly seasonality,
period 52), but the function is generic over any regular series.
"""

from datetime import date, timedelta

import numpy as np

HOLDOUT = 13   # weeks held out for the backtest
SEASON = 52    # yearly seasonality on weekly data


def _mape(actual: np.ndarray, pred: np.ndarray) -> float:
    mask = actual > 0
    return float(np.mean(np.abs(actual[mask] - pred[mask]) / actual[mask]) * 100)


def _seasonal_naive(train: np.ndarray, horizon: int) -> np.ndarray:
    last_season = train[-SEASON:]
    reps = int(np.ceil(horizon / SEASON))
    return np.tile(last_season, reps)[:horizon]


def _holt_winters(train: np.ndarray, horizon: int) -> np.ndarray:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    model = ExponentialSmoothing(
        train.astype(float), trend="add", seasonal="add",
        seasonal_periods=SEASON, initialization_method="estimated",
    ).fit()
    return np.asarray(model.forecast(horizon))


def forecast_series(weeks: list[str], values: list[float], horizon: int = 13) -> dict:
    """weeks: ISO Mondays ascending; values: same length. Returns the forecast payload."""
    y = np.asarray(values, dtype=float)
    if len(y) < SEASON * 2 + HOLDOUT:
        raise ValueError("need at least two seasons of history to forecast")

    train, test = y[:-HOLDOUT], y[-HOLDOUT:]

    naive_bt = _seasonal_naive(train, HOLDOUT)
    naive_mape = _mape(test, naive_bt)
    try:
        hw_bt = _holt_winters(train, HOLDOUT)
        hw_mape = _mape(test, hw_bt)
    except Exception:
        hw_bt, hw_mape = None, float("inf")

    if hw_mape < naive_mape:
        chosen, bt_pred, bt_mape = "holt_winters", hw_bt, hw_mape
        future = _holt_winters(y, horizon)
    else:
        chosen, bt_pred, bt_mape = "seasonal_naive", naive_bt, naive_mape
        future = _seasonal_naive(y, horizon)

    residuals = test - bt_pred
    lo_off, hi_off = np.percentile(residuals, 10), np.percentile(residuals, 90)

    last_week = date.fromisoformat(weeks[-1])
    out = []
    for i in range(horizon):
        wk = last_week + timedelta(weeks=i + 1)
        mean = max(0.0, float(future[i]))
        out.append({
            "week": wk.isoformat(),
            "mean": round(mean, 1),
            "lo": round(max(0.0, mean + float(lo_off)), 1),
            "hi": round(mean + float(hi_off), 1),
        })

    return {
        "model": chosen,
        "backtest_mape": round(bt_mape, 1),
        "baseline_mape": round(naive_mape, 1),
        "holdout_weeks": HOLDOUT,
        "forecast": out,
    }
