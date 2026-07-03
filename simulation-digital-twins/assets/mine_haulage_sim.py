# pip install simpy numpy scipy
"""Mine haulage chain DES: pit shovels -> truck fleet -> crusher -> stockpile
-> train loadout, in SimPy.

Demonstrates the four pieces of statistical craft that separate a defensible
DES study from a demo:

  1. Stream discipline: one named RNG per stochastic process per replication,
     seeded independently of the policy, so common random numbers (CRN)
     survive a policy change. A single global seed breaks CRN the moment a
     policy change reorders event execution and the processes start consuming
     each other's draws.
  2. Welch warm-up analysis on the hourly-throughput series.
  3. Replication sizing from a pilot run (iterated t-quantile solve).
  4. CRN paired comparison of two fleet policies, with the measured
     variance-reduction factor against independent sampling.

Run the demo:  python3 mine_haulage_sim.py
Runtime is under a minute on a laptop.

Simplifications, stated so nobody mistakes this for a site model:
  - Crusher failures run on a calendar clock. Real fleet-management MTBF is
    quoted in operating hours; convert before you parametrize.
  - The train takes whatever stockpile tonnes exist at each call, so train
    demurrage is out of scope.
  - One material type, no grade, no blending.
"""
from __future__ import annotations

import math
import zlib
from dataclasses import dataclass, replace

import numpy as np
import simpy
from scipy import stats

BASE_SEED = 20260712


def stream(rep: int, name: str) -> np.random.Generator:
    """One RNG per (replication, process name).

    The seed depends on the replication and the process name only. Two
    policies run with the same rep therefore see identical random inputs
    wherever their structure overlaps, which is the whole CRN mechanism.
    Per-truck streams (name includes the truck id) keep synchronization when
    a policy adds trucks: trucks 0..6 draw the same cycle times under both
    policies, and truck 7 gets a fresh stream of its own.
    """
    return np.random.default_rng(
        np.random.SeedSequence((BASE_SEED, rep, zlib.crc32(name.encode())))
    )


@dataclass(frozen=True)
class Params:
    n_trucks: int = 7
    payload_t: float = 220.0
    n_shovels: int = 2
    load_mean_min: float = 4.2      # shovel load time, gamma(k=16) => cv 0.25
    load_cv: float = 0.25
    haul_median_min: float = 11.0   # loaded haul, lognormal median
    haul_sigma: float = 0.22        # sigma of log(haul time)
    return_median_min: float = 8.5  # empty return, lognormal median
    dump_min: float = 1.6           # apron-feeder dump, deterministic
    crusher_mtbf_h: float = 30.0    # calendar-hour exponential
    crusher_mttr_h: float = 1.4     # lognormal median, sigma 0.5
    stockpile_cap_t: float = 60_000.0
    stockpile_init_t: float = 20_000.0
    train_interval_h: float = 8.0
    train_parcel_t: float = 30_000.0
    sim_hours: float = 240.0


class TimeWeighted:
    """Time-weighted average of a piecewise-constant signal (queue lengths,
    busy counts). Event-driven, so no sampling bias."""

    def __init__(self, env: simpy.Environment, initial: float = 0.0):
        self.env = env
        self.value = initial
        self.last_t = env.now
        self.area = 0.0

    def set(self, value: float) -> None:
        now = self.env.now
        self.area += self.value * (now - self.last_t)
        self.last_t = now
        self.value = value

    def add(self, delta: float) -> None:
        self.set(self.value + delta)

    def mean(self, since: float = 0.0) -> float:
        # Close the integral at the current time, then drop the warm-up area
        # by re-integrating is not possible; callers who need a post-warm-up
        # mean should construct the tracker after warm-up or accept the small
        # bias. The demo reports whole-run means for context metrics only.
        self.set(self.value)
        horizon = self.env.now - since
        return self.area / horizon if horizon > 0 else 0.0


