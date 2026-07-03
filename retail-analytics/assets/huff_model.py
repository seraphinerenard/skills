#!/usr/bin/env python3
"""Huff gravity model for site selection, with own-banner cannibalization.

pip install numpy pandas

Huff (1963): the probability that a shopper in zone i patronizes store j is

    P_ij = A_j^alpha * d_ij^(-beta) / sum_l A_l^alpha * d_il^(-beta)

with A_j store attractiveness (floor area as the default proxy), d_ij
travel distance or time, alpha and beta calibrated. Expected store revenue
is sum_i w_i * P_ij with w_i the zone's category spend.

Two properties drive how consultants should use it:
  * Huff reallocates a FIXED demand pool. A candidate site's projected
    revenue is always partly taken from every existing store, including
    your own. The decision number is net-new revenue after subtracting
    own-banner cannibalization; the gross projection flatters every site.
  * beta is the load-bearing parameter and it is category-specific
    (convenience trips decay fast, destination trips slowly). Calibrate on
    observed revenues or loyalty-card trade areas; a copied textbook beta
    silently sets every trade-area boundary.

Calibration here is a grid search over (alpha, beta) against observed store
revenues, which keeps the objective visible. With loyalty-card zone-store
flows, fit a conditional logit instead; the Huff model is that logit with
log attractiveness and log distance as its only covariates.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RNG = np.random.default_rng(21)


def huff_probabilities(attr: np.ndarray, dist: np.ndarray,
                       alpha: float, beta: float) -> np.ndarray:
    """attr: (n_stores,), dist: (n_zones, n_stores) -> P (n_zones, n_stores)."""
    u = (attr[None, :] ** alpha) * (np.maximum(dist, 0.05) ** -beta)
    return u / u.sum(axis=1, keepdims=True)


def expected_revenue(attr: np.ndarray, dist: np.ndarray, spend: np.ndarray,
                     alpha: float, beta: float) -> np.ndarray:
    P = huff_probabilities(attr, dist, alpha, beta)
    return spend @ P


def calibrate(attr: np.ndarray, dist: np.ndarray, spend: np.ndarray,
              observed_rev: np.ndarray, alpha: float = 1.0,
              betas=np.linspace(0.5, 4.0, 71)) -> tuple[float, float]:
    """Grid-search beta minimizing squared log revenue error, alpha fixed.

    A handful of store revenues identifies alpha and beta only jointly
    (bigger stores farther apart fit as well as smaller stores closer), so
    revenue-only calibration fixes alpha = 1 by convention. Zone-to-store
    flows from loyalty cards identify both; fit the conditional logit then.
    """
    best_b, best_err = 2.0, np.inf
    for b in betas:
        rev = expected_revenue(attr, dist, spend, alpha, b)
        err = float(((np.log(rev) - np.log(observed_rev)) ** 2).sum())
        if err < best_err:
            best_b, best_err = float(b), err
    return alpha, best_b


def evaluate_candidate(attr: np.ndarray, dist: np.ndarray, spend: np.ndarray,
                       own: np.ndarray, cand_attr: float,
                       cand_dist: np.ndarray, alpha: float,
                       beta: float) -> dict:
    """Candidate site impact: gross revenue, source split, net-new revenue.

    own: boolean mask of own-banner stores among existing stores.
    cand_dist: (n_zones,) distances from zones to the candidate.
    """
    rev_before = expected_revenue(attr, dist, spend, alpha, beta)
    attr2 = np.append(attr, cand_attr)
    dist2 = np.column_stack([dist, cand_dist])
    rev_after = expected_revenue(attr2, dist2, spend, alpha, beta)

    cand_rev = float(rev_after[-1])
    delta = rev_after[:-1] - rev_before          # all negative in Huff
    from_own = float(-delta[own].sum())
    from_comp = float(-delta[~own].sum())
    return {
        "candidate_revenue": cand_rev,
        "from_own_stores": from_own,
        "from_competitors": from_comp,
        "cannibalization_rate": from_own / cand_rev,
        "net_new_revenue": cand_rev - from_own,
        "own_store_deltas": delta[own],
    }


# ---------------------------------------------------------------- demo ----

def _demo() -> None:
    # 40 demand zones on a 15x15 km area, spend proportional to population,
    # concentrated around a town centre at (4, 5) inside the own cluster
    zones = RNG.uniform(0, 15, size=(40, 2))
    spend = RNG.lognormal(mean=np.log(2.0e6), sigma=0.5, size=40)
    centre_dist = np.linalg.norm(zones - np.array([4.0, 5.0]), axis=1)
    spend = spend * (1 + 3.5 * np.exp(-centre_dist / 3.0))

    # 6 stores: own banner clustered southwest, competitors northeast
    stores = np.array([[3.0, 3.0], [6.0, 5.0], [4.0, 9.0],
                       [11.0, 11.0], [13.0, 7.0], [9.0, 13.0]])
    own = np.array([True, True, True, False, False, False])
    attr = np.array([35, 45, 30, 55, 40, 25], dtype=float)  # k sq ft

    dist = np.linalg.norm(zones[:, None, :] - stores[None, :, :], axis=2)

    # synthetic truth: alpha=1.0, beta=2.5, observed with 5% noise
    true_rev = expected_revenue(attr, dist, spend, 1.0, 2.5)
    observed = true_rev * RNG.lognormal(0, 0.05, len(true_rev))

    alpha, beta = calibrate(attr, dist, spend, observed)
    print(f"calibrated beta = {beta:.2f} (true 2.50), alpha fixed at "
          f"{alpha:.2f}")

    # A sits inside the own-banner cluster; B sits in competitor territory
    candidates = {"A (near own stores)": np.array([4.0, 5.5]),
                  "B (competitor turf)": np.array([13.5, 11.5])}
    rows = []
    for name, xy in candidates.items():
        cd = np.linalg.norm(zones - xy[None, :], axis=1)
        r = evaluate_candidate(attr, dist, spend, own, 40.0, cd, alpha, beta)
        rows.append({"candidate": name,
                     "gross $M": r["candidate_revenue"] / 1e6,
                     "from own $M": r["from_own_stores"] / 1e6,
                     "from comp $M": r["from_competitors"] / 1e6,
                     "cannibal %": 100 * r["cannibalization_rate"],
                     "net new $M": r["net_new_revenue"] / 1e6})
    out = pd.DataFrame(rows)
    print(out.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    g = out.loc[out["gross $M"].idxmax(), "candidate"]
    n = out.loc[out["net new $M"].idxmax(), "candidate"]
    print(f"\ngross revenue picks {g}; net-new revenue picks {n}.")


if __name__ == "__main__":
    _demo()
