#!/usr/bin/env python3
"""Leak-safe feature factory for panel (grouped time-series) data.

pip install: numpy pandas

Every feature built here reads only information available strictly before
the target row's timestamp, or plan data (promo calendars, holidays) that
is known in advance by construction. Rolling and EWM features shift the
input series before windowing, so the window never touches the current
row. `leak_check` verifies the property mechanically: it truncates the
panel at probe dates, rebuilds, and diffs the feature rows.

Conventions: long format, one row per (keys, date); `keys` is the list of
group columns; the frame carries no duplicate (keys, date) pairs; the date
column has dtype datetime64.
"""

import numpy as np
import pandas as pd


def _sorted(df: pd.DataFrame, keys: list, date_col: str) -> pd.DataFrame:
    return df.sort_values(keys + [date_col], kind="mergesort").reset_index(drop=True)


def add_lags(df, keys, date_col, col, lags):
    """target lagged by each value in `lags` (in rows, i.e. panel periods)."""
    df = _sorted(df, keys, date_col)
    g = df.groupby(keys, observed=True, sort=False)[col]
    for lag in lags:
        df[f"{col}_lag{lag}"] = g.shift(lag)
    return df


def add_rollings(df, keys, date_col, col, windows, stats=("mean", "std"), shift=1):
    """Rolling stats over a window that ends `shift` rows before the current row.

    shift=1 is the leak-safe default for a target column: the window covers
    t-shift-window+1 .. t-shift. shift=0 is valid only for columns already
    known at prediction time (price plans, weather forecasts).
    """
    df = _sorted(df, keys, date_col)
    g = df.groupby(keys, observed=True, sort=False)[col]
    for w in windows:
        base = g.shift(shift)
        gb = base.groupby([df[k] for k in keys], observed=True, sort=False)
        for stat in stats:
            mp = max(1, w // 2)
            df[f"{col}_roll{w}_{stat}"] = gb.transform(
                lambda s, w=w, stat=stat, mp=mp: s.rolling(w, min_periods=mp).agg(stat)
            )
    return df


def add_ewm(df, keys, date_col, col, halflives, shift=1):
    """Exponentially weighted mean of the shifted series, one column per halflife."""
    df = _sorted(df, keys, date_col)
    g = df.groupby(keys, observed=True, sort=False)[col]
    base = g.shift(shift)
    gb = base.groupby([df[k] for k in keys], observed=True, sort=False)
    for h in halflives:
        df[f"{col}_ewm{h}"] = gb.transform(
            lambda s, h=h: s.ewm(halflife=h, min_periods=1).mean()
        )
    return df


def add_event_distance(df, keys, date_col, event_col, name=None, horizon=365):
    """days_since_<name> and days_until_<name>, capped at `horizon`.

    days_until is leak-safe only when the event column is plan data known in
    advance (promo calendar, holidays, scheduled price changes). For events
    observed only after the fact, use days_since alone and drop the until
    column before training.
    """
    name = name or event_col
    df = _sorted(df, keys, date_col)
    days = df[date_col].values.astype("datetime64[D]").astype(np.int64)
    since = np.full(len(df), horizon, dtype=np.int64)
    until = np.full(len(df), horizon, dtype=np.int64)
    for _, idx in df.groupby(keys, observed=True, sort=False).indices.items():
        d = days[idx]
        ev = d[df[event_col].values[idx].astype(bool)]
        if len(ev) == 0:
            continue
        pos = np.searchsorted(ev, d, side="right") - 1
        ok = pos >= 0
        since[idx[ok]] = np.minimum(d[ok] - ev[pos[ok]], horizon)
        nxt = np.searchsorted(ev, d, side="left")
        ok = nxt < len(ev)
        until[idx[ok]] = np.minimum(ev[nxt[ok]] - d[ok], horizon)
    df[f"days_since_{name}"] = since
    df[f"days_until_{name}"] = until
    return df


def add_calendar(df, date_col):
    """Bounded, repeating calendar columns. Deliberately excludes raw date
    ordinals and cumulative counters: those break at extrapolation time."""
    dt = df[date_col].dt
    df["dow"] = dt.dayofweek.astype(np.int8)
    df["dom"] = dt.day.astype(np.int8)
    df["month"] = dt.month.astype(np.int8)
    df["weekofyear"] = dt.isocalendar().week.astype(np.int8)
    return df


def add_fourier(df, date_col, period, k, prefix):
    """k sine/cosine harmonics of the given period (in days)."""
    t = df[date_col].values.astype("datetime64[D]").astype(np.int64).astype(float)
    for i in range(1, k + 1):
        arg = 2.0 * np.pi * i * t / period
        df[f"{prefix}_sin{i}"] = np.sin(arg)
        df[f"{prefix}_cos{i}"] = np.cos(arg)
    return df


def _same(a: np.ndarray, b: np.ndarray) -> bool:
    if a.shape != b.shape:
        return False
    if a.dtype.kind in "fc" or b.dtype.kind in "fc":
        return np.allclose(a.astype(float), b.astype(float), equal_nan=True)
    return bool(np.array_equal(a, b))


def leak_check(build, df, keys, date_col, observed_cols, n_probes=4):
    """Rebuild features on a censored panel and diff against the full build.

    `build` maps a raw panel frame to a feature frame at the same row grain.
    `observed_cols` lists the columns learned only as time passes: the target,
    plus any covariate recorded after the fact (actual weather, actual price
    paid). Plan-data columns (promo calendar, holidays, list-price schedule)
    stay visible at every date by assumption; declare a column as observed
    when that assumption fails for it.

    For each probe date t, the observed columns are masked to NaN from t
    onward, which reproduces the information set available when the row at t
    is scored. The feature rows at date == t must match the full-data build.
    A mismatch means some feature at t read a same-day or later observation.
    Returns a list of (probe_date, column) violations; an empty list passes.
    """
    if isinstance(observed_cols, str):
        observed_cols = [observed_cols]
    full = _sorted(build(df.copy()), keys, date_col)
    dates = np.sort(df[date_col].unique())
    half = dates[len(dates) // 2:]
    probes = half[:: max(1, len(half) // n_probes)][:n_probes]
    violations = []
    for t in probes:
        masked = df.copy()
        for c in observed_cols:
            masked[c] = masked[c].astype(float)
            masked.loc[masked[date_col] >= t, c] = np.nan
        part = _sorted(build(masked), keys, date_col)
        a = full[full[date_col] == t].set_index(keys).sort_index()
        b = part[part[date_col] == t].set_index(keys).sort_index()
        skip = set(observed_cols) | {date_col}
        for c in [c for c in a.columns if c not in skip]:
            if not _same(a[c].to_numpy(), b[c].to_numpy()):
                violations.append((str(np.datetime64(t, "D")), c))
    return violations


def _synthetic_panel(n_days=400, seed=7):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n_days, freq="D")
    rows = []
    for store in ["S1", "S2", "S3"]:
        for sku in ["A", "B"]:
            level = rng.uniform(20, 60)
            promo_days = set(rng.choice(n_days, size=n_days // 20, replace=False))
            for i, d in enumerate(dates):
                promo = i in promo_days
                mu = level * (1.0 + 0.25 * np.sin(2 * np.pi * d.dayofweek / 7))
                mu *= 1.6 if promo else 1.0
                rows.append((store, sku, d, promo, rng.poisson(mu)))
    return pd.DataFrame(rows, columns=["store", "sku", "date", "promo", "units"])


if __name__ == "__main__":
    keys, date_col = ["store", "sku"], "date"
    panel = _synthetic_panel()

    def build(df):
        df = add_lags(df, keys, date_col, "units", [1, 7, 14, 28])
        df = add_rollings(df, keys, date_col, "units", [7, 28], ("mean", "std"))
        df = add_ewm(df, keys, date_col, "units", [7, 28])
        df = add_event_distance(df, keys, date_col, "promo")
        df = add_calendar(df, date_col)
        df = add_fourier(df, date_col, 7.0, 3, "wk")
        return df

    feats = build(panel)
    print(f"panel rows={len(feats)} feature cols={feats.shape[1] - panel.shape[1]}")
    print(feats.tail(3).to_string(index=False, max_colwidth=12))

    bad = leak_check(build, panel, keys, date_col, ["units"])
    print(f"\nleak_check on the shifted build: {len(bad)} violations "
          f"({'PASS' if not bad else 'FAIL'})")

    def leaky_build(df):
        # classic bug: rolling window includes the current row (shift=0)
        return add_rollings(df, keys, date_col, "units", [7], ("mean",), shift=0)

    bad = leak_check(leaky_build, panel, keys, date_col, ["units"])
    print(f"leak_check on the unshifted build: {len(bad)} violations "
          f"(expected > 0), e.g. {bad[:2]}")