class Model:
    def __init__(self, env: simpy.Environment, p: Params, rep: int,
                 stream_ns: str = ""):
        self.env, self.p, self.rep = env, p, rep
        self.ns = stream_ns  # non-empty namespace defeats CRN on purpose
        self.shovels = simpy.Resource(env, capacity=p.n_shovels)
        # PreemptiveResource lets the failure process interrupt a dump.
        self.crusher = simpy.PreemptiveResource(env, capacity=1)
        self.stockpile = simpy.Container(
            env, capacity=p.stockpile_cap_t, init=p.stockpile_init_t)
        self.crushed_t = 0.0
        self.hourly: list[float] = []
        self.shovel_q = TimeWeighted(env)
        self.crusher_q = TimeWeighted(env)
        self.crusher_down = TimeWeighted(env)

    def rng(self, name: str) -> np.random.Generator:
        return stream(self.rep, self.ns + name)

    # --- processes ---------------------------------------------------------

    def truck(self, tid: int):
        p = self.p
        # Per-truck streams keep CRN synchronized across fleet sizes.
        r_load = self.rng(f"load-{tid}")
        r_haul = self.rng(f"haul-{tid}")
        k = 1.0 / (p.load_cv ** 2)  # gamma shape from cv
        while True:
            with self.shovels.request() as req:
                self.shovel_q.add(1)
                yield req
                self.shovel_q.add(-1)
                load = r_load.gamma(k, p.load_mean_min / k) / 60.0
                yield self.env.timeout(load)
            yield self.env.timeout(
                math.exp(math.log(p.haul_median_min)
                         + p.haul_sigma * r_haul.standard_normal()) / 60.0)
            # Dump into the crusher; a failure preempts and we resume the
            # remaining dump time after repair (the machine-shop pattern).
            remaining = p.dump_min / 60.0
            self.crusher_q.add(1)
            queued = True
            while remaining > 1e-12:
                start = None
                with self.crusher.request(priority=1) as req:
                    try:
                        yield req
                        if queued:
                            self.crusher_q.add(-1)
                            queued = False
                        start = self.env.now
                        yield self.env.timeout(remaining)
                        remaining = 0.0
                    except simpy.Interrupt:
                        if start is not None:
                            remaining -= self.env.now - start
            self.crushed_t += p.payload_t
            self.stockpile.put(p.payload_t)  # blocks when the stockpile is full
            yield self.env.timeout(
                math.exp(math.log(p.return_median_min)
                         + p.haul_sigma * r_haul.standard_normal()) / 60.0)

    def crusher_failures(self):
        p = self.p
        r = self.rng("crusher-fail")
        while True:
            yield self.env.timeout(r.exponential(p.crusher_mtbf_h))
            with self.crusher.request(priority=0) as req:
                yield req
                self.crusher_down.set(1)
                repair = math.exp(math.log(p.crusher_mttr_h)
                                  + 0.5 * r.standard_normal())
                yield self.env.timeout(repair)
                self.crusher_down.set(0)

    def train_loadout(self):
        p = self.p
        while True:
            yield self.env.timeout(p.train_interval_h)
            take = min(p.train_parcel_t, self.stockpile.level)
            if take > 0:
                yield self.stockpile.get(take)

    def hourly_monitor(self):
        prev = 0.0
        while True:
            yield self.env.timeout(1.0)
            self.hourly.append(self.crushed_t - prev)
            prev = self.crushed_t

    def run(self) -> dict:
        p = self.p
        for tid in range(p.n_trucks):
            self.env.process(self.truck(tid))
        self.env.process(self.crusher_failures())
        self.env.process(self.train_loadout())
        self.env.process(self.hourly_monitor())
        self.env.run(until=p.sim_hours)
        return {
            "hourly": np.array(self.hourly),
            "shovel_q": self.shovel_q.mean(),
            "crusher_q": self.crusher_q.mean(),
            "crusher_downtime": self.crusher_down.mean(),
        }


def run_rep(p: Params, rep: int, stream_ns: str = "") -> dict:
    return Model(simpy.Environment(), p, rep, stream_ns).run()


def daily_throughput(hourly: np.ndarray, warmup_h: int) -> float:
    return float(hourly[warmup_h:].mean() * 24.0)


# --- Welch warm-up analysis -------------------------------------------------

