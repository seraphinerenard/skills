#!/usr/bin/env python3
# pip install: numpy scipy
"""Finite-horizon markdown optimization as a dynamic program over inventory.

Setting: a seasonal item (fashion, seasonal hardware, holiday stock) with a
fixed initial buy, no reorder, a hard season end, and a discrete markdown
ladder that can only move down. The DP chooses the ladder step each week to
maximize expected revenue plus salvage.

State: (week t, inventory n, current ladder step k). Action: ladder step
k' >= k (markdowns are irreversible; retailers do not re-raise a marked-down
seasonal item because the shelf tag and the customer's memory both forbid it).
Demand at step k in week t: Poisson with mean A_t * (p_k / p_0) ** beta,
where A_t is a decaying season traffic curve and beta is the markdown-range
elasticity (steeper than base-price elasticity; the clearance shopper is the
most price-sensitive customer the item will ever meet).

Bellman recursion:
  V_t(n, k) = max_{k' >= k}  E_D[ p_{k'} * min(D, n) + V_{t+1}(n - min(D, n), k') ]
  V_T(n, k) = salvage * n

The demo prints the optimal policy frontier (the inventory threshold above
which the DP drops price, per week), the DP value, a Monte Carlo check of
that value, and a comparison against two fixed calendars a merchant would
actually propose. Run time is a few seconds.
"""

import numpy as np
from scipy import stats


def season_demand_curve(n_weeks, base, decay):
    """Traffic decays through the season: A_t = base * exp(-decay * t)."""
    t = np.arange(n_weeks)
    return base * np.exp(-decay * t)


def solve_markdown_dp(prices, full_price, beta, traffic, n0, salvage,
                      d_tail=1e-10):
    """Backward induction over (week, inventory, ladder step).

    Returns (V, policy):
      V[t, n, k]      expected future revenue from state (t, n, k)
      policy[t, n, k] optimal ladder step chosen in that state
    """
    n_weeks = len(traffic)
    n_steps = len(prices)
    inv = np.arange(n0 + 1)

    V = np.zeros((n_weeks + 1, n0 + 1, n_steps))
    V[n_weeks] = salvage * inv[:, None]
    policy = np.zeros((n_weeks, n0 + 1, n_steps), dtype=int)

    for t in range(n_weeks - 1, -1, -1):
        # Candidate value of playing step k2 this week, for every inventory.
        cand = np.full((n0 + 1, n_steps), -np.inf)
        for k2 in range(n_steps):
            lam = traffic[t] * (prices[k2] / full_price) ** beta
            dmax = int(stats.poisson.isf(d_tail, lam)) + 1
            d = np.arange(dmax + 1)
            pmf = stats.poisson.pmf(d, lam)
            pmf[-1] = 1.0 - pmf[:-1].sum()          # fold the tail mass in
            sold = np.minimum(d[None, :], inv[:, None])   # (n0+1, dmax+1)
            nxt = inv[:, None] - sold
            cand[:, k2] = (pmf[None, :]
                           * (prices[k2] * sold + V[t + 1][nxt, k2])).sum(axis=1)
        for k in range(n_steps):
            feas = cand[:, k:]                       # only k' >= k is legal
            policy[t, :, k] = k + np.argmax(feas, axis=1)
            V[t, :, k] = np.max(feas, axis=1)
    return V, policy


def simulate(policy, prices, full_price, beta, traffic, n0, salvage,
             n_sims, seed=0):
    """Monte Carlo revenue under a policy array policy[t, n, k]."""
    rng = np.random.default_rng(seed)
    n_weeks = len(traffic)
    rev = np.zeros(n_sims)
    inv = np.full(n_sims, n0)
    step = np.zeros(n_sims, dtype=int)
    for t in range(n_weeks):
        step = policy[t][inv, step]
        lam = traffic[t] * (prices[step] / full_price) ** beta
        d = rng.poisson(lam)
        sold = np.minimum(d, inv)
        rev += prices[step] * sold
        inv -= sold
    return rev + salvage * inv


def fixed_policy(schedule, n_weeks, n0, n_steps):
    """Build a policy array for a fixed calendar {week: step}."""
    pol = np.zeros((n_weeks, n0 + 1, n_steps), dtype=int)
    cur = 0
    for t in range(n_weeks):
        cur = max(cur, schedule.get(t, cur))
        pol[t, :, :] = np.maximum(cur, np.arange(n_steps)[None, :])
    return pol


if __name__ == "__main__":
    # A $60 seasonal item, 16-week season, 400 units bought, $8 salvage
    # (jobber/outlet), ladder 0/25/40/60 percent off, markdown elasticity -2.8.
    full_price = 60.0
    prices = np.array([60.0, 45.0, 36.0, 24.0])
    beta = -2.8
    n_weeks, n0, salvage = 16, 400, 8.0
    traffic = season_demand_curve(n_weeks, base=32.0, decay=0.16)

    V, policy = solve_markdown_dp(prices, full_price, beta, traffic, n0,
                                  salvage)
    dp_value = V[0, n0, 0]
    print(f"DP expected revenue (incl. salvage): ${dp_value:,.0f}")

    mc = simulate(policy, prices, full_price, beta, traffic, n0, salvage,
                  n_sims=20000)
    print(f"Monte Carlo under DP policy:         ${mc.mean():,.0f} "
          f"(se {mc.std() / np.sqrt(len(mc)):,.1f})")

    # Policy frontier: smallest inventory at which the DP has already left
    # full price, per week (read: 'if you still hold >= this many units in
    # week t, you should be marked down by now').
    print("\nweek  first-markdown inventory threshold (from full price)")
    for t in range(n_weeks):
        below = np.where(policy[t, :, 0] > 0)[0]
        thr = below.min() if len(below) else None
        print(f"  {t:2d}   {'never' if thr is None else thr}")

    # Benchmarks a merchant would propose.
    never = fixed_policy({}, n_weeks, n0, len(prices))
    classic = fixed_policy({8: 1, 12: 2, 14: 3}, n_weeks, n0, len(prices))
    for name, pol in [("no markdown at all", never),
                      ("fixed calendar wk8/12/14", classic)]:
        r = simulate(pol, prices, full_price, beta, traffic, n0, salvage,
                     n_sims=20000, seed=1)
        gap = dp_value - r.mean()
        print(f"\n{name}: ${r.mean():,.0f}  "
              f"(DP adds ${gap:,.0f}, {100 * gap / r.mean():.1f}%)")
