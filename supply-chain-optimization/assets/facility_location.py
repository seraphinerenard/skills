#!/usr/bin/env python3
"""Capacitated facility location (CFLP), solved with HiGHS.

pip install pulp highspy

Pick which depots to open and how to route customer demand so fixed opening
cost plus transport cost is minimized. The demo builds the same instance in
the weak formulation (capacity linking only) and the strong formulation
(adds the disaggregated variable-upper-bound cuts x_ij <= min(d_i, K_j) y_j)
and prints both LP bounds: the strong formulation typically closes most of
the root gap, which is why it wins on real network-design instances even
though it has |I| x |J| extra rows.

Model (full derivation in references/formulations.md):
  min  sum_j f_j y_j + sum_{i,j} c_ij x_ij
  s.t. sum_j x_ij = d_i                 (demand met)
       sum_i x_ij <= K_j y_j           (capacity + linking)
       x_ij <= min(d_i, K_j) y_j       (strong formulation only)
       x >= 0;  y binary
Costs c_ij here are demand-weighted distances; on a real engagement they come
from a rated freight matrix (lane rates or a cost-per-km-per-unit model).
"""

import math
import random

import pulp


def build_cflp(fixed, cap, demand, cost, strong=True, relax=False):
    """fixed[j], cap[j], demand[i], cost[(i,j)] per unit. Returns PuLP model."""
    J, I = list(fixed), list(demand)
    prob = pulp.LpProblem("cflp", pulp.LpMinimize)
    cat = "Continuous" if relax else "Binary"
    y = pulp.LpVariable.dicts("open", J, lowBound=0, upBound=1, cat=cat)
    x = pulp.LpVariable.dicts("flow", (I, J), lowBound=0)

    prob += (pulp.lpSum(fixed[j] * y[j] for j in J)
             + pulp.lpSum(cost[i, j] * x[i][j] for i in I for j in J))
    for i in I:
        prob += pulp.lpSum(x[i][j] for j in J) == demand[i], f"met_{i}"
    for j in J:
        prob += pulp.lpSum(x[i][j] for i in I) <= cap[j] * y[j], f"cap_{j}"
    if strong:
        for i in I:
            for j in J:
                prob += x[i][j] <= min(demand[i], cap[j]) * y[j], f"vub_{i}_{j}"
    return prob


def solve(prob, gap=1e-4, time_limit=120):
    status = prob.solve(pulp.HiGHS(msg=False, gapRel=gap, timeLimit=time_limit))
    if pulp.LpStatus[status] not in ("Optimal", "Integer Feasible"):
        raise RuntimeError(f"solver status {pulp.LpStatus[status]}")
    return pulp.value(prob.objective)


def demo_instance(n_sites=20, n_customers=80, seed=7):
    """Synthetic region: customers clustered around 4 metros, candidate depots
    scattered, capacity sized so roughly 4 to 6 depots are needed."""
    rng = random.Random(seed)
    metros = [(20, 20), (80, 25), (30, 75), (70, 70)]
    customers, demand = {}, {}
    for k in range(n_customers):
        mx, my = metros[k % 4]
        customers[f"c{k:02d}"] = (rng.gauss(mx, 9), rng.gauss(my, 9))
        demand[f"c{k:02d}"] = rng.randint(5, 40)
    sites, fixed, cap = {}, {}, {}
    for k in range(n_sites):
        sites[f"s{k:02d}"] = (rng.uniform(5, 95), rng.uniform(5, 95))
        fixed[f"s{k:02d}"] = rng.uniform(9000, 16000)
        cap[f"s{k:02d}"] = rng.uniform(350, 550)
    cost = {}
    for i, (cx, cy) in customers.items():
        for j, (sx, sy) in sites.items():
            cost[i, j] = 1.6 * math.hypot(cx - sx, cy - sy)  # $ per unit
    return fixed, cap, demand, cost


if __name__ == "__main__":
    fixed, cap, demand, cost = demo_instance()

    lp_weak = solve(build_cflp(fixed, cap, demand, cost, strong=False, relax=True))
    lp_strong = solve(build_cflp(fixed, cap, demand, cost, strong=True, relax=True))

    mip = build_cflp(fixed, cap, demand, cost, strong=True)
    z = solve(mip)

    print("CFLP demo: 20 candidate depots, 80 customers")
    print(f"LP bound, weak formulation   : {lp_weak:12.2f}")
    print(f"LP bound, strong formulation : {lp_strong:12.2f}")
    print(f"MIP optimum                  : {z:12.2f}")
    print(f"root gap closed by VUB cuts alone: "
          f"{100 * (lp_strong - lp_weak) / (z - lp_weak):.1f}%")

    opened = [j for j in fixed
              if (mip.variablesDict()[f"open_{j}"].value() or 0) > 0.5]
    util = {j: sum((mip.variablesDict()[f"flow_{i}_{j}"].value() or 0)
                   for i in demand) / cap[j] for j in opened}
    print(f"depots opened: {len(opened)}")
    for j in sorted(opened):
        print(f"  {j}: utilization {100 * util[j]:5.1f}%")
