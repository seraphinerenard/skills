"""Forecast value added (FVA) stairstep and forecast stability (plan churn).

pip install: numpy pandas

Conventions, chosen deliberately:
- WAPE (sum|error| / sum|actual|) is the accuracy metric, because MAPE explodes
  on low-volume rows and rewards under-forecasting; FVA differences in MAPE
  terms routinely reverse sign when recomputed in WAPE on the same data.
- FVA is reported in WAPE percentage points, positive = the step reduced WAPE
  relative to the comparison. Each process step is compared to BOTH the
  seasonal naive and the step immediately upstream; a step can beat the naive
  while destroying value added by the step before it, and the stairstep view
  is the whole point of the exercise (Gilliland's FVA methodology).
- Baselines are computed from actuals as of the forecast origin: naive is the
  prior period, seasonal naive the same period one season back. Rows without a
  full set of baselines and step forecasts are dropped so every row of the
  stairstep is scored on the identical sample; scoring steps on different
  samples is the most common way an FVA table lies.
- Bias is signed: sum(forecast - actual) / sum(actual). A step that halves
  WAPE while running +8% bias still wrecks inventory; report both.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _wape(y: np.ndarray, f: np.ndarray) -> float:
    return float(np.sum(np.abs(f - y)) / np.sum(np.abs(y)))


def _bias(y: np.ndarray, f: np.ndarray) -> float:
    return float(np.sum(f - y) / np.sum(y))


def fva_stairstep(df: pd.DataFrame, steps: list[str], season: int = 12,
                  id_col: str = "unique_id", ds_col: str = "ds",
                  y_col: str = "y") -> pd.DataFrame:
    """Stairstep table over process steps in upstream-to-downstream order,
    e.g. steps=["stat", "planner", "consensus"]. df is long format, one row
    per (series, period), sorted or sortable by ds within series."""
    d = df.sort_values([id_col, ds_col]).copy()
    g = d.groupby(id_col, observed=True)[y_col]
    d["naive"] = g.shift(1)
    d["snaive"] = g.shift(season)
    cols = ["snaive", "naive"] + steps
    d = d.dropna(subset=cols + [y_col])
    if d.empty:
        raise ValueError("no rows with all baselines and steps populated; "
                         "need > season periods of history per series")
    y = d[y_col].to_numpy(float)
    rows = []
    prev_wape = None
    snaive_wape = _wape(y, d["snaive"].to_numpy(float))
    for name in cols:
        f = d[name].to_numpy(float)
        w = _wape(y, f)
        rows.append({
            "step": name,
            "wape_pct": round(100 * w, 1),
            "bias_pct": round(100 * _bias(y, f), 1),
            "fva_vs_snaive_pp": round(100 * (snaive_wape - w), 1),
            "fva_vs_prev_step_pp": (round(100 * (prev_wape - w), 1)
                                    if prev_wape is not None else np.nan),
        })
        prev_wape = w
    out = pd.DataFrame(rows)
    out.attrs["n_rows_scored"] = len(d)
    return out


def plan_churn(vintages: pd.DataFrame, id_col: str = "unique_id",
               target_col: str = "target", vintage_col: str = "vintage",
               f_col: str = "forecast") -> pd.DataFrame:
    """Period-over-period revision of the plan: for each consecutive vintage
    pair, sum|F_new - F_old| / sum|F_old| over the target periods both
    vintages cover. This is the number planners feel; a plan that churns 15%
    a week gets overridden into a flat line no matter what accuracy says."""
    v = vintages.sort_values([id_col, target_col, vintage_col]).copy()
    v["prev_f"] = v.groupby([id_col, target_col], observed=True)[f_col].shift(1)
    v = v.dropna(subset=["prev_f"])
    rows = []
    for vin, grp in v.groupby(vintage_col, observed=True):
        churn = float(np.sum(np.abs(grp[f_col] - grp["prev_f"]))
                      / np.sum(np.abs(grp["prev_f"])))
        rows.append({"vintage": vin, "n_targets": len(grp),
                     "churn_pct": round(100 * churn, 1)})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------- demo ---

if __name__ == "__main__":
    rng = np.random.default_rng(11)
    pd.set_option("display.width", 120)

    # 40 SKUs x 48 months. True expectation mu = level x seasonality x trend;
    # demand y = mu x lognormal noise, cut 25% when a distributor event fires
    # (planners see the event calendar, the statistical model does not).
    n_series, n_months = 40, 48
    months = pd.period_range("2022-01", periods=n_months, freq="M").astype(str)
    frames = []
    for i in range(n_series):
        level = rng.lognormal(6, 0.8)
        seas = 1 + 0.30 * np.sin(2 * np.pi * (np.arange(n_months)
                                              + rng.integers(12)) / 12)
        trend = (1 + rng.normal(0.002, 0.001)) ** np.arange(n_months)
        mu = level * seas * trend
        event = rng.random(n_months) < 0.06
        materialized = event & (rng.random(n_months) < 0.7)
        y = mu * rng.lognormal(0, 0.18, n_months) * np.where(materialized, 0.75, 1.0)
        frames.append(pd.DataFrame({"unique_id": f"sku_{i:02d}", "ds": months,
                                    "y": y, "mu": mu, "event": event}))
    df = pd.concat(frames, ignore_index=True)

    # Statistical step: recovers mu with estimation error, blind to events.
    df["stat"] = df["mu"] * rng.lognormal(0, 0.08, len(df))
    # Planner step: cuts 25% on flagged events (right 70% of the time), and
    # pads everything +5% on average, the small-upward-adjustment habit the
    # override literature finds destroys accuracy.
    pad = rng.lognormal(0.05, 0.05, len(df))
    df["planner"] = df["stat"] * pad * np.where(df["event"], 0.75, 1.0)
    # Consensus step: rounds to the nearest 10 and pads another 2%.
    df["consensus"] = np.round(df["planner"] * 1.02, -1)

    print("FVA stairstep, 40 SKUs x 48 months, monthly, season=12")
    tab = fva_stairstep(df, steps=["stat", "planner", "consensus"], season=12)
    print(tab.to_string(index=False))
    print(f"rows scored: {tab.attrs['n_rows_scored']}")
    print("Read the last column: every step below 'stat' with a negative "
          "number is a meeting that made the number worse.")

    print()
    print("Plan churn across 6 weekly re-forecasts of the same quarter")
    # Same statistical plan re-run weekly with new noise: accuracy identical
    # in expectation, churn is pure cost.
    targets = [f"2026-{m:02d}" for m in (7, 8, 9)]
    rows = []
    for vin in range(6):
        for t in targets:
            for i in range(8):
                base = 1000 + 80 * i
                rows.append({"unique_id": f"sku_{i:02d}", "target": t,
                             "vintage": f"wk{vin}",
                             "forecast": base * rng.lognormal(0, 0.12)})
    print(plan_churn(pd.DataFrame(rows)).to_string(index=False))
    print("A 12-15% weekly whipsaw with zero information gain: dampen "
          "re-forecast output (e.g. publish only revisions > one week of "
          "supply) before planners dampen it for you by ignoring the system.")
