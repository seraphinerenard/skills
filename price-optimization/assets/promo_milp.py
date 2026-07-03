#!/usr/bin/env python3
# pip install: numpy scipy   (scipy >= 1.9 for scipy.optimize.milp / HiGHS)
"""Promo calendar as a MILP with a same-week cannibalization matrix.

Setting: a retailer plans a 13-week quarter for one category group. Each
item-week promo has a pre-computed own incremental margin m[i, w] (volume
lift at the promo price minus the discount given away on baseline buyers,
scaled by week seasonality). Promoting two substitutes in the same week
destroys part of both lifts; that loss enters as a pairwise penalty from a
cannibalization matrix, which the retail-analytics skill measures and this
optimizer consumes.

Decision variables:
  x[i, w] in {0, 1}   promote item i in week w
  y[p, w] in [0, 1]   pair indicator for substitute pair p = (i, j)

y needs no integrality and only the lower-bound link  y >= x_i + x_j - 1:
its objective coefficient is a penalty, so the solver pushes every y to its
lower bound, where it equals the AND of the two binaries. This halves the
integer variable count versus the textbook three-inequality AND encoding.

Constraints: flyer slots per week, promo frequency cap per item, a minimum
gap between repeats of the same item (pull-forward protection), and a
discount budget.

The demo solves the MILP, prints the calendar, and evaluates the greedy
plan (rank item-weeks by own margin, ignore cannibalization) under the true
objective, so the gap the matrix is worth is a number.
"""

import numpy as np
from scipy import optimize, sparse


def build_and_solve(m, pairs, pen, slots, max_promos, min_gap, spend, budget):
    """m: (I, W) own incremental margin. pairs: list of (i, j) substitutes.
    pen: (len(pairs),) same-week cannibalization cost in dollars.
    Returns (x_opt (I, W) int array, objective value)."""
    I, W = m.shape
    P = len(pairs)
    nx, ny = I * W, P * W

    def xi(i, w):
        return i * W + w

    def yi(p, w):
        return nx + p * W + w

    # scipy.milp minimizes: negate margins, keep penalties positive.
    c = np.concatenate([-m.ravel(), np.repeat(pen, W)])
    integrality = np.concatenate([np.ones(nx), np.zeros(ny)])
    bounds = optimize.Bounds(0, 1)

    rows, cols, vals, lb, ub = [], [], [], [], []
    r = 0

    def add_row(idx, coef, lo, hi):
        nonlocal r
        rows.extend([r] * len(idx))
        cols.extend(idx)
        vals.extend(coef)
        lb.append(lo)
        ub.append(hi)
        r += 1

    for w in range(W):                                   # flyer slots
        add_row([xi(i, w) for i in range(I)], [1] * I, 0, slots)
    for i in range(I):                                   # frequency cap
        add_row([xi(i, w) for w in range(W)], [1] * W, 0, max_promos)
    for i in range(I):                                   # min gap windows
        for w in range(W - min_gap + 1):
            add_row([xi(i, w + g) for g in range(min_gap)],
                    [1] * min_gap, 0, 1)
    add_row([xi(i, w) for i in range(I) for w in range(W)],
            list(spend.ravel()), 0, budget)              # discount budget
    for p, (i, j) in enumerate(pairs):                   # y >= x_i + x_j - 1
        for w in range(W):
            add_row([xi(i, w), xi(j, w), yi(p, w)], [1, 1, -1], -np.inf, 1)

    A = sparse.coo_array((vals, (rows, cols)), shape=(r, nx + ny))
    res = optimize.milp(c, integrality=integrality, bounds=bounds,
                        constraints=optimize.LinearConstraint(
                            A, np.array(lb), np.array(ub)))
    if not res.success:
        raise RuntimeError(f"MILP failed: {res.message}")
    x = np.round(res.x[:nx]).astype(int).reshape(I, W)
    return x, -res.fun


def true_objective(x, m, pairs, pen):
    own = float((m * x).sum())
    cann = float(sum(pen[p] * (x[i] * x[j]).sum()
                     for p, (i, j) in enumerate(pairs)))
    return own, cann, own - cann


def greedy_plan(m, slots, max_promos, min_gap, spend, budget):
    """Rank item-weeks by own margin; take what fits. No cannibalization."""
    I, W = m.shape
    x = np.zeros((I, W), dtype=int)
    used = 0.0
    for i, w in sorted(np.ndindex(I, W), key=lambda t: -m[t]):
        if m[i, w] <= 0:
            break
        lo, hi = max(0, w - min_gap + 1), min(W, w + min_gap)
        if (x[:, w].sum() < slots and x[i].sum() < max_promos
                and x[i, lo:hi].sum() == 0 and used + spend[i, w] <= budget):
            x[i, w] = 1
            used += spend[i, w]
    return x


if __name__ == "__main__":
    rng = np.random.default_rng(11)
    I, W = 12, 13                       # 12 items, one quarter
    cats = np.repeat(np.arange(4), 3)   # 4 categories, 3 substitutes each

    base_units = rng.uniform(300, 1200, I)
    lift = rng.uniform(1.8, 3.2, I)                     # promo unit multiplier
    margin_base = rng.uniform(6.0, 12.0, I)             # $ per unit, shelf
    margin_promo = margin_base - rng.uniform(2.5, 5.0, I)  # after discount
    season = 1.0 + 0.35 * np.sin(np.linspace(0, np.pi, W)) \
        + (np.arange(W) == 11) * 0.5                    # week 12 spike
    m = (base_units[:, None]
         * (lift[:, None] * margin_promo[:, None] - margin_base[:, None])
         * season[None, :])
    spend = (base_units[:, None] * lift[:, None]
             * (margin_base - margin_promo)[:, None] * season[None, :])

    pairs = [(i, j) for i in range(I) for j in range(i + 1, I)
             if cats[i] == cats[j]]
    # Same-week substitute penalty: 55% of the smaller partner's own margin,
    # floored at 0 (a promo with negative m already penalizes itself).
    pen = np.array([0.55 * max(0.0, min(m[i].mean(), m[j].mean()))
                    for i, j in pairs])

    slots, max_promos, min_gap, budget = 3, 2, 4, 120_000.0

    x_opt, obj = build_and_solve(m, pairs, pen, slots, max_promos, min_gap,
                                 spend, budget)
    own, cann, net = true_objective(x_opt, m, pairs, pen)
    x_grd = greedy_plan(m, slots, max_promos, min_gap, spend, budget)
    g_own, g_cann, g_net = true_objective(x_grd, m, pairs, pen)

    print("MILP calendar (rows = items by category, cols = weeks 1-13)")
    for i in range(I):
        row = "".join(" X " if x_opt[i, w] else " . " for w in range(W))
        print(f"  cat{cats[i]} item{i:2d} |{row}")
    same_wk = sum(int((x_opt[i] * x_opt[j]).sum()) for i, j in pairs)
    print(f"\nMILP:   own ${own:12,.0f}  cannibalization -${cann:10,.0f}  "
          f"net ${net:12,.0f}  (substitute clashes: {same_wk})")
    g_same = sum(int((x_grd[i] * x_grd[j]).sum()) for i, j in pairs)
    print(f"greedy: own ${g_own:12,.0f}  cannibalization -${g_cann:10,.0f}  "
          f"net ${g_net:12,.0f}  (substitute clashes: {g_same})")
    print(f"\ncannibalization-aware MILP adds ${net - g_net:,.0f} "
          f"({100 * (net - g_net) / g_net:.1f}%) over margin-ranked greedy")
    assert abs(obj - net) < 1.0, "solver objective and audit must agree"
