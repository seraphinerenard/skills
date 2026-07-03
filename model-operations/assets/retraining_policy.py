"""Retraining-policy backtester: replay calendar and trigger policies over a
synthetic drifting process and price them in dollars, with label delay
modelled, because label delay is what breaks most trigger designs.

pip install: numpy pandas

What the simulation encodes:
- The relationship drifts two ways: a slow coefficient random walk (the normal
  case) and an optional abrupt break (supplier change, price rule change,
  pandemic). Policies rank differently under the two, which is why a policy
  chosen on vibes fails: backtest the policy on YOUR history, on both regimes
  if both occur in it.
- Labels arrive `label_delay` days late. Every policy (calendar and trigger)
  trains and evaluates its trigger on labels available at decision time, so
  after a break, even a perfect trigger reacts no sooner than the delay, and
  the model retrains on a window that still mixes pre-break rows.
- Economics: total cost = n_retrains * retrain_cost + sum over days of
  (MAE_day * rows_day * error_cost_per_unit). Retrain cost covers the human
  loop (validation, sign-off, deploy), which for consulting-delivered models
  dominates compute; $500 to $5,000 per cycle is the range seen when a client
  data team runs a documented playbook.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class World:
    n_days: int = 540
    rows_per_day: int = 200
    n_features: int = 5
    noise_sd: float = 1.0
    walk_sd: float = 0.004      # daily sd of each coefficient's random walk
    break_day: int | None = None
    break_shift: float = 1.0    # added to coefficient 0 at the break
    label_delay: int = 21
    seed: int = 3


def simulate(w: World):
    """Returns (X[day][row, feat], y[day][row], beta[day, feat])."""
    rng = np.random.default_rng(w.seed)
    beta = np.zeros((w.n_days, w.n_features))
    beta[0] = rng.normal(1.0, 0.3, w.n_features)
    steps = rng.normal(0, w.walk_sd, (w.n_days - 1, w.n_features))
    beta[1:] = beta[0] + np.cumsum(steps, axis=0)
    if w.break_day is not None:
        beta[w.break_day:, 0] += w.break_shift
    X = [rng.normal(0, 1, (w.rows_per_day, w.n_features)) for _ in range(w.n_days)]
    y = [X[t] @ beta[t] + rng.normal(0, w.noise_sd, w.rows_per_day)
         for t in range(w.n_days)]
    return X, y, beta


def _fit(X, y, upto_day, window, delay):
    """OLS on the trailing `window` days of LABELLED data at decision day."""
    last = upto_day - delay          # newest day whose labels have arrived
    first = max(0, last - window)
    if last <= first:
        return None
    Xw = np.vstack(X[first:last])
    yw = np.concatenate(y[first:last])
    coef, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
    return coef


def backtest_policy(w: World, policy: str, every: int = 30,
                    trigger_ratio: float = 1.25, window: int = 90,
                    warmup: int = 120, retrain_cost: float = 1_500.0,
                    error_cost_per_unit: float = 2.0) -> dict:
    """policy: 'never' | 'calendar' (retrain each `every` days) | 'trigger'
    (retrain when trailing-14d labelled MAE > trigger_ratio x the baseline
    MAE anchored in the first healthy window). Two trigger rules that matter:
    the anchor is NEVER reset to a post-incident error level, because
    re-anchoring to a sick baseline silences the trigger exactly when the
    model is still broken; and retrains observe a cooldown of
    label_delay + 14 days, so the trigger scores the NEW model's labelled
    errors before it is allowed to fire again."""
    X, y, _ = simulate(w)
    coef = _fit(X, y, warmup, window, w.label_delay)
    baseline_mae = None
    cooldown = w.label_delay + 14
    last_retrain = -10**9
    daily_mae = np.zeros(w.n_days)
    n_retrains, retrain_days = 0, []
    for t in range(warmup, w.n_days):
        daily_mae[t] = float(np.mean(np.abs(X[t] @ coef - y[t])))
        # Decision uses labelled days only: [t-delay-14, t-delay).
        lab_end = t - w.label_delay
        lab_mae = float(np.mean(daily_mae[max(warmup, lab_end - 14):lab_end])) \
            if lab_end - 14 >= warmup else None
        if baseline_mae is None and lab_mae is not None:
            baseline_mae = lab_mae   # anchored once, in the healthy period
        do = (policy == "calendar" and (t - warmup) % every == 0 and t > warmup) or \
             (policy == "trigger" and lab_mae is not None
              and baseline_mae is not None
              and lab_mae > trigger_ratio * baseline_mae
              and t - last_retrain > cooldown)
        if do:
            new = _fit(X, y, t, window, w.label_delay)
            if new is not None:
                coef, n_retrains = new, n_retrains + 1
                retrain_days.append(t)
                last_retrain = t
    scored = slice(warmup, w.n_days)
    mae = float(np.mean(daily_mae[scored]))
    err_cost = float(np.sum(daily_mae[scored]) * w.rows_per_day
                     * error_cost_per_unit)
    return {"policy": policy if policy != "calendar" else f"calendar/{every}d",
            "retrains": n_retrains, "avg_mae": round(mae, 4),
            "error_cost": round(err_cost, -2),
            "retrain_cost": n_retrains * retrain_cost,
            "total_cost": round(err_cost + n_retrains * retrain_cost, -2)}


def compare(w: World, label: str) -> pd.DataFrame:
    rows = [backtest_policy(w, "never"),
            backtest_policy(w, "calendar", every=7),
            backtest_policy(w, "calendar", every=30),
            backtest_policy(w, "calendar", every=90),
            backtest_policy(w, "trigger")]
    out = pd.DataFrame(rows)
    out.insert(0, "world", label)
    return out


if __name__ == "__main__":
    pd.set_option("display.width", 130)
    slow = World()                                   # random walk only
    broken = World(break_day=330, break_shift=1.0)   # walk + abrupt break

    print("Slow-drift world (coefficient random walk, no break), 420 scored "
          "days, 200 rows/day, $2 per unit of absolute error, $1,500 per "
          "retrain, labels 21 days late")
    a = compare(slow, "slow drift")
    print(a.to_string(index=False))
    print()
    print("Same world plus an abrupt break at day 330")
    b = compare(broken, "with break")
    print(b.to_string(index=False))
    print()
    wk = a.loc[a.policy == "calendar/7d", "total_cost"].iloc[0]
    mo = a.loc[a.policy == "calendar/30d", "total_cost"].iloc[0]
    print(f"Slow drift: weekly total ${wk:,.0f} vs monthly ${mo:,.0f}; the "
          f"extra {int(a.loc[a.policy=='calendar/7d','retrains'].iloc[0] - a.loc[a.policy=='calendar/30d','retrains'].iloc[0])} "
          f"retrains bought ~{(a.loc[a.policy=='calendar/30d','avg_mae'].iloc[0] - a.loc[a.policy=='calendar/7d','avg_mae'].iloc[0]):.4f} MAE.")
    print("With a break: 'never' and long calendars bleed until the next "
          "cycle; the trigger pays for its extra retrains, and its reaction "
          "floor is the 21-day label delay, visible in avg_mae.")
