#!/usr/bin/env python3
# pip install numpy pandas lifelines scikit-learn
"""Contractual churn as a survival problem with time-varying covariates.

Two estimators on the same person-month panel:
    1. lifelines CoxTimeVaryingFitter on (id, start, stop, event) rows
    2. discrete-time hazard: logistic regression on person-months with
       tenure-bucket dummies (the pragmatic route; coefficients match the
       Cox partial-hazard scale closely when monthly hazards are small)

The demo simulates a subscription base where a price increase temporarily
lifts the hazard, support tickets lift it, and engagement suppresses it,
then checks both estimators against the true coefficients and calibrates
the discrete-time model on held-out person-months.

Prediction warning: any forecast past next month requires an assumed
covariate path (will engagement stay at its last value?). The honest
short-horizon product is next-month risk from last observed covariates.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from lifelines import CoxTimeVaryingFitter
from sklearn.linear_model import LogisticRegression

TRUE = dict(price_increase=0.9, tickets=0.35, engagement=-1.8, premium=-0.5)
BASE_LOGIT = -3.2  # ~4% monthly hazard at engagement 0.5, no events


def simulate_panel(n: int, rng: np.random.Generator,
                   max_months: int = 36) -> pd.DataFrame:
    """Person-month panel. Each row: one customer-month at risk."""
    rows = []
    for cid in range(n):
        premium = int(rng.random() < 0.3)
        window = int(rng.integers(6, max_months + 1))  # staggered joins
        pi_month = int(rng.integers(4, 30)) if rng.random() < 0.4 else -99
        engagement = float(np.clip(rng.normal(0.55, 0.2), 0, 1))
        for m in range(1, window + 1):
            engagement = float(np.clip(
                0.85 * engagement + 0.15 * rng.normal(0.5, 0.25), 0, 1))
            tickets = int(rng.poisson(0.4))
            price_increase = int(m in (pi_month, pi_month + 1))
            logit = (BASE_LOGIT
                     + TRUE["price_increase"] * price_increase
                     + TRUE["tickets"] * tickets
                     + TRUE["engagement"] * engagement
                     + TRUE["premium"] * premium)
            event = int(rng.random() < 1 / (1 + np.exp(-logit)))
            rows.append((cid, m - 1, m, event, price_increase, tickets,
                         engagement, premium))
            if event:
                break
    return pd.DataFrame(rows, columns=[
        "id", "start", "stop", "event",
        "price_increase", "tickets", "engagement", "premium"])


if __name__ == "__main__":
    rng = np.random.default_rng(3)
    panel = simulate_panel(3000, rng)
    n_events = panel.event.sum()
    print(f"panel: {panel.id.nunique()} customers, {len(panel)} person-months, "
          f"{n_events} churn events ({panel.event.mean():.1%} monthly hazard)")

    covs = ["price_increase", "tickets", "engagement", "premium"]

    # 1. Cox with time-varying covariates.
    ctv = CoxTimeVaryingFitter(penalizer=0.0)
    ctv.fit(panel, id_col="id", event_col="event",
            start_col="start", stop_col="stop", show_progress=False)
    print(f"\n{'covariate':<16} {'true':>6} {'cox':>7} {'logit':>7}")

    # 2. Discrete-time hazard: person-period logistic with tenure buckets.
    train_ids = rng.random(panel.id.nunique()) < 0.7
    tr = panel[train_ids[panel.id]]
    te = panel[~train_ids[panel.id]]
    buckets = pd.get_dummies(pd.cut(panel.stop, [0, 3, 6, 12, 24, 36]),
                             prefix="tenure", dtype=float)
    X = pd.concat([panel[covs], buckets], axis=1)
    lr = LogisticRegression(C=1e6, max_iter=2000)
    lr.fit(X[train_ids[panel.id]], tr.event)

    for i, c in enumerate(covs):
        print(f"{c:<16} {TRUE[c]:>6.2f} {ctv.params_[c]:>7.2f} "
              f"{lr.coef_[0][i]:>7.2f}")

    # Calibration on held-out person-months, by predicted-hazard decile.
    p = lr.predict_proba(X[~train_ids[panel.id]])[:, 1]
    cal = (pd.DataFrame({"p": p, "y": te.event.to_numpy()})
           .assign(decile=lambda d: pd.qcut(d.p, 10, labels=False,
                                            duplicates="drop"))
           .groupby("decile").agg(predicted=("p", "mean"),
                                  observed=("y", "mean"),
                                  n=("y", "size")))
    print("\nheld-out calibration by predicted-hazard decile")
    print(cal.round(3).to_string())
    top = cal.iloc[-1]
    print(f"\ntop decile: predicted {top.predicted:.3f}, observed "
          f"{top.observed:.3f}, lift {top.observed / te.event.mean():.1f}x "
          f"over the base rate {te.event.mean():.3f}")
