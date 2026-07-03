# pip install numpy scipy
"""Replication-count calculator for terminating and steady-state simulation
studies.

Three procedures, in the order a study actually uses them:

  1. fixed_n_from_pilot: run a pilot (n0 >= 10), then solve for the smallest
     n with  t_{n-1, 1-a/2} * s0 / sqrt(n) <= h*.  The t-quantile falls as n
     grows, so the solve iterates; the naive z-formula understates n by a
     rep or two at n ~ 75 and by 30%+ when the answer is under ~15.
  2. relative_precision: Law's gamma-adjusted rule for "within 5% of the
     mean". The adjustment gamma/(1+gamma) exists because the target is
     relative to the UNKNOWN mean; skipping it makes 5% quietly become
     5.26%.
  3. sequential: add one replication at a time and stop when the half-width
     target holds. Cheapest in total runs; mildly biased coverage because
     the stopping rule peeks at the data (Law, Simulation Modeling and
     Analysis, 5th ed., ch. 9). Fine for engineering precision targets;
     state the rule in the report.

Run the demo:  python3 replication_calculator.py
"""
from __future__ import annotations

import math
from typing import Callable, Iterable

import numpy as np
from scipy import stats


def half_width(data: Iterable[float], conf: float = 0.95) -> float:
    x = np.asarray(list(data), dtype=float)
    n = len(x)
    return float(stats.t.ppf(0.5 + conf / 2.0, n - 1)
                 * x.std(ddof=1) / math.sqrt(n))


def fixed_n_from_pilot(pilot_sd: float, target_h: float,
                       conf: float = 0.95, n_max: int = 100_000) -> int:
    """Smallest n with t_{n-1} * pilot_sd / sqrt(n) <= target_h.

    Treats the pilot sd as the truth, which it is not; expect the achieved
    half-width to miss the target roughly half the time by a small margin.
    When the target is contractual, inflate the pilot sd by 20% or run the
    sequential procedure instead."""
    if target_h <= 0:
        raise ValueError("target_h must be positive")
    for n in range(2, n_max):
        t = stats.t.ppf(0.5 + conf / 2.0, n - 1)
        if t * pilot_sd / math.sqrt(n) <= target_h:
            return n
    return n_max


def relative_precision(pilot: Iterable[float], gamma: float = 0.05,
                       conf: float = 0.95, n_max: int = 100_000) -> int:
    """Smallest n whose expected half-width is within gamma of |mean|,
    using the gamma/(1+gamma) correction (Law 5th ed., eq. 9.1)."""
    x = np.asarray(list(pilot), dtype=float)
    sd, mean = x.std(ddof=1), abs(x.mean())
    g_adj = gamma / (1.0 + gamma)
    for n in range(2, n_max):
        t = stats.t.ppf(0.5 + conf / 2.0, n - 1)
        if t * sd / math.sqrt(n) / mean <= g_adj:
            return n
    return n_max


def sequential(run_one: Callable[[int], float], target_h: float,
               conf: float = 0.95, n0: int = 10, n_max: int = 10_000
               ) -> tuple[np.ndarray, float]:
    """Call run_one(rep_index) until the CI half-width meets target_h.
    Returns (data, achieved half-width)."""
    data = [run_one(i) for i in range(n0)]
    while half_width(data, conf) > target_h and len(data) < n_max:
        data.append(run_one(len(data)))
    return np.asarray(data), half_width(data, conf)


if __name__ == "__main__":
    rng = np.random.default_rng(11)

    # Stand-in for a DES: daily throughput, true mean 80,000, true sd 2,300.
    def one_rep(i: int) -> float:
        return float(rng.normal(80_000, 2_300))

    print("=== pilot of 10 replications ===")
    pilot = np.array([one_rep(i) for i in range(10)])
    sd0 = pilot.std(ddof=1)
    print(f"mean {pilot.mean():,.0f}, sd {sd0:,.0f}, "
          f"95% half-width {half_width(pilot):,.0f}")

    print("\n=== fixed-n for +/-500 at 95% ===")
    n_star = fixed_n_from_pilot(sd0, 500.0)
    z_naive = math.ceil((1.959964 * sd0 / 500.0) ** 2)
    print(f"iterated-t answer: {n_star} replications "
          f"(naive z-formula says {z_naive})")

    print("\n=== relative precision: within 5% of the mean ===")
    print(f"n = {relative_precision(pilot, gamma=0.05)} "
          f"(tight because sd/mean is only "
          f"{sd0 / pilot.mean():.3%} here)")

    print("\n=== sequential procedure, target +/-500 ===")
    data, h = sequential(one_rep, 500.0)
    print(f"stopped at n = {len(data)}, achieved half-width {h:,.0f}, "
          f"mean {data.mean():,.0f}")

    print("\n=== coverage check of the sequential rule (2,000 trials) ===")
    hits = 0
    for _ in range(2_000):
        d, _ = sequential(lambda i: float(rng.normal(80_000, 2_300)), 500.0)
        lo = d.mean() - half_width(d)
        hi = d.mean() + half_width(d)
        hits += lo <= 80_000 <= hi
    print(f"empirical coverage of the nominal 95% CI: {hits / 2_000:.3f} "
          f"(the peeking penalty is negligible at this sd/target ratio)")
