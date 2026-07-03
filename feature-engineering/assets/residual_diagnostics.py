#!/usr/bin/env python3
"""Residual diagnostics for grouped forecasting models.

pip install: numpy pandas scipy

Residuals are the feature-search directive: structure left in the residual
names the feature that is missing. Three questions, three tools.

1. Is there structure left in time? Ljung-Box per series; report the share
   of series rejecting whiteness at p<0.05. A share near the 5% false-alarm
   rate is clean; a share above roughly 20% says add lags or seasonality.
2. Does a candidate column explain the residual? Binned mean-residual
   profile plus eta-squared (between-bin share of residual variance).
3. Where does the model sit biased? Mean residual by calendar slice or by
   group, with counts, so a 2% bias on the largest store is visible.
"""

import numpy as np
import pandas as pd
from scipy.stats import chi2


def ljung_box(resid, lags=10):
    """Returns (Q, p) for the Ljung-Box whiteness test at the given lag count."""
    x = np.asarray(resid, dtype=float)
    x = x[~np.isnan(x)] - np.nanmean(x)
    n = len(x)
    denom = float(np.dot(x, x))
    if n <= lags + 1 or denom == 0.0:
        return np.nan, np.nan
    r = np.array([np.dot(x[:-k], x[k:]) / denom for k in range(1, lags + 1)])
    q = n * (n + 2.0) * np.sum(r**2 / (n - np.arange(1, lags + 1)))
    return q, float(chi2.sf(q, lags))


def per_group_ljung_box(df, keys, resid_col, lags=10, alpha=0.05):
    """Share of series rejecting whiteness, plus the per-series p-values."""
    rows = []
    for name, g in df.groupby(keys, observed=True, sort=False):
        _, p = ljung_box(g[resid_col].to_numpy(), lags)
        rows.append((name, p))
    out = pd.DataFrame(rows, columns=["series", "p"]).dropna()
    share = float((out["p"] < alpha).mean()) if len(out) else np.nan
    return share, out


def residual_vs_feature(resid, candidate, n_bins=10):
    """Binned mean-residual profile and eta-squared for a candidate feature.

    eta2 is the share of residual variance explained by bin membership; a
    value above roughly 0.02 on holdout residuals marks a feature worth
    adding. Categorical candidates use their levels as bins.
    """
    resid = np.asarray(resid, dtype=float)
    cand = pd.Series(candidate).reset_index(drop=True)
    if cand.dtype.kind in "if" and cand.nunique() > n_bins:
        bins = pd.qcut(cand, n_bins, duplicates="drop")
    else:
        bins = cand
    tab = (
        pd.DataFrame({"bin": bins, "resid": resid})
        .groupby("bin", observed=True)["resid"]
        .agg(["mean", "count"])
        .reset_index()
    )
    grand = resid.mean()
    ss_between = float((tab["count"] * (tab["mean"] - grand) ** 2).sum())
    ss_total = float(((resid - grand) ** 2).sum())
    eta2 = ss_between / ss_total if ss_total > 0 else np.nan
    return eta2, tab


def bias_table(df, by, resid_col):
    """Mean residual and count by one or more grouping columns."""
    return (
        df.groupby(by, observed=True)[resid_col]
        .agg(["mean", "count"])
        .reset_index()
        .sort_values("mean")
    )


def _demo_panel(seed=3):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=300, freq="D")
    dow_effect = np.array([0.0, -1.0, -1.5, -1.0, 1.0, 4.0, 3.0])
    rows = []
    for s in range(20):
        level = rng.uniform(20, 50)
        for d in dates:
            mu = level + 2.0 * dow_effect[d.dayofweek]
            rows.append((f"S{s:02d}", d, d.dayofweek, mu + rng.normal(0, 1.5)))
    return pd.DataFrame(rows, columns=["series", "date", "dow", "y"])


if __name__ == "__main__":
    df = _demo_panel()

    # model A ignores day-of-week: per-series mean only
    df["pred_a"] = df.groupby("series")["y"].transform("mean")
    df["resid_a"] = df["y"] - df["pred_a"]
    # model B adds the missing feature: per-series x day-of-week mean
    df["pred_b"] = df.groupby(["series", "dow"])["y"].transform("mean")
    df["resid_b"] = df["y"] - df["pred_b"]

    for tag, col in [("A (no dow feature)", "resid_a"), ("B (dow added)", "resid_b")]:
        share, _ = per_group_ljung_box(df, ["series"], col, lags=14)
        eta2, tab = residual_vs_feature(df[col].to_numpy(), df["dow"])
        print(f"model {tag}: Ljung-Box rejection share={share:.2f}  "
              f"eta2(resid ~ dow)={eta2:.3f}")
        if col == "resid_a":
            print(bias_table(df, "dow", col).to_string(index=False,
                                                       float_format="%.2f"))
    print("reading: model A fails whiteness in every series and dow explains "
          "the residual; adding dow removes both findings")
