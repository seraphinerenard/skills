#!/usr/bin/env python3
# pip install numpy pandas scikit-learn
"""Uplift modelling for retention targeting, with Qini evaluation from scratch.

Builds three rankings of who to contact with a retention offer:
    1. churn-risk ranking (the default most teams reach for first)
    2. T-learner uplift (two models: treated and control)
    3. transformed-outcome uplift (single regression on Y* = Y(W-e)/(e(1-e)))

and scores each with a Qini curve computed directly from the definition, so
the numbers do not depend on any library's normalization choice. The demo
population contains the four canonical response types (sure things,
persuadables, lost causes, sleeping dogs), so the churn-risk ranking loses
to uplift by construction of the world, which mirrors published retention
results (Ascarza 2018).

Outcome convention: Y = 1 means the customer was retained. Positive uplift
means the offer raises retention.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor


# ----------------------------------------------------------------------
# Synthetic retention campaign
# ----------------------------------------------------------------------

def simulate_campaign(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Randomized retention offer over a base of subscription customers.

    True treatment effects on retention (percentage points):
        persuadables   (mid risk, engaged)          +10
        sleeping dogs  (price sensitive, dormant)    -6
        everyone else                                 ~0
    """
    tenure = rng.integers(1, 60, n)
    spend = rng.gamma(4, 15, n)
    tickets = rng.poisson(0.6, n)
    engagement = np.clip(rng.normal(0.5, 0.22, n), 0, 1)
    price_sensitive = (rng.random(n) < 0.25).astype(int)

    logit = (-0.4 - 0.02 * tenure + 0.5 * tickets - 2.2 * engagement
             + 0.35 * price_sensitive + 0.004 * spend)
    p_churn = 1 / (1 + np.exp(-logit))

    persuadable = (p_churn > 0.15) & (p_churn < 0.45) & (engagement > 0.45)
    sleeping_dog = (price_sensitive == 1) & (engagement < 0.30)
    effect = np.where(persuadable, 0.10, 0.0)
    effect = np.where(sleeping_dog, -0.06, effect)

    w = (rng.random(n) < 0.5).astype(int)
    p_churn_treated = np.clip(p_churn - effect, 0.01, 0.99)
    p = np.where(w == 1, p_churn_treated, p_churn)
    y = (rng.random(n) >= p).astype(int)  # 1 = retained

    return pd.DataFrame(dict(
        tenure=tenure, spend=spend, tickets=tickets, engagement=engagement,
        price_sensitive=price_sensitive, w=w, y=y, true_uplift=effect,
    ))


# ----------------------------------------------------------------------
# Qini evaluation, from the definition
# ----------------------------------------------------------------------

def qini_curve(y, w, scores):
    """Radcliffe Qini: sort by score desc; at each prefix of size k,
    Q(k) = Y_T(k) - Y_C(k) * n_T(k) / n_C(k)  (incremental retained
    customers among the k targeted, control-scaled). Returns (frac, Q)."""
    order = np.argsort(-np.asarray(scores))
    y = np.asarray(y)[order]
    w = np.asarray(w)[order]
    n_t = np.cumsum(w)
    n_c = np.cumsum(1 - w)
    y_t = np.cumsum(y * w)
    y_c = np.cumsum(y * (1 - w))
    with np.errstate(divide="ignore", invalid="ignore"):
        q = y_t - np.where(n_c > 0, y_c * n_t / n_c, 0.0)
    frac = np.arange(1, len(y) + 1) / len(y)
    return frac, q


def qini_coefficient(y, w, scores) -> float:
    """Area between the Qini curve and the random-targeting diagonal,
    per customer. Libraries normalize this differently (causalml and
    sklift disagree); comparing rankings on the same dataset with the
    same formula is the only safe use."""
    frac, q = qini_curve(y, w, scores)
    random_line = frac * q[-1]
    return float(np.trapezoid(q - random_line, frac) / len(y))


