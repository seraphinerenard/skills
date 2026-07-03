# pip install simpy numpy scipy
"""Bayesian optimization over an expensive stochastic simulation, on a toy
three-machine flow line with finite buffers and a failure-prone middle
machine.

Decision variables: the two buffer sizes b1, b2 in [1, 40].
Objective: steady-state throughput (parts/h) minus a holding cost per buffer
slot. Each objective evaluation is a small SimPy run, so it is noisy; the
point of the module is the machinery that respects that noise:

  - GP surrogate with a fitted noise term (RBF-ARD + white noise), scaled
    inputs, standardized outputs, hyperparameters by L-BFGS on the log
    marginal likelihood with restarts. No library beyond numpy/scipy, so the
    mechanics stay visible; swap in BoTorch qLogNEI for production work.
  - Expected improvement computed against the best POSTERIOR MEAN at an
    observed point. EI against the best raw observation chases noise: the
    incumbent is then a lucky draw and the optimizer stalls under-exploring.
  - An equal-budget random-search baseline, with both winners re-evaluated
    on 20 fresh replications. Comparing on the noisy training values would
    flatter whichever method got luckier; the fresh-replication re-test is
    the honest scoreboard.

Run the demo:  python3 sim_opt_bayes.py   (about one minute)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import simpy
from scipy import optimize, stats

BASE_SEED = 813


# --- the "expensive" simulator ----------------------------------------------

@dataclass(frozen=True)
class Line:
    rates: tuple = (11.0, 10.0, 11.5)   # parts/h, machine 2 is the bottleneck
    mtbf_h: float = 8.0                 # machine 2 only
    mttr_h: float = 0.5
    warmup_h: float = 20.0
    horizon_h: float = 220.0
    hold_cost: float = 0.03             # objective points per buffer slot


def simulate_line(b1: int, b2: int, seed: int, line: Line = Line()) -> float:
    """One replication: net objective = throughput - holding cost."""
    rng = np.random.default_rng(np.random.SeedSequence((BASE_SEED, seed)))
    env = simpy.Environment()
    buf1 = simpy.Store(env, capacity=b1)
    buf2 = simpy.Store(env, capacity=b2)
    done = {"n": 0, "warm": 0}
    m2_up = env.event()
    m2_up.succeed()

    def machine(rate, src, dst, is_m2=False):
        while True:
            part = 1 if src is None else (yield src.get())
            yield env.timeout(rng.exponential(1.0 / rate))
            if is_m2:
                yield m2_state["up"]      # wait out repairs
            if dst is None:
                done["n"] += 1
                if env.now <= line.warmup_h:
                    done["warm"] += 1
            else:
                yield dst.put(part)       # blocks when the buffer is full

    m2_state = {"up": m2_up}

    def failures():
        while True:
            yield env.timeout(rng.exponential(line.mtbf_h))
            m2_state["up"] = env.event()
            yield env.timeout(rng.exponential(line.mttr_h))
            m2_state["up"].succeed()

    env.process(machine(line.rates[0], None, buf1))
    env.process(machine(line.rates[1], buf1, buf2, is_m2=True))
    env.process(machine(line.rates[2], buf2, None))
    env.process(failures())
    env.run(until=line.horizon_h)
    tp = (done["n"] - done["warm"]) / (line.horizon_h - line.warmup_h)
    return tp - line.hold_cost * (b1 + b2)


def evaluate(x: np.ndarray, seed: int, reps: int = 2) -> float:
    """Average of `reps` independent replications at design x = (b1, b2)."""
    b1, b2 = int(round(x[0])), int(round(x[1]))
    return float(np.mean([simulate_line(b1, b2, seed * 1000 + r)
                          for r in range(reps)]))


# --- minimal GP with fitted noise --------------------------------------------

class GP:
    """RBF-ARD kernel plus white noise, zero prior mean on standardized y."""

    def __init__(self, x: np.ndarray, y: np.ndarray):
        self.x = x
        self.mu, self.sd = y.mean(), y.std() + 1e-12
        self.y = (y - self.mu) / self.sd
        self.theta = self._fit()          # log(ls_1, ls_2, sf, sn)
        self._factor()

    def _nll(self, theta):
        k = self._kernel(self.x, self.x, theta)
        k[np.diag_indices_from(k)] += 1e-8
        try:
            chol = np.linalg.cholesky(k)
        except np.linalg.LinAlgError:
            return 1e10
        alpha = np.linalg.solve(chol.T, np.linalg.solve(chol, self.y))
        return float(0.5 * self.y @ alpha + np.log(np.diag(chol)).sum())

    @staticmethod
    def _kernel(a, b, theta):
        ls = np.exp(theta[:2])
        sf, sn = np.exp(theta[2]), np.exp(theta[3])
        d2 = ((a[:, None, :] - b[None, :, :]) / ls) ** 2
        k = sf ** 2 * np.exp(-0.5 * d2.sum(-1))
        if a.shape[0] == b.shape[0] and a is b:
            k[np.diag_indices_from(k)] += sn ** 2
        return k

    def _fit(self):
        best, best_val = None, np.inf
        rng = np.random.default_rng(0)
        for _ in range(6):
            x0 = np.concatenate([rng.uniform(-1.5, 0.5, 2),   # lengthscales
                                 rng.uniform(-1.0, 1.0, 1),   # signal
                                 rng.uniform(-3.0, -0.5, 1)]) # noise
            res = optimize.minimize(self._nll, x0, method="L-BFGS-B")
            if res.fun < best_val:
                best, best_val = res.x, res.fun
        return best

    def _factor(self):
        k = self._kernel(self.x, self.x, self.theta)
        k[np.diag_indices_from(k)] += 1e-8
        self.chol = np.linalg.cholesky(k)
        self.alpha = np.linalg.solve(
            self.chol.T, np.linalg.solve(self.chol, self.y))

    def predict(self, xq: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Posterior mean and sd of the LATENT (noise-free) objective."""
        ks = self._kernel(xq, self.x, self.theta)
        mean = ks @ self.alpha
        v = np.linalg.solve(self.chol, ks.T)
        sf = np.exp(self.theta[2])
        var = np.clip(sf ** 2 - (v ** 2).sum(0), 1e-12, None)
        return mean * self.sd + self.mu, np.sqrt(var) * self.sd


