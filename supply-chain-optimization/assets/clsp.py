#!/usr/bin/env python3
"""Capacitated lot sizing (CLSP) with setup costs and setup times, solved with HiGHS.

pip install pulp highspy

Big-bucket CLSP: several products share one capacitated resource per period;
producing product i in period t requires a setup (binary) that consumes both
money and capacity. The demo builds one instance twice, with a loose big-M and
with the tight per-(i,t) big-M, and prints the LP-relaxation bound of each so
the formulation lesson is visible in numbers: the tight M closes most of the
root gap before branching starts.

Model (full derivation in references/formulations.md):
  min  sum_{i,t} sc_i y_it + h_i I_it
  s.t. I_i,t-1 + x_it - I_it = d_it                    (flow balance)
       x_it <= M_it y_it                               (setup forcing)
       sum_i a_i x_it + st_i y_it <= C_t               (capacity)
       x, I >= 0;  y binary
Tight M_it = min( sum_{tau>=t} d_i,tau , (C_t - st_i)/a_i ): production above
remaining demand is never optimal under positive holding cost, and production
above post-setup capacity is infeasible.
"""

from dataclasses import dataclass, field

import pulp


@dataclass
class ClspInstance:
    products: list          # product names
    periods: list           # period labels (ordered)
    demand: dict            # (i, t) -> units
    capacity: dict          # t -> hours available
    rate: dict              # i -> hours per unit
    setup_time: dict        # i -> hours per setup
    setup_cost: dict        # i -> $ per setup
    holding_cost: dict      # i -> $ per unit per period
    initial_inventory: dict = field(default_factory=dict)  # i -> units


def build_clsp(inst: ClspInstance, tight_bigm: bool = True,
               relax: bool = False) -> pulp.LpProblem:
    """Return a PuLP model; relax=True drops integrality to expose the LP bound."""
    P, T = inst.products, inst.periods
    tidx = {t: k for k, t in enumerate(T)}

    prob = pulp.LpProblem("clsp", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("prod", (P, T), lowBound=0)
    I = pulp.LpVariable.dicts("inv", (P, T), lowBound=0)
    cat = "Continuous" if relax else "Binary"
    y = pulp.LpVariable.dicts("setup", (P, T), lowBound=0, upBound=1, cat=cat)

    prob += pulp.lpSum(inst.setup_cost[i] * y[i][t] + inst.holding_cost[i] * I[i][t]
                       for i in P for t in T)

    for i in P:
        for t in T:
            prev = (inst.initial_inventory.get(i, 0.0) if tidx[t] == 0
                    else I[i][T[tidx[t] - 1]])
            prob += prev + x[i][t] - I[i][t] == inst.demand[i, t], f"bal_{i}_{t}"

            if tight_bigm:
                remaining = sum(inst.demand[i, u] for u in T if tidx[u] >= tidx[t])
                cap_room = (inst.capacity[t] - inst.setup_time[i]) / inst.rate[i]
                m = max(0.0, min(remaining, cap_room))
            else:
                m = sum(inst.demand.values())
            prob += x[i][t] <= m * y[i][t], f"force_{i}_{t}"

    for t in T:
        prob += pulp.lpSum(inst.rate[i] * x[i][t] + inst.setup_time[i] * y[i][t]
                           for i in P) <= inst.capacity[t], f"cap_{t}"
    return prob


def solve(prob: pulp.LpProblem, gap: float = 1e-4, time_limit: int = 60) -> float:
    status = prob.solve(pulp.HiGHS(msg=False, gapRel=gap, timeLimit=time_limit))
    if pulp.LpStatus[status] not in ("Optimal", "Integer Feasible"):
        raise RuntimeError(f"solver status {pulp.LpStatus[status]}")
    return pulp.value(prob.objective)


def demo_instance() -> ClspInstance:
    """Four products, 12 weekly buckets, seasonal demand, one bottleneck line."""
    import math
    products = ["A", "B", "C", "D"]
    periods = [f"w{k:02d}" for k in range(1, 13)]
    base = {"A": 90, "B": 60, "C": 40, "D": 25}
    demand = {}
    for i in products:
        for k, t in enumerate(periods):
            season = 1.0 + 0.35 * math.sin(2 * math.pi * (k + ord(i[0]) % 4) / 12)
            demand[i, t] = round(base[i] * season)
    return ClspInstance(
        products=products,
        periods=periods,
        demand=demand,
        capacity={t: 170.0 for t in periods},
        rate={"A": 0.5, "B": 0.6, "C": 0.8, "D": 1.0},
        setup_time={"A": 6.0, "B": 6.0, "C": 9.0, "D": 9.0},
        setup_cost={"A": 400.0, "B": 350.0, "C": 500.0, "D": 450.0},
        holding_cost={"A": 1.5, "B": 2.0, "C": 2.5, "D": 3.0},
        initial_inventory={"A": 90, "B": 60, "C": 40, "D": 25},
    )


def print_plan(prob: pulp.LpProblem, inst: ClspInstance) -> None:
    vals = {v.name: v.value() for v in prob.variables()}
    print(f"{'':>4}" + "".join(f"{t:>7}" for t in inst.periods))
    for i in inst.products:
        row = [(vals.get(f"prod_{i}_{t}") or 0.0) for t in inst.periods]
        row = [0.0 if abs(q) < 1e-6 else q for q in row]
        print(f"{i:>4}" + "".join(f"{q:7.0f}" for q in row))
    setups = sum(1 for i in inst.products for t in inst.periods
                 if (vals.get(f"setup_{i}_{t}", 0) or 0) > 0.5)
    print(f"setups used: {setups} of {len(inst.products) * len(inst.periods)} slots")


if __name__ == "__main__":
    inst = demo_instance()

    lp_loose = solve(build_clsp(inst, tight_bigm=False, relax=True))
    lp_tight = solve(build_clsp(inst, tight_bigm=True, relax=True))

    mip = build_clsp(inst, tight_bigm=True)
    z = solve(mip, gap=1e-4)

    print("CLSP demo: 4 products x 12 weeks, shared line")
    print(f"LP bound, loose big-M : {lp_loose:10.2f}")
    print(f"LP bound, tight big-M : {lp_tight:10.2f}")
    print(f"MIP optimum           : {z:10.2f}")
    print(f"root gap closed by tightening M alone: "
          f"{100 * (lp_tight - lp_loose) / (z - lp_loose):.1f}%")
    print()
    print_plan(mip, inst)