def uplift_at_k(y, w, scores, k: float) -> float:
    """Observed uplift (retention-rate difference, T minus C) inside the
    top k fraction by score."""
    order = np.argsort(-np.asarray(scores))
    top = order[: int(len(y) * k)]
    y, w = np.asarray(y)[top], np.asarray(w)[top]
    return y[w == 1].mean() - y[w == 0].mean()


def incremental_saves_per_10k(y, w, scores, k: float) -> float:
    return 10_000 * uplift_at_k(y, w, scores, k)


# ----------------------------------------------------------------------
# Sample-size reality for uplift
# ----------------------------------------------------------------------

def n_per_cell_for_effect_difference(p_base: float, delta: float,
                                     alpha: float = 0.05,
                                     power: float = 0.80) -> int:
    """Customers per cell (2 segments x T/C = 4 cells) to detect a
    difference `delta` between two segments' treatment effects.
    The contrast is a difference of differences of proportions, so its
    variance sums four binomial terms; p_base approximates all four."""
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    var_unit = 4 * p_base * (1 - p_base)
    return int(np.ceil(z**2 * var_unit / delta**2))


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------

if __name__ == "__main__":
    rng = np.random.default_rng(11)
    df = simulate_campaign(60_000, rng)
    feats = ["tenure", "spend", "tickets", "engagement", "price_sensitive"]
    train, test = df.iloc[:40_000], df.iloc[40_000:]
    print(f"train {len(train)}, holdout {len(test)}; "
          f"control churn {1 - train.loc[train.w == 0, 'y'].mean():.1%}; "
          f"ATE on retention "
          f"{train.loc[train.w == 1, 'y'].mean() - train.loc[train.w == 0, 'y'].mean():+.3f}")

    gbm = dict(n_estimators=200, max_depth=3, learning_rate=0.05)

    # 1. churn-risk ranking: risk model on the control arm only.
    risk = GradientBoostingClassifier(**gbm, random_state=0)
    ctrl = train[train.w == 0]
    risk.fit(ctrl[feats], 1 - ctrl.y)
    churn_risk = risk.predict_proba(test[feats])[:, 1]

    # 2. T-learner.
    m1 = GradientBoostingClassifier(**gbm, random_state=0)
    m0 = GradientBoostingClassifier(**gbm, random_state=0)
    m1.fit(train.loc[train.w == 1, feats], train.loc[train.w == 1, "y"])
    m0.fit(train.loc[train.w == 0, feats], train.loc[train.w == 0, "y"])
    t_uplift = (m1.predict_proba(test[feats])[:, 1]
                - m0.predict_proba(test[feats])[:, 1])

    # 3. transformed outcome: e = 0.5 by design, Y* = 2Y(2W - 1).
    y_star = 2 * train.y * (2 * train.w - 1)
    to = GradientBoostingRegressor(**gbm, random_state=0)
    to.fit(train[feats], y_star)
    to_uplift = to.predict(test[feats])

    rankings = {
        "churn risk (descending)": churn_risk,
        "T-learner uplift": t_uplift,
        "transformed-outcome uplift": to_uplift,
        "true uplift (oracle bound)": test.true_uplift.to_numpy(),
    }
    print(f"\n{'ranking':<28} {'Qini/cust':>10} {'uplift@30%':>11} "
          f"{'saves/10k contacted':>20}")
    for name, s in rankings.items():
        qc = qini_coefficient(test.y, test.w, s)
        u30 = uplift_at_k(test.y, test.w, s, 0.30)
        print(f"{name:<28} {qc:>10.4f} {u30:>+11.3f} "
              f"{incremental_saves_per_10k(test.y, test.w, s, 0.30):>20.0f}")

    ate = test.loc[test.w == 1, "y"].mean() - test.loc[test.w == 0, "y"].mean()
    print(f"\nblanket campaign (everyone): {10_000 * ate:.0f} saves/10k contacted")

    n = n_per_cell_for_effect_difference(p_base=0.25, delta=0.02)
    print(f"\npower check: separating two segments whose true effects differ "
          f"by 2pp\n(base churn 25%) needs {n:,} customers per cell, "
          f"{4 * n:,} in the experiment.")
