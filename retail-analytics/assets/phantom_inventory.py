#!/usr/bin/env python3
"""Phantom-inventory detector: negative-binomial likelihood ratio on zero-sales runs.

pip install numpy pandas

The system believes on-hand > 0, yet the shelf is empty (shrink, receiving
error, unrecorded damage), so POS shows a run of zero-sales days while
auto-replenishment stays asleep. The detector asks, for each store-item's
trailing run of zero-sales days: how surprising is this run under the item's
own demand model?

Model. Daily demand is negative binomial with day-of-week mean mu_t and
common dispersion k (Var = mu + mu^2/k). Under H0 (in stock, record correct)
the probability of a zero-sales day is p0(t) = (k/(k+mu_t))^k. Under H1
(phantom: shelf empty) observed sales are zero with probability 1.

    LLR(run) = -sum_t ln p0(t)
    P(phantom | run) = pi / (pi + (1-pi) * exp(-LLR))

with pi the prior that any given trailing zero run is a phantom event.
Demand parameters are fit on history BEFORE the run starts; fitting on the
full history drags mu toward zero and blinds the test.

Audit targeting. A flag is worth auditing when
    P(phantom) * mu_bar * price * margin * horizon_days > audit_cost,
where horizon_days is how long the error would otherwise persist (time to
the next scheduled count). Store labour caps counts per day, so rank flags
by expected recovered margin and take the top k.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RNG = np.random.default_rng(7)


def nb_zero_prob(mu: np.ndarray, k: float) -> np.ndarray:
    """P(D=0) for NB with mean mu, dispersion k. Poisson limit as k -> inf."""
    mu = np.asarray(mu, dtype=float)
    return (k / (k + mu)) ** k


def fit_nb_dow(sales: np.ndarray) -> tuple[np.ndarray, float]:
    """Day-of-week means and pooled dispersion via method of moments.

    sales: 1-D daily units, day 0 taken as Monday. Returns (mu_dow[7], k).
    Moment estimator for common alpha = 1/k with varying means:
        alpha_hat = sum((x-mu)^2 - mu) / sum(mu^2).
    """
    sales = np.asarray(sales, dtype=float)
    days = np.arange(len(sales)) % 7
    mu_dow = np.array([max(sales[days == d].mean(), 1e-3) for d in range(7)])
    mu_t = mu_dow[days]
    denom = float((mu_t**2).sum())
    alpha = float(((sales - mu_t) ** 2 - mu_t).sum()) / max(denom, 1e-9)
    alpha = float(np.clip(alpha, 1e-6, 10.0))
    return mu_dow, 1.0 / alpha


def trailing_zero_run(sales: np.ndarray) -> int:
    """Length of the zero-sales run ending at the last observed day."""
    n = 0
    for x in sales[::-1]:
        if x != 0:
            break
        n += 1
    return n


def phantom_posterior(sales: np.ndarray, prior: float = 0.05,
                      min_history: int = 28) -> dict:
    """Score one store-item's trailing zero run. Returns diagnostics dict."""
    run = trailing_zero_run(sales)
    if run == 0 or len(sales) - run < min_history:
        return {"run_days": run, "llr": 0.0, "posterior": 0.0, "mu_bar": np.nan}
    hist = sales[: len(sales) - run]          # fit strictly before the run
    mu_dow, k = fit_nb_dow(hist)
    run_days = (np.arange(len(sales) - run, len(sales))) % 7
    p0 = nb_zero_prob(mu_dow[run_days], k)
    llr = float(-np.log(p0).sum())
    post = prior / (prior + (1 - prior) * np.exp(-min(llr, 500.0)))
    return {"run_days": run, "llr": llr, "posterior": float(post),
            "mu_bar": float(mu_dow.mean()), "k": k}


