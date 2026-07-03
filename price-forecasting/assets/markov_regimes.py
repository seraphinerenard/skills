"""Markov regime switching on commodity returns, with a stability audit.

pip install numpy pandas statsmodels
Tested with statsmodels 0.14.6, numpy 2.5, pandas 3.0.

MarkovRegression fits by maximum likelihood from multiple random starts
(search_reps); the likelihood surface has local optima and single-start fits
are unreliable. Two habits this module bakes in:

  1. Label alignment. Regime numbering is arbitrary across fits, so every
     comparison first sorts regimes by fitted variance.
  2. A refit-stability audit. Fit on the first half, fit on the full sample,
     and compare transition probabilities and regime parameters. Markov
     switching describes history well and extrapolates poorly; the audit
     quantifies how much the story moves when the sample changes, which is
     the number a client decision should depend on.

Expected regime duration = 1 / (1 - p_stay). A calm regime with
p_stay = 0.98 lasts 50 days on average; a spike regime with p_stay = 0.80
lasts 5. Report durations, they read better than transition matrices.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression


def simulate_regimes(n: int, rng: np.random.Generator):
    """Two-regime daily returns: calm (mu 0, sd 1%) and stress (mu +0.5%, sd 4%).

    True transition: p(calm->calm) = 0.98, p(stress->stress) = 0.90.
    Returns (returns, true_states).
    """
    p_stay = np.array([0.98, 0.90])
    mu = np.array([0.000, 0.005])
    sd = np.array([0.010, 0.040])
    states = np.empty(n, dtype=int)
    states[0] = 0
    u = rng.random(n)
    for t in range(1, n):
        s = states[t - 1]
        states[t] = s if u[t] < p_stay[s] else 1 - s
    rets = rng.normal(mu[states], sd[states])
    return pd.Series(rets, index=pd.bdate_range("2021-01-04", periods=n)), states


def fit_switching(returns: pd.Series, k: int = 2, search_reps: int = 30,
                  seed: int = 0):
    """Fit a k-regime switching-mean, switching-variance model."""
    np.random.seed(seed)  # search_reps draws random starts from numpy global state
    mod = MarkovRegression(returns, k_regimes=k, trend="c",
                           switching_variance=True)
    return mod.fit(search_reps=search_reps)


def regime_order(res, k: int = 2) -> np.ndarray:
    """Regime indices sorted by fitted variance (calm first)."""
    sig2 = np.array([res.params[f"sigma2[{i}]"] for i in range(k)])
    return np.argsort(sig2)


def summarize(res, k: int = 2) -> pd.DataFrame:
    order = regime_order(res, k)
    rows = []
    for rank, i in enumerate(order):
        rows.append({
            "regime": "calm" if rank == 0 else f"stress{rank}" if k > 2 else "stress",
            "mean": res.params[f"const[{i}]"],
            "sd": np.sqrt(res.params[f"sigma2[{i}]"]),
            "expected_duration_days": res.expected_durations[i],
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    rng = np.random.default_rng(11)
    returns, true_states = simulate_regimes(1000, rng)

    res = fit_switching(returns)
    print("=== Full-sample fit (n = 1000) ===")
    print(summarize(res).round(4).to_string(index=False))
    print("true: calm (mean 0.0000, sd 0.0100, duration 50); "
          "stress (mean 0.0050, sd 0.0400, duration 10)")

    order = regime_order(res)
    stress_prob = res.smoothed_marginal_probabilities[order[1]]
    classified = (stress_prob > 0.5).astype(int)
    acc = float((classified.to_numpy() == true_states).mean())
    print(f"smoothed-probability state recovery: {acc:.1%}")

    print("\n=== Refit-stability audit ===")
    res_half = fit_switching(returns.iloc[:500], seed=1)
    full = summarize(res).set_index("regime")
    half = summarize(res_half).set_index("regime")
    cmp = full.join(half, lsuffix="_full", rsuffix="_half").round(4)
    print(cmp.to_string())
    dur_shift = (full["expected_duration_days"] - half["expected_duration_days"]).abs()
    print(f"max duration shift between fits: {dur_shift.max():.1f} days")
    print("If durations or variances move materially between the half and "
          "full fits, present the regimes as descriptive history and keep "
          "them out of the point forecast.")
