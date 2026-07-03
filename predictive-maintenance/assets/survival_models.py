"""Survival and reliability fits for maintenance data with censoring.

pip install: numpy pandas lifelines
(scipy arrives as a lifelines dependency; tested with numpy 2.5, pandas 2.3,
lifelines 0.30.3 on Python 3.14)

Three demos on synthetic fleet data, each targeting a mistake that recurs in
maintenance analytics:

  A. Weibull fit with right-censoring, against the two naive fits
     (drop censored units; treat censored as failed). Preventive change-outs
     censor most lifetimes in a real fleet, and both naive fits bias the
     scale parameter enough to flip the maintenance-policy conclusion.
  B. Cox proportional hazards with a time-varying covariate (payload
     utilization) in start-stop format via CoxTimeVaryingFitter.
  C. Repairable-system data: the Laplace trend test, a Crow-AMSAA
     (power-law NHPP) fit with closed-form MLE, and the wrong analysis
     (iid Weibull on inter-failure gaps) shown failing side by side.

Run: python survival_models.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from lifelines import CoxTimeVaryingFitter, WeibullFitter

RNG = np.random.default_rng(7)


# ---------------------------------------------------------------- demo A ---

def simulate_component_lives(
    n: int = 150,
    shape: float = 2.6,
    scale_h: float = 14_000.0,
    pm_changeout_h: float = 14_000.0,
    window_h: float = 40_000.0,
) -> pd.DataFrame:
    """Fleet of components with two censoring sources.

    True lives are Weibull(shape, scale). A preventive change-out policy
    replaces survivors at pm_changeout_h (type-I censoring), and staggered
    commissioning inside a finite observation window censors young units.
    """
    true_life = scale_h * RNG.weibull(shape, size=n)
    install = RNG.uniform(0.0, window_h - 2_000.0, size=n)
    exposure = window_h - install                      # hours of observation
    duration = np.minimum.reduce([true_life, np.full(n, pm_changeout_h), exposure])
    event = (true_life <= pm_changeout_h) & (true_life <= exposure)
    return pd.DataFrame({"duration_h": duration, "failed": event.astype(int)})


def weibull_three_ways(df: pd.DataFrame) -> None:
    frac_censored = 1.0 - df["failed"].mean()
    print(f"fleet: {len(df)} components, {frac_censored:.0%} censored")

    correct = WeibullFitter().fit(df["duration_h"], df["failed"], label="censoring handled")
    dropped = WeibullFitter().fit(
        df.loc[df["failed"] == 1, "duration_h"],
        np.ones(int(df["failed"].sum())),
        label="censored units dropped",
    )
    as_failed = WeibullFitter().fit(df["duration_h"], np.ones(len(df)),
                                    label="censored treated as failed")

    print(f"{'fit':<28}{'shape':>8}{'scale (h)':>12}{'B10 life (h)':>14}")
    for wf in (correct, dropped, as_failed):
        b10 = wf.lambda_ * (-np.log(0.9)) ** (1.0 / wf.rho_)
        print(f"{wf.label:<28}{wf.rho_:>8.2f}{wf.lambda_:>12,.0f}{b10:>14,.0f}")
    row = correct.summary.loc["rho_"]
    print(f"shape 95% CI [{row['coef lower 95%']:.2f}, "
          f"{row['coef upper 95%']:.2f}]  "
          f"(rho > 1 means wear-out; age-based replacement can pay)")


# ---------------------------------------------------------------- demo B ---

def simulate_time_varying(
    n_machines: int = 200,
    period_h: float = 500.0,
    n_periods: int = 30,
    beta_util: float = 1.4,
    shape: float = 2.2,
    scale_h: float = 18_000.0,
) -> pd.DataFrame:
    """Start-stop rows: piecewise-constant utilization drives the hazard.

    Hazard in each period is the Weibull baseline at the period midpoint
    times exp(beta_util * utilization), utilization scaled to [0, 1].
    """
    rows = []
    for m in range(n_machines):
        base_util = RNG.uniform(0.2, 0.8)
        for k in range(n_periods):
            start, stop = k * period_h, (k + 1) * period_h
            util = np.clip(base_util + RNG.normal(0, 0.10), 0.0, 1.0)
            mid = 0.5 * (start + stop)
            h0 = (shape / scale_h) * (mid / scale_h) ** (shape - 1.0)
            p_fail = 1.0 - np.exp(-h0 * period_h * np.exp(beta_util * util))
            fail = RNG.random() < p_fail
            rows.append((m, start, stop, util, int(fail)))
            if fail:
                break
    return pd.DataFrame(rows, columns=["id", "start", "stop", "util", "event"])


def cox_time_varying(df: pd.DataFrame) -> None:
    ctv = CoxTimeVaryingFitter()
    ctv.fit(df, id_col="id", event_col="event",
            start_col="start", stop_col="stop", show_progress=False)
    coef = ctv.summary.loc["util"]
    print(f"machines: {df['id'].nunique()}, failures: {int(df['event'].sum())}, "
          f"rows: {len(df)}")
    print(f"utilization coef {coef['coef']:.2f} "
          f"(true 1.40), HR per +0.1 util = {np.exp(0.1 * coef['coef']):.3f}, "
          f"p = {coef['p']:.1e}")
    print("note: CoxTimeVaryingFitter has no predict_survival_function; "
          "use it for hazard ratios, use a parametric or landmark model "
          "to produce forward risk scores")


# ---------------------------------------------------------------- demo C ---

def simulate_nhpp_power_law(
    beta: float = 1.6, lam: float = 6.0e-6, t_end_h: float = 30_000.0
) -> np.ndarray:
    """Failure times of one deteriorating repairable system.

    Power-law NHPP with intensity lam * beta * t^(beta-1). Conditional on
    the count, arrival times are order statistics of (t/T)^beta.
    """
    n = RNG.poisson(lam * t_end_h**beta)
    return np.sort(t_end_h * RNG.random(n) ** (1.0 / beta))


def laplace_trend_test(times: np.ndarray, t_end: float) -> float:
    """Standard-normal statistic; u > 1.96 means deteriorating at 5%."""
    n = len(times)
    return (times.sum() / n - t_end / 2.0) / (t_end * np.sqrt(1.0 / (12.0 * n)))


def crow_amsaa_mle(times: np.ndarray, t_end: float) -> tuple[float, float]:
    """Closed-form MLE for the time-truncated power-law NHPP."""
    n = len(times)
    beta_hat = n / np.log(t_end / times).sum()
    lam_hat = n / t_end**beta_hat
    return beta_hat, lam_hat


def repairable_system_demo() -> None:
    t_end = 30_000.0
    times = simulate_nhpp_power_law(t_end_h=t_end)
    u = laplace_trend_test(times, t_end)
    beta_hat, lam_hat = crow_amsaa_mle(times, t_end)
    rocof_now = lam_hat * beta_hat * t_end ** (beta_hat - 1.0)

    gaps = np.diff(np.concatenate([[0.0], times]))
    wf = WeibullFitter().fit(gaps, np.ones(len(gaps)))

    print(f"failures on one system over {t_end:,.0f} h: {len(times)}")
    print(f"Laplace trend u = {u:.2f}  "
          f"({'deteriorating' if u > 1.96 else 'no trend at 5%'})")
    print(f"Crow-AMSAA: beta = {beta_hat:.2f} (true 1.60), "
          f"current ROCOF = {rocof_now * 1000:.2f} failures per 1,000 h")
    print(f"wrong iid-Weibull on gaps: shape = {wf.rho_:.2f} "
          f"(near 1.0, reads as 'random failures' and hides the trend; "
          f"gaps from a deteriorating NHPP are neither iid nor Weibull)")


if __name__ == "__main__":
    print("=== A. Weibull with right-censoring, three ways ===")
    weibull_three_ways(simulate_component_lives())
    print("\n=== B. Cox with time-varying utilization ===")
    cox_time_varying(simulate_time_varying())
    print("\n=== C. Repairable system: trend test + Crow-AMSAA ===")
    repairable_system_demo()
