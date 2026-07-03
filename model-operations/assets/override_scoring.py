"""Judgmental-override scoring: turn an override log into a quarterly
scorecard by owner, direction, and size, in the layout the override
literature says matters (Fildes et al. 2009: large and downward adjustments
tend to help, small and upward ones tend to hurt).

pip install: numpy pandas

Log schema (one row per series-period where a human touched the number):
    date, series, owner, reason, stat, final, actual
Rows where final == stat cost nothing to keep and give the denominator for
the adjustment rate, so log every series-period, touched or untouched.

Scoring definitions:
- improvement = |stat - actual| - |final - actual|; positive means the
  override moved the number toward the actual.
- Aggregation uses value-weighted points: sum(improvement) / sum(actual),
  reported in percentage points of WAPE. Averaging per-row percentage
  improvements lets one near-zero actual dominate the quarter.
- hit_rate is the share of overrides with improvement > 0. Report it next to
  net points: a 55% hit rate with negative net points means many small wins
  and a few catastrophic misses, a pattern worth naming in the review.
- size splits at 10% relative change by default; direction is the sign of
  final - stat. The 2x2 direction-by-size table is the single most useful
  artifact in a quarterly override review because owners recognize their own
  habits in it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SIZE_SPLIT = 0.10


def _prep(log: pd.DataFrame, size_split: float) -> pd.DataFrame:
    d = log.copy()
    d["overridden"] = d["final"] != d["stat"]
    d["improvement"] = (d["stat"] - d["actual"]).abs() - (d["final"] - d["actual"]).abs()
    rel = (d["final"] - d["stat"]) / d["stat"].replace(0, np.nan)
    d["direction"] = np.where(rel > 0, "up", "down")
    d["size"] = np.where(rel.abs() > size_split, "large", "small")
    return d


def _score(grp: pd.DataFrame) -> pd.Series:
    ov = grp[grp["overridden"]]
    return pd.Series({
        "n_periods": int(len(grp)),
        "n_overrides": int(len(ov)),
        "adjust_rate_pct": round(100 * len(ov) / len(grp), 1) if len(grp) else np.nan,
        "hit_rate_pct": round(100 * float((ov["improvement"] > 0).mean()), 1)
        if len(ov) else np.nan,
        "net_wape_pp": round(100 * ov["improvement"].sum() / grp["actual"].sum(), 2)
        if len(ov) else 0.0,
    })


def owner_scorecard(log: pd.DataFrame, size_split: float = SIZE_SPLIT) -> pd.DataFrame:
    """One row per owner: adjustment rate, hit rate, net WAPE points."""
    d = _prep(log, size_split)
    return (d.groupby("owner", observed=True).apply(_score, include_groups=False)
            .reset_index().sort_values("net_wape_pp", ascending=False))


def direction_size_table(log: pd.DataFrame,
                         size_split: float = SIZE_SPLIT) -> pd.DataFrame:
    """The Fildes-style 2x2: direction x size, hit rate and net points."""
    d = _prep(log, size_split)
    d = d[d["overridden"]]
    return (d.groupby(["direction", "size"], observed=True)
            .apply(_score, include_groups=False).reset_index())


def reason_table(log: pd.DataFrame, size_split: float = SIZE_SPLIT,
                 min_n: int = 5) -> pd.DataFrame:
    """Net value by logged reason. Reasons with n < min_n stay in the table
    with their count, because 'insufficient sample' is itself a finding: a
    reason code used twice a quarter is a free-text field wearing a costume."""
    d = _prep(log, size_split)
    d = d[d["overridden"]]
    out = (d.groupby("reason", observed=True)
           .apply(_score, include_groups=False).reset_index())
    out["scored"] = out["n_overrides"] >= min_n
    return out.sort_values("net_wape_pp", ascending=False)


# ------------------------------------------------------------------- demo ---

if __name__ == "__main__":
    rng = np.random.default_rng(23)
    pd.set_option("display.width", 130)

    # One quarter, 60 series x 13 weeks. True demand ~ lognormal around 100.
    n = 60 * 13
    actual_mu = rng.lognormal(np.log(100), 0.4, n)
    actual = actual_mu * rng.lognormal(0, 0.15, n)
    stat = actual_mu * rng.lognormal(0, 0.12, n)   # decent statistical line

    owner = rng.choice(["planner_A", "planner_B", "sales_C"], n, p=[.4, .3, .3])
    final = stat.copy()
    reason = np.full(n, "untouched", dtype=object)

    # planner_A: informed large cuts on real events they can see coming.
    m = (owner == "planner_A") & (rng.random(n) < 0.25)
    event = m & (rng.random(n) < 0.7)              # the event usually fires
    actual[event] *= 0.70
    final[m] = stat[m] * 0.72
    reason[m] = "distributor holiday"

    # planner_B: small tweaks both ways on gut feel, pure noise.
    m = (owner == "planner_B") & (rng.random(n) < 0.60)
    final[m] = stat[m] * rng.lognormal(0, 0.05, int(m.sum()))
    reason[m] = "gut feel"

    # sales_C: small upward pads to protect the sales target.
    m = (owner == "sales_C") & (rng.random(n) < 0.50)
    final[m] = stat[m] * rng.lognormal(0.06, 0.03, int(m.sum()))
    reason[m] = "sales target"

    log = pd.DataFrame({"date": "2026-Q2", "series": np.arange(n) % 60,
                        "owner": owner, "reason": reason,
                        "stat": stat, "final": final, "actual": actual})

    print("Owner scorecard (net_wape_pp > 0 means the owner's overrides "
          "beat the statistical line)")
    print(owner_scorecard(log).to_string(index=False))
    print()
    print("Direction x size (the Fildes 2x2)")
    print(direction_size_table(log).to_string(index=False))
    print()
    print("By logged reason")
    print(reason_table(log).to_string(index=False))
    print()
    print("The quarterly meeting runs off these three tables: keep the "
          "override classes that pay (here: large informed cuts), route the "
          "ones that cost into a forecast the model can learn (the "
          "distributor calendar belongs in the feature set), and put the "
          "padding habit on the table with its price attached.")
