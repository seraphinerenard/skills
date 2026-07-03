#!/usr/bin/env python3
"""Cohort, GRR/NRR, and customer-concentration engine over a raw transaction table.

pip install: pandas numpy

Input contract: a long transaction table, one row per invoice line or payment,
with a customer id, a timestamp, and a signed revenue amount (credits and
refunds negative). The engine aggregates to customer-month, so invoice
granularity does not matter. Convert currency at a fixed monthly rate BEFORE
this engine; converting after aggregation mixes rate moves into retention.

Definitions implemented (the ones buyers compute from the data-room tape):

  Base(t, w)  = customers with revenue > 0 in month t-w.
  GRR(t, w)   = sum_i min(rev_i[t], rev_i[t-w]) / sum_i rev_i[t-w], i in Base.
                Every customer is capped at their base-period revenue, so
                expansion never hides churn. GRR <= 100% by construction.
  NRR(t, w)   = sum_i rev_i[t] / sum_i rev_i[t-w], i in Base.
                Expansion of surviving customers counts; new logos never do.
  Logo(t, w)  = |{i in Base : rev_i[t] > 0}| / |Base(t, w)|.

The window w is in months: w=12 gives the annual figures buyers quote, w=1
gives the monthly series. Annual NRR is NOT monthly NRR to the 12th power;
reactivation and intra-year expansion break the compounding identity, so each
window is computed directly on the matrix.

Traps handled here:
  * Partial last month: the final month is dropped when the latest transaction
    lands before the cutoff day (default 22), because a half-billed month
    reads as mass churn.
  * Reactivation: a customer with zero revenue at t-w sits outside the base
    even if active earlier; their return counts as new business, never as
    retention.
  * Credits: customer-month revenue is clipped at zero after aggregation so a
    refund month reads as a churn month and the denominators stay positive.

Decomposition identity (asserted in the demo):
  NRR = 1 - churn_loss - contraction_loss + expansion_gain
  GRR = 1 - churn_loss - contraction_loss
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def monthly_matrix(
    tx: pd.DataFrame,
    customer_col: str = "customer_id",
    date_col: str = "date",
    revenue_col: str = "revenue",
    partial_month_cutoff_day: int = 22,
) -> pd.DataFrame:
    """Customer x month revenue matrix from a raw transaction table.

    Returns a wide DataFrame indexed by customer with a complete monthly
    PeriodIndex as columns (gap months filled with 0.0), values clipped at 0.
    """
    df = tx[[customer_col, date_col, revenue_col]].copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["month"] = df[date_col].dt.to_period("M")
    last_ts = df[date_col].max()
    if last_ts.day < partial_month_cutoff_day:
        df = df[df["month"] < df["month"].max()]
    m = df.pivot_table(
        index=customer_col, columns="month", values=revenue_col,
        aggfunc="sum", fill_value=0.0,
    )
    full = pd.period_range(m.columns.min(), m.columns.max(), freq="M")
    m = m.reindex(columns=full, fill_value=0.0)
    return m.clip(lower=0.0)


def retention_series(matrix: pd.DataFrame, window: int = 12) -> pd.DataFrame:
    """GRR, NRR, logo retention, and the loss/gain decomposition per month.

    One row per month t that has a full base month t-window inside the matrix.
    """
    months = list(matrix.columns)
    rows = []
    for k in range(window, len(months)):
        t, t0 = months[k], months[k - window]
        base = matrix.loc[matrix[t0] > 0, [t0, t]]
        denom = float(base[t0].sum())
        if denom <= 0:
            continue
        prev, cur = base[t0], base[t]
        churn = float(prev[cur == 0].sum()) / denom
        contraction = float((prev - cur)[(cur > 0) & (cur < prev)].sum()) / denom
        expansion = float((cur - prev)[cur > prev].sum()) / denom
        rows.append({
            "month": str(t),
            "window_m": window,
            "base_logos": int(len(base)),
            "base_revenue": denom,
            "grr": float(np.minimum(cur, prev).sum()) / denom,
            "nrr": float(cur.sum()) / denom,
            "logo_retention": float((cur > 0).mean()),
            "churn_loss": churn,
            "contraction_loss": contraction,
            "expansion_gain": expansion,
        })
    return pd.DataFrame(rows)


def cohort_triangle(matrix: pd.DataFrame, metric: str = "revenue") -> pd.DataFrame:
    """Cohort (month of first revenue) x age retention triangle.

    metric="revenue": cohort revenue at age a / cohort revenue at age 0.
      Values above 1.0 mean expansion outran churn inside the cohort.
    metric="logo": share of the cohort's original customers still active.
    """
    alive = matrix.sum(axis=1) > 0
    m = matrix[alive]
    first = m.gt(0).idxmax(axis=1)
    months = list(m.columns)
    pos = {mo: i for i, mo in enumerate(months)}
    out = {}
    for cohort, grp in m.groupby(first):
        start = pos[cohort]
        base_rev = float(grp[cohort].sum())
        base_n = int((grp[cohort] > 0).sum())
        row = {}
        for age, mo in enumerate(months[start:]):
            if metric == "revenue":
                row[age] = float(grp[mo].sum()) / base_rev
            else:
                row[age] = float((grp[mo] > 0).sum()) / base_n
        out[str(cohort)] = row
    tri = pd.DataFrame(out).T.sort_index()
    tri.index.name = "cohort"
    tri.columns.name = "age_months"
    return tri


def concentration(matrix: pd.DataFrame, trailing: int = 12) -> dict:
    """HHI and top-N revenue shares over the trailing-N-month book."""
    rev = matrix[matrix.columns[-trailing:]].sum(axis=1)
    rev = rev[rev > 0].sort_values(ascending=False)
    share = rev / rev.sum()
    hhi = float((share ** 2).sum())
    return {
        "trailing_months": trailing,
        "customers": int(len(rev)),
        "top1_share": float(share.iloc[0]),
        "top5_share": float(share.iloc[:5].sum()),
        "top10_share": float(share.iloc[:10].sum()),
        "hhi": hhi,
        "effective_customers": 1.0 / hhi,
    }


def _synthetic_transactions(seed: int = 11) -> pd.DataFrame:
    """36 months of SaaS-like invoices: monthly cohorts, early-tenure churn
    hazard, expansion drift on survivors, two whale accounts."""
    rng = np.random.default_rng(seed)
    rows = []
    cid = 0
    months = pd.period_range("2023-07", periods=36, freq="M")
    for j, m0 in enumerate(months[:-1]):
        for _ in range(int(rng.integers(8, 16))):
            cid += 1
            mrr = float(np.exp(rng.normal(np.log(2000), 0.8)))
            if rng.random() < 0.02:
                mrr *= 25.0  # whale
            for age, m in enumerate(months[j:]):
                hazard = 0.045 if age < 3 else 0.022
                if age > 0 and rng.random() < hazard:
                    break
                if age > 0:
                    mrr *= float(np.exp(rng.normal(0.008, 0.05)))
                day = int(rng.integers(1, 28))
                rows.append({
                    "customer_id": f"C{cid:04d}",
                    "date": m.to_timestamp() + pd.Timedelta(days=day),
                    "revenue": round(mrr, 2),
                })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    tx = _synthetic_transactions()
    print(f"transactions: {len(tx):,} rows, "
          f"{tx['customer_id'].nunique()} customers, "
          f"{tx['date'].min():%Y-%m} to {tx['date'].max():%Y-%m}\n")

    m = monthly_matrix(tx)

    r12 = retention_series(m, window=12)
    cols = ["month", "base_logos", "grr", "nrr", "logo_retention",
            "churn_loss", "contraction_loss", "expansion_gain"]
    print("annual-window retention, last 6 months:")
    print(r12[cols].tail(6).to_string(index=False,
          float_format=lambda x: f"{x:0.3f}"))

    # decomposition identities
    assert np.allclose(r12["nrr"], 1 - r12["churn_loss"]
                       - r12["contraction_loss"] + r12["expansion_gain"])
    assert np.allclose(r12["grr"], 1 - r12["churn_loss"]
                       - r12["contraction_loss"])
    print("\ndecomposition identities hold (NRR and GRR reconcile exactly)")

    tri = cohort_triangle(m, metric="revenue")
    print("\ncohort revenue retention, first 6 cohorts x ages 0-12:")
    print(tri.iloc[:6, :13].to_string(float_format=lambda x: f"{x:0.2f}"))

    print("\nconcentration on the trailing-12-month book:")
    for k, v in concentration(m).items():
        print(f"  {k}: {v:,.3f}" if isinstance(v, float) else f"  {k}: {v}")