def rank_audits(flags: pd.DataFrame, horizon_days: float = 14.0,
                audit_cost: float = 1.50, capacity: int = 15) -> pd.DataFrame:
    """Rank flagged store-items by expected recovered margin; keep top capacity.

    flags needs columns: posterior, mu_bar, price, margin_rate.
    """
    f = flags.copy()
    f["exp_recovery"] = (f["posterior"] * f["mu_bar"] * f["price"]
                         * f["margin_rate"] * horizon_days)
    f["worth_it"] = f["exp_recovery"] > audit_cost
    f = f.sort_values("exp_recovery", ascending=False)
    f["audited"] = False
    f.iloc[:capacity, f.columns.get_loc("audited")] = True
    return f


# ---------------------------------------------------------------- demo ----

def _simulate_panel(n_items: int = 200, n_days: int = 120,
                    phantom_rate: float = 0.08) -> pd.DataFrame:
    """Store-item daily sales with injected phantom events.

    True demand is NB with item-level mu in [0.3, 6] and a weekend lift.
    A phantom event zeroes true availability from a random onset day onward
    while the system record stays positive.
    """
    rows = []
    dow_lift = np.array([0.9, 0.9, 0.95, 1.0, 1.1, 1.3, 1.15])
    for i in range(n_items):
        mu_base = float(np.exp(RNG.uniform(np.log(0.3), np.log(6.0))))
        k = float(RNG.uniform(0.8, 3.0))
        days = np.arange(n_days)
        mu_t = mu_base * dow_lift[days % 7]
        demand = RNG.negative_binomial(k, k / (k + mu_t))
        is_phantom = RNG.random() < phantom_rate
        onset = int(RNG.integers(n_days - 30, n_days - 2)) if is_phantom else n_days
        sales = demand.copy()
        sales[onset:] = 0
        rows.append({
            "item": i, "sales": sales, "mu_true": mu_base,
            "is_phantom": is_phantom, "onset": onset,
            "price": float(RNG.uniform(1.5, 12.0)),
            "margin_rate": float(RNG.uniform(0.22, 0.38)),
        })
    return pd.DataFrame(rows)


def _demo() -> None:
    panel = _simulate_panel()
    scored = []
    for _, r in panel.iterrows():
        s = phantom_posterior(r["sales"])
        s.update(item=r["item"], is_phantom=r["is_phantom"],
                 price=r["price"], margin_rate=r["margin_rate"])
        scored.append(s)
    df = pd.DataFrame(scored).dropna(subset=["mu_bar"])

    flagged = df[df["posterior"] > 0.5]
    tp = int((flagged["is_phantom"]).sum())
    n_phantom = int(df["is_phantom"].sum())
    print(f"items scored: {len(df)}   true phantoms: {n_phantom}")
    print(f"posterior>0.5 flags: {len(flagged)}   true positives: {tp}")
    print(f"precision: {tp / max(len(flagged), 1):.2f}   "
          f"recall: {tp / max(n_phantom, 1):.2f}")

    ranked = rank_audits(df[df["posterior"] > 0.2])
    audited = ranked[ranked["audited"]]
    p_at_k = audited["is_phantom"].mean() if len(audited) else 0.0
    print(f"\naudit list (capacity 15): precision@15 = {p_at_k:.2f}")
    cols = ["item", "run_days", "llr", "posterior", "exp_recovery",
            "is_phantom"]
    print(audited[cols].to_string(index=False,
                                  float_format=lambda x: f"{x:.2f}"))

    # detection latency: zero-sales days needed before posterior crosses 0.5,
    # i.e. cumulative -ln p0 exceeds ln((1-prior)/prior)
    thresh = np.log((1 - 0.05) / 0.05)
    hits = df[df["is_phantom"] & (df["posterior"] > 0.5)].copy()
    if len(hits):
        p0 = (hits["k"] / (hits["k"] + hits["mu_bar"])) ** hits["k"]
        hits["days_to_flag"] = np.ceil(thresh / -np.log(p0))
        fast = hits.loc[hits["mu_bar"] >= 2.0, "days_to_flag"]
        slow = hits.loc[hits["mu_bar"] < 2.0, "days_to_flag"]
        print(f"\nzero-days needed to flag (posterior 0.5): "
              f"fast movers {fast.median():.0f} d, "
              f"slow movers {slow.median():.0f} d")


if __name__ == "__main__":
    _demo()