def expected_improvement(gp: GP, xq: np.ndarray, incumbent: float
                         ) -> np.ndarray:
    mean, sd = gp.predict(xq)
    z = (mean - incumbent) / sd
    return (mean - incumbent) * stats.norm.cdf(z) + sd * stats.norm.pdf(z)


# --- the optimization loop ---------------------------------------------------

BOUNDS = np.array([[1.0, 40.0], [1.0, 40.0]])


def scale(x):
    return (x - BOUNDS[:, 0]) / (BOUNDS[:, 1] - BOUNDS[:, 0])


def bayes_opt(budget: int = 32, n_init: int = 8, verbose: bool = True):
    rng = np.random.default_rng(4)
    # Space-filling initial design (jittered grid stands in for an LHS).
    grid = np.array([[b1, b2] for b1 in (5, 15, 25, 35)
                     for b2 in (10, 30)], dtype=float)
    xs = grid + rng.uniform(-2, 2, grid.shape)
    ys = [evaluate(x, seed=i) for i, x in enumerate(xs)]
    xs = list(xs)
    for it in range(n_init, budget):
        gp = GP(scale(np.array(xs)), np.array(ys))
        mean_obs, _ = gp.predict(scale(np.array(xs)))
        incumbent = mean_obs.max()        # best posterior mean, never raw y
        cand = rng.uniform(BOUNDS[:, 0], BOUNDS[:, 1], (4000, 2))
        ei = expected_improvement(gp, scale(cand), incumbent)
        x_next = cand[ei.argmax()]
        y_next = evaluate(x_next, seed=it)
        xs.append(x_next)
        ys.append(y_next)
        if verbose and (it + 1) % 8 == 0:
            print(f"  iter {it + 1:2d}: tried b=({x_next[0]:4.1f}, "
                  f"{x_next[1]:4.1f}) -> {y_next:.3f} | "
                  f"incumbent posterior mean {incumbent:.3f}")
    gp = GP(scale(np.array(xs)), np.array(ys))
    mean_obs, _ = gp.predict(scale(np.array(xs)))
    best = np.array(xs)[mean_obs.argmax()]
    return best, np.array(xs), np.array(ys)


def random_search(budget: int = 32):
    rng = np.random.default_rng(99)
    xs = rng.uniform(BOUNDS[:, 0], BOUNDS[:, 1], (budget, 2))
    ys = np.array([evaluate(x, seed=500 + i) for i, x in enumerate(xs)])
    return xs[ys.argmax()], xs, ys


def fresh_score(x: np.ndarray, reps: int = 20) -> tuple[float, float]:
    vals = np.array([simulate_line(int(round(x[0])), int(round(x[1])),
                                   seed=9_000 + r) for r in range(reps)])
    return float(vals.mean()), float(
        stats.t.ppf(0.975, reps - 1) * vals.std(ddof=1) / math.sqrt(reps))


if __name__ == "__main__":
    budget = 32
    print(f"=== Bayesian optimization, budget {budget} evaluations "
          f"(2 reps each) ===")
    x_bo, _, _ = bayes_opt(budget)
    print(f"BO pick: b1={x_bo[0]:.0f}, b2={x_bo[1]:.0f}")

    print(f"\n=== random search, same budget ===")
    x_rs, _, ys_rs = random_search(budget)
    print(f"RS pick: b1={x_rs[0]:.0f}, b2={x_rs[1]:.0f} "
          f"(training value {ys_rs.max():.3f})")

    print("\n=== honest re-test: 20 fresh replications of each winner ===")
    for label, x in (("BO", x_bo), ("RS", x_rs)):
        m, h = fresh_score(x)
        print(f"{label} config b=({x[0]:.0f}, {x[1]:.0f}): "
              f"objective {m:.3f} +/- {h:.3f} (95% CI)")
    m0, h0 = fresh_score(np.array([40, 40]))
    print(f"max-buffer reference b=(40, 40): {m0:.3f} +/- {h0:.3f} "
          f"(buys throughput at full holding cost)")
