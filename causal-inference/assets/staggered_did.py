# pip install numpy pandas
"""Staggered difference-in-differences via group-time ATTs
(Callaway & Sant'Anna, J. Econometrics 2021, unconditional version),
with a two-way fixed effects (TWFE) comparison that exhibits the
heterogeneity bias on the same data.

ATT(g, t) = [ mean_{i in cohort g}  (Y_it - Y_i,g-1) ]
          - [ mean_{i in controls}  (Y_it - Y_i,g-1) ]

Controls are never-treated units, or optionally not-yet-treated units
(first_treat > t). The base period is g-1 throughout, including for the
pre-period placebo estimates, so the event-study coefficient at e = -1 is
zero by construction. Aggregations weight cohorts by size. Inference is a
cluster bootstrap over units (percentile intervals).

This module exists to make the mechanics inspectable and to demonstrate the
TWFE failure. For client work use pyfixest or the R `did` package; both are
maintained and validated (see references/staggered-did.md in this skill).

Run the demo: python3 staggered_did.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

NEVER = np.inf


def att_gt(df: pd.DataFrame, unit: str = "unit", time: str = "time",
           first_treat: str = "first_treat", y: str = "y",
           control_group: str = "never_treated") -> pd.DataFrame:
    """Group-time ATTs on a balanced panel.

    df columns: unit id, integer time, first treatment period (np.inf for
    never treated), outcome. Returns rows (group, time, event_time, att,
    n_treated, n_control).
    """
    Y = df.pivot(index=unit, columns=time, values=y)
    ft = df.groupby(unit)[first_treat].first().reindex(Y.index).to_numpy(dtype=float)
    times = np.array(sorted(Y.columns))
    rows = []
    for g in sorted(set(ft[np.isfinite(ft)])):
        base = g - 1
        if base not in Y.columns:
            continue
        in_g = ft == g
        for t in times:
            if t == base:
                continue
            if control_group == "never_treated":
                ctrl = ~np.isfinite(ft)
            elif control_group == "not_yet_treated":
                ctrl = (ft > max(t, base)) & ~in_g
            else:
                raise ValueError(control_group)
            if ctrl.sum() == 0 or in_g.sum() == 0:
                continue
            d_treat = (Y[t] - Y[base]).to_numpy()[in_g].mean()
            d_ctrl = (Y[t] - Y[base]).to_numpy()[ctrl].mean()
            rows.append({"group": g, "time": t, "event_time": t - g,
                         "att": d_treat - d_ctrl,
                         "n_treated": int(in_g.sum()), "n_control": int(ctrl.sum())})
    return pd.DataFrame(rows)


def aggregate_event_study(gt: pd.DataFrame) -> pd.DataFrame:
    """Cohort-size-weighted mean ATT by event time."""
    def wmean(sub):
        return np.average(sub["att"], weights=sub["n_treated"])
    return (gt.groupby("event_time").apply(wmean, include_groups=False)
              .rename("att").reset_index())


def overall_att(gt: pd.DataFrame) -> float:
    """Cohort-size-weighted mean over all post-treatment (g, t) cells."""
    post = gt[gt["event_time"] >= 0]
    return float(np.average(post["att"], weights=post["n_treated"]))


def twfe_estimate(df: pd.DataFrame, unit: str = "unit", time: str = "time",
                  first_treat: str = "first_treat", y: str = "y") -> float:
    """Static TWFE coefficient on a balanced panel via two-way demeaning."""
    Y = df.pivot(index=unit, columns=time, values=y)
    ft = df.groupby(unit)[first_treat].first().reindex(Y.index).to_numpy(dtype=float)
    times = np.array(sorted(Y.columns), dtype=float)
    D = (times[None, :] >= ft[:, None]).astype(float)
    M = Y.to_numpy()

    def demean(A):
        return A - A.mean(1, keepdims=True) - A.mean(0, keepdims=True) + A.mean()

    Dd, Md = demean(D), demean(M)
    return float((Dd * Md).sum() / (Dd * Dd).sum())


def bootstrap_overall(df: pd.DataFrame, n_boot: int = 200, seed: int = 0,
                      control_group: str = "never_treated", **cols) -> tuple:
    """Cluster (unit) bootstrap percentile CI for the overall ATT."""
    rng = np.random.default_rng(seed)
    unit = cols.get("unit", "unit")
    units = df[unit].unique()
    stats = []
    for _ in range(n_boot):
        draw = rng.choice(units, size=len(units), replace=True)
        parts = []
        for k, u in enumerate(draw):
            sub = df[df[unit] == u].copy()
            sub[unit] = k  # unique id per resample so pivot stays balanced
            parts.append(sub)
        bdf = pd.concat(parts, ignore_index=True)
        gt = att_gt(bdf, control_group=control_group, **cols)
        if len(gt) and (gt["event_time"] >= 0).any():
            stats.append(overall_att(gt))
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return float(lo), float(hi)


def _make_panel(seed: int = 3) -> tuple[pd.DataFrame, float, dict]:
    """40 units, 20 periods, cohorts g=6 (early) and g=11 (late), 20 never.
    True effect for cohort g at event time e >= 0: tau_g + 0.30 * e, with the
    early cohort at tau=2.0 and the late cohort at tau=0.5. Effects grow with
    exposure, which is exactly the pattern that breaks static TWFE."""
    rng = np.random.default_rng(seed)
    n_units, n_periods = 40, 20
    ft = np.array([6.0] * 10 + [11.0] * 10 + [NEVER] * 20)
    tau0 = {6.0: 2.0, 11.0: 0.5}
    unit_fe = rng.normal(0, 2, n_units)
    time_fe = np.cumsum(rng.normal(0.2, 0.3, n_periods))
    rows, true_cells = [], []
    for i in range(n_units):
        for t in range(n_periods):
            e = t - ft[i]
            tau = (tau0[ft[i]] + 0.30 * e) if np.isfinite(ft[i]) and e >= 0 else 0.0
            if np.isfinite(ft[i]) and e >= 0:
                true_cells.append(tau)
            rows.append({"unit": i, "time": t, "first_treat": ft[i],
                         "y": unit_fe[i] + time_fe[t] + tau + rng.normal(0, 0.5)})
    truth_by_e = {e: np.mean([tau0[g] + 0.30 * e for g in (6.0, 11.0)
                              if e <= 19 - g]) for e in range(0, 14)}
    return pd.DataFrame(rows), float(np.mean(true_cells)), truth_by_e


def _demo() -> None:
    df, true_att, truth_by_e = _make_panel()
    gt = att_gt(df)
    es = aggregate_event_study(gt)
    att = overall_att(gt)
    lo, hi = bootstrap_overall(df, n_boot=200)
    twfe = twfe_estimate(df)

    print("Staggered DiD demo: 40 units, 20 periods, cohorts at t=6 and t=11")
    print("true overall ATT (mean over treated cells): %.3f" % true_att)
    print("group-time estimator: %.3f  [95%% CI %.3f, %.3f]" % (att, lo, hi))
    print("static TWFE estimate: %.3f  (biased low: late-treated units are"
          % twfe)
    print("  compared against already-treated units whose effects keep growing)")
    print()
    print("event time   estimate   truth")
    for _, r in es.iterrows():
        e = int(r["event_time"])
        if -3 <= e <= 6:
            t = truth_by_e.get(e, 0.0) if e >= 0 else 0.0
            print("   %+3d      %7.3f   %6.3f" % (e, r["att"], t))
    near_pre = es[(es["event_time"] >= -4) & (es["event_time"] <= -2)]
    pre = near_pre["att"].abs().max()
    assert abs(att - true_att) < 0.25, "group-time estimate off truth"
    assert abs(twfe - true_att) > 0.5, "TWFE should be visibly biased here"
    assert pre < 0.4, "placebos in the -4..-2 window should sit near zero"
    print()
    print("smoke test passed: group-time ATT %.2f vs truth %.2f; TWFE %.2f is"
          " biased; max |pre-period placebo| = %.2f" % (att, true_att, twfe, pre))


if __name__ == "__main__":
    _demo()