def welch(p: Params, n_reps: int = 10, window: int = 25,
          band: float = 0.02, hold: int = 24) -> tuple[int, np.ndarray]:
    """Average the hourly series across replications, smooth with a centred
    moving average, and return the first hour after which the smoothed curve
    stays inside `band` of its terminal level for `hold` consecutive hours.

    Welch (1983) leaves the flat-point call to the analyst's eye; the band
    rule here automates the call so the demo is reproducible. Plot the curve
    before trusting the automated pick on a new model.
    """
    mat = np.vstack([run_rep(p, rep)["hourly"] for rep in range(n_reps)])
    mean = mat.mean(axis=0)
    kernel = np.ones(window) / window
    sm = np.convolve(mean, kernel, mode="valid")
    terminal = sm[len(sm) // 2:].mean()
    ok = np.abs(sm / terminal - 1.0) < band
    for i in range(len(ok) - hold):
        if ok[i:i + hold].all():
            # index in smoothed series -> hour in raw series (centred window)
            return i + window // 2, sm
    return len(sm) // 2, sm  # no flat point found: flag and extend the run


# --- replication sizing ------------------------------------------------------

def reps_for_half_width(sd: float, target_h: float, conf: float = 0.95,
                        n_max: int = 10_000) -> int:
    """Smallest n with t_{n-1, 1-a/2} * sd / sqrt(n) <= target_h."""
    for n in range(2, n_max):
        t = stats.t.ppf(0.5 + conf / 2.0, n - 1)
        if t * sd / math.sqrt(n) <= target_h:
            return n
    return n_max


def ci(data: np.ndarray, conf: float = 0.95) -> tuple[float, float]:
    n = len(data)
    h = stats.t.ppf(0.5 + conf / 2.0, n - 1) * data.std(ddof=1) / math.sqrt(n)
    return float(data.mean()), float(h)


# --- CRN policy comparison ---------------------------------------------------

def compare(p_a: Params, p_b: Params, n_reps: int, warmup_h: int) -> dict:
    """Paired (CRN) and independent comparisons of policy B minus policy A
    on steady-state daily throughput."""
    a = np.array([daily_throughput(run_rep(p_a, r)["hourly"], warmup_h)
                  for r in range(n_reps)])
    b = np.array([daily_throughput(run_rep(p_b, r)["hourly"], warmup_h)
                  for r in range(n_reps)])
    # Independent runs: a disjoint stream namespace defeats seed sharing.
    b_ind = np.array([daily_throughput(
        run_rep(p_b, r, stream_ns="ind/")["hourly"], warmup_h)
        for r in range(n_reps)])
    d_crn, d_ind = b - a, b_ind - a
    return {
        "a": a, "b": b,
        "diff_crn": ci(d_crn), "diff_ind": ci(d_ind),
        "var_ratio": d_ind.var(ddof=1) / d_crn.var(ddof=1),
        "rho": float(np.corrcoef(a, b)[0, 1]),
    }


if __name__ == "__main__":
    base = Params()

    print("=== 1. Welch warm-up analysis (10 reps, window 25 h) ===")
    warmup, sm = welch(base)
    print(f"smoothed hourly tonnes at h=5..240 step 24: "
          f"{[round(float(sm[min(i, len(sm) - 1)])) for i in range(5, 216, 24)]}")
    print(f"chosen warm-up: {warmup} h (band 2%, hold 24 h)\n")

    print("=== 2. Pilot run and replication sizing ===")
    pilot = np.array([daily_throughput(run_rep(base, r)["hourly"], warmup)
                      for r in range(10)])
    m, h = ci(pilot)
    print(f"pilot (n=10): mean {m:,.0f} t/day, sd {pilot.std(ddof=1):,.0f}, "
          f"95% CI half-width {h:,.0f} t/day")
    target = 500.0
    n_star = reps_for_half_width(pilot.std(ddof=1), target)
    print(f"replications for +/-{target:.0f} t/day at 95%: {n_star}\n")

    print("=== 3. CRN policy comparison: 8 trucks vs 7 trucks (15 reps) ===")
    res = compare(base, replace(base, n_trucks=8), n_reps=15, warmup_h=warmup)
    (dm, dh), (im, ih) = res["diff_crn"], res["diff_ind"]
    print(f"baseline mean: {res['a'].mean():,.0f} t/day | "
          f"8-truck mean: {res['b'].mean():,.0f} t/day")
    print(f"CRN paired diff:   {dm:+,.0f} +/- {dh:,.0f} t/day (95%)")
    print(f"independent diff:  {im:+,.0f} +/- {ih:,.0f} t/day (95%)")
    print(f"CRN correlation between policies: rho = {res['rho']:.3f}")
    print(f"variance ratio (independent / CRN): {res['var_ratio']:.1f}x "
          f"=> same precision with ~{res['var_ratio']:.0f}x fewer reps")

    print("\n=== 4. Context metrics, baseline rep 0 ===")
    out = run_rep(base, 0)
    print(f"mean shovel queue {out['shovel_q']:.2f} trucks, "
          f"mean crusher queue {out['crusher_q']:.2f} trucks, "
          f"crusher downtime fraction {out['crusher_downtime']:.3f}")
