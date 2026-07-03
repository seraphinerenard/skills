#!/usr/bin/env python3
"""Cutting stock by column generation (Gilmore-Gomory), lumber trim case, HiGHS.

pip install highspy

A stud mill buys raw lengths (16 ft and 20 ft here) and cuts them into
demanded products (precut studs, 8-footers, blocking). Each cutting pattern
for a stock length is a column; the restricted master LP picks pattern
quantities to cover demand at minimum purchase cost; the pricing problem per
stock length is an unbounded knapsack over the row duals, solved by dynamic
programming in exact eighth-inch units so 92-5/8 in studs stay integral.

Master LP (duals pi_i from HiGHS):
  min  sum_p cost_stock(p) z_p
  s.t. sum_p a_ip z_p >= d_i   for each product i
       z >= 0
Pricing for stock s: max sum_i pi_i n_i  s.t. sum_i (l_i + kerf) n_i <= L_s + kerf,
n_i integer >= 0. Add the pattern when cost_s minus the knapsack value < 0.
After convergence the generated columns are flipped to integer and re-solved:
the CG LP optimum is a valid lower bound on the full integer problem, the
restricted-master MIP is an upper bound, and the demo prints both plus the gap.

The same machinery handles the price-directed variant (choose WHAT to cut,
given product prices and demand caps): make demand rows ranged
(min commitment, max sellable) and put revenue minus stock cost in the
objective. See references/formulations.md.
"""

import highspy

INF = highspy.kHighsInf
EIGHTH = 8  # work in 1/8-inch integer units


def knapsack_best_pattern(duals, piece_w, capacity):
    """Unbounded knapsack by DP. Returns (value, counts per product)."""
    n = len(piece_w)
    dp = [0.0] * (capacity + 1)
    take = [-1] * (capacity + 1)
    for c in range(1, capacity + 1):
        dp[c] = dp[c - 1]
        for i in range(n):
            if piece_w[i] <= c and duals[i] > 1e-12:
                v = dp[c - piece_w[i]] + duals[i]
                if v > dp[c] + 1e-12:
                    dp[c], take[c] = v, i
    counts = [0] * n
    c = capacity
    while c > 0:
        i = take[c]
        if i < 0:
            c -= 1
        else:
            counts[i] += 1
            c -= piece_w[i]
    return dp[capacity], counts


def solve_cutting_stock(stock, products, demand, kerf_in=0.125, max_iters=200):
    """stock: {name: (length_in, cost)}; products: {name: length_in};
    demand: {name: pieces}. Returns dict of results."""
    prods = list(products)
    piece_w = [round((products[p] + kerf_in) * EIGHTH) for p in prods]
    caps = {s: round((L + kerf_in) * EIGHTH) for s, (L, _) in stock.items()}

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    for p in prods:
        h.addRow(float(demand[p]), INF, 0, [], [])

    columns = []  # (stock_name, counts)

    def add_pattern(s, counts):
        idx = [i for i, n in enumerate(counts) if n > 0]
        val = [float(counts[i]) for i in idx]
        h.addCol(stock[s][1], 0.0, INF, len(idx), idx, val)
        columns.append((s, list(counts)))

    # seed: one single-product pattern per (product, cheapest stock that fits)
    for i, p in enumerate(prods):
        fits = [(cost / (caps[s] // piece_w[i]), s) for s, (L, cost) in stock.items()
                if caps[s] >= piece_w[i]]
        if not fits:
            raise ValueError(f"product {p} fits in no stock length")
        s = min(fits)[1]
        counts = [0] * len(prods)
        counts[i] = caps[s] // piece_w[i]
        add_pattern(s, counts)

    iters = 0
    for iters in range(1, max_iters + 1):
        h.run()
        duals = list(h.getSolution().row_dual)
        new_cols = 0
        for s, (L, cost) in stock.items():
            value, counts = knapsack_best_pattern(duals, piece_w, caps[s])
            if value > cost + 1e-7:  # reduced cost of column < 0
                add_pattern(s, counts)
                new_cols += 1
        if new_cols == 0:
            break
    lp_bound = h.getObjectiveValue()

    # integerize the generated columns and re-solve as a MIP
    for j in range(len(columns)):
        h.changeColIntegrality(j, highspy.HighsVarType.kInteger)
    h.run()
    z_ip = h.getObjectiveValue()
    usage = list(h.getSolution().col_value)

    used = [(round(u), s, counts) for u, (s, counts) in zip(usage, columns)
            if u > 0.5]
    return {"lp_bound": lp_bound, "ip_cost": z_ip, "iterations": iters,
            "columns": len(columns), "used_patterns": used, "prods": prods}


def demo():
    stock = {  # length in inches, delivered cost per piece
        "16ft": (192.0, 6.40),
        "20ft": (240.0, 8.30),
    }
    products = {  # finished cut lengths, inches
        "stud_92_5/8": 92.625,   # precut stud, 8 ft wall
        "stud_104_5/8": 104.625,  # precut stud, 9 ft wall
        "plate_96": 96.0,
        "plate_120": 120.0,
        "block_46_1/2": 46.5,
    }
    demand = {"stud_92_5/8": 2400, "stud_104_5/8": 900,
              "plate_96": 1400, "plate_120": 600, "block_46_1/2": 800}

    r = solve_cutting_stock(stock, products, demand)
    print("Lumber trim demo: 2 stock lengths, 5 products")
    print(f"column generation: {r['iterations']} iterations, "
          f"{r['columns']} columns generated")
    print(f"LP lower bound : ${r['lp_bound']:10.2f}")
    print(f"integer plan   : ${r['ip_cost']:10.2f}  "
          f"(gap {100 * (r['ip_cost'] - r['lp_bound']) / r['ip_cost']:.2f}%)")

    demand_in = sum(products[p] * demand[p] for p in products)
    bought_in = sum(n * {"16ft": 192.0, "20ft": 240.0}[s]
                    for n, s, _ in r["used_patterns"])
    print(f"yield: {100 * demand_in / bought_in:.1f}% of purchased inches "
          f"become product")
    print("patterns in the plan:")
    for n, s, counts in sorted(r["used_patterns"], key=lambda t: -t[0]):
        cuts = " + ".join(f"{c}x {p}" for p, c in zip(r["prods"], counts) if c)
        print(f"  {n:5d} x {s}: {cuts}")


if __name__ == "__main__":
    demo()
