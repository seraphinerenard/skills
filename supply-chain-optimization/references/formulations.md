# Archetype formulations

Full mathematical statements for the six archetypes summarized in SKILL.md, with the formulation-strength arguments that decide whether an instance solves in seconds or hangs. Notation: sets in capitals, parameters in lower case, decision variables `x, y, z, I`. All models minimize cost unless stated. Sources for every named result live in [sources.md](sources.md).

## Facility location and network design

Sets: candidate facilities `J`, customers `I`. Parameters: fixed opening cost `f_j`, capacity `K_j`, demand `d_i`, unit flow cost `c_ij` (a rated freight matrix on real engagements; demand-weighted distance only for prototyping).

```
min   sum_j f_j y_j + sum_{i,j} c_ij x_ij
s.t.  sum_j x_ij = d_i                       for all i     (demand met)
      sum_i x_ij <= K_j y_j                  for all j     (capacity + linking)
      x_ij <= min(d_i, K_j) y_j              for all i, j  (VUB, strong form)
      x >= 0, y in {0,1}
```

The weak formulation omits the variable-upper-bound (VUB) row. Both describe the same integer feasible set; the strong one has a much tighter LP relaxation because the weak LP can open a facility fractionally (`y_j = sum_i x_ij / K_j`) and pay a fraction of `f_j`. On the 20-site, 80-customer demo in `assets/facility_location.py` the weak LP bound is 67,412, the strong LP bound is 81,057, and the MIP optimum is 81,057: the VUB rows close 100% of the root gap on that instance. The strong form carries `|I| x |J|` extra rows; for very large instances add the VUB rows lazily as cuts or use a solver's built-in cut generation before paying for them all upfront.

Variants that change the mathematics, worth recognizing in the client's language:

- Single sourcing ("each store gets one depot") turns `x_ij` into binary assignment with `x_ij <= y_j` and `sum_j x_ij = 1`, demand scaling the capacity row. This is a generalized assignment structure and is markedly harder; keep flows continuous unless the client's operations genuinely require single sourcing.
- Fixed facility count (p-median) replaces `f_j` with `sum_j y_j = p`. Symmetric costs invite symmetry breaking (order the `y_j` of identical candidates).
- Multi-period network design adds open/close transitions `y_jt >= y_j,t-1 - z_jt` style rows and one-time closing costs. The LP stays tight if VUBs are indexed by period.
- Echelons (plants to DCs to customers) add flow-balance rows at intermediate nodes. Balance rows keep the model a min-cost-flow skeleton plus binaries; report flows per echelon so the client can audit lane by lane.

## Capacitated lot sizing

Big-bucket CLSP: products `i` share one resource across periods `t`. Parameters: demand `d_it`, capacity `C_t` (hours), run rate `a_i` (hours per unit), setup time `st_i`, setup cost `sc_i`, holding cost `h_i`.

```
min   sum_{i,t} sc_i y_it + h_i I_it
s.t.  I_i,t-1 + x_it - I_it = d_it           (flow balance)
      x_it <= M_it y_it                       (setup forcing)
      sum_i (a_i x_it + st_i y_it) <= C_t     (capacity)
      x, I >= 0, y in {0,1}
```

The tight forcing constant is `M_it = min( sum_{u>=t} d_iu , (C_t - st_i)/a_i )`: producing beyond remaining horizon demand loses money under positive holding cost, and producing beyond post-setup capacity is infeasible. On the 4-product, 12-week demo in `assets/clsp.py` the loose big-M (total horizon demand) gives an LP bound of 456 against a MIP optimum of 12,702, while the tight `M_it` lifts the bound to 5,956, closing 44.9% of the root gap before any branching. Two further tightenings are standard when instances stall:

- The facility-location (or shortest-path) reformulation splits `x_it` into `w_ist`, the quantity produced in `t` to serve demand in `s >= t`. Its LP relaxation equals the convex hull for the uncapacitated single-item case (Krarup and Bilde), and in practice it closes most of the remaining CLSP gap at the price of `O(|I| |T|^2)` variables.
- `(l, S)` valid inequalities added as cuts give a similar effect without the variable blowup; modern solvers derive flow-cover cuts that partially substitute.

Extensions clients actually ask for, in increasing order of pain:

- Setup carryover (linked lot sizing): a binary `w_it` carries a live setup across the bucket boundary, saving `st_i` and `sc_i` when the same product continues. Adds rows `w_it <= y_i,t-1 + w_i,t-1` and a single-carryover row per period.
- Sequence-dependent changeovers (CLSD): changeover cost `sc_ij` depends on the pair. The model now embeds a sequencing decision per bucket; formulations add flow variables `z_ijt` (product `i` followed by `j` in `t`) with degree and subtour-elimination rows. Past roughly 10 products per bucket, hand the sequencing layer to CP-SAT or a rolling heuristic and keep the MILP for lot sizes.
- Small-bucket models (DLSP, PLSP) discretize time so each bucket holds at most one or two products. They linearize sequencing at the cost of many more periods; they suit process industries with long campaigns.

Backlogging adds `B_it` with cost in the balance row; overtime adds a priced slack on the capacity row. Both are also the correct elastic variables for infeasibility diagnosis (see SKILL.md on infeasibility).

## Blending

Choose input quantities `x_r` of raws (cost `c_r`, quality attributes `q_ra`) to make blends meeting attribute windows at minimum cost:

```
min   sum_r c_r x_r
s.t.  sum_r x_r = Q                                  (batch size)
      lo_a * Q <= sum_r q_ra x_r <= hi_a * Q         (attribute windows)
      avail_r >= x_r >= 0
```

The ratio constraint "attribute a of the blend between lo and hi" is linear once multiplied through by batch size; leaving it as a ratio makes the model nonlinear for no reason. Two traps:

- Pooling. The moment blended intermediates flow into further blends through shared tanks, the attribute of the pool becomes a variable multiplying a flow variable, the problem turns bilinear and nonconvex, and LP pricing logic stops applying. Recognize it early (shared tanks, reblending) and either fix pool qualities operationally, discretize them, or move to a global solver; HiGHS does not solve pooling.
- Attribute nonlinearity. Some qualities (viscosity, octane in some ranges) blend nonlinearly in volume; refiners use blending indices that restore linearity. Ask the process engineer for the index before modelling the raw attribute.

Feed, fuel, fertilizer, and food-recipe problems are all this model, usually with integer batch counts or minimum-lot rows added, which is when the LP becomes a MILP and formulation strength starts to matter again.

## Cutting stock and column generation

The one-dimensional problem: stock lengths `s` (length `L_s`, cost `c_s`), products `i` (length `l_i`, demand `d_i`), saw kerf `k`. A pattern `p` for stock `s` is an integer vector `a_ip` with `sum_i (l_i + k) a_ip <= L_s + k`.

The compact (Kantorovich) formulation indexes stock pieces explicitly and has a notoriously weak LP bound plus heavy symmetry (every piece is interchangeable); avoid it. The Gilmore-Gomory pattern formulation is the workhorse:

```
Master:   min  sum_p c_{s(p)} z_p
          s.t. sum_p a_ip z_p >= d_i    for all i    (duals pi_i)
               z_p >= 0
```

Column generation loop, as implemented in `assets/cutting_stock.py`:

1. Seed the restricted master with one single-product pattern per product so it is feasible.
2. Solve the master LP; read duals `pi_i`.
3. For each stock length solve the pricing problem `max sum_i pi_i n_i` subject to `sum_i (l_i + k) n_i <= L_s + k`, an unbounded integer knapsack. The reduced cost of the best pattern is `c_s - value`; add every pattern with negative reduced cost.
4. Stop when no stock length prices out. The master LP value is now a valid lower bound for the full integer problem.
5. Integerize: flip the generated columns to integer and re-solve the restricted master as a MIP. This is a heuristic (the integer optimum might need a column the LP never generated), so report the LP-to-MIP gap. On lumber-scale instances the gap is routinely zero or one stock piece; the demo instance closes at 0.00% with 10 columns after 4 pricing rounds and a 96.0% length yield.

Derivation of the pricing objective: the reduced cost of column `p` is `c_s - sum_i pi_i a_ip`; minimizing it over feasible patterns is the stated knapsack. Solve the knapsack by dynamic programming over the length grid in exact material units (eighths of an inch for dimensional lumber, so a 92-5/8 in precut stud is the integer 741) because floating-point capacities silently admit patterns the saw cannot cut.

Kerf enters as `l_i + k` per piece against capacity `L_s + k`, which credits the final piece's kerf back; trim-end allowances subtract from `L_s` directly. Two-dimensional (panel) cutting changes the pricing problem to 2D knapsack with guillotine constraints and gets hard fast; for panel work use a staged-cut heuristic for pricing and accept a weaker bound.

The price-directed variant lumber planners ask for ("what should we cut, given prices") keeps the same pricing loop: make the demand rows ranged, `commit_i <= sum_p a_ip z_p <= cap_i`, and maximize `sum_i r_i (sold_i) - sum_p c_{s(p)} z_p` with a sales variable linked to production. Duals from the ranged rows drive the identical knapsack. Demand caps `cap_i` and prices `r_i` come from the demand-forecasting and price-forecasting skills; with quantile demand forecasts, solve the newsvendor-style trade per product to set `cap_i` (see [inventory-theory.md](inventory-theory.md)).

Random yield is the honest complication in sawmilling: a log class yields a distribution over product baskets, so upstream of the trim saw the "pattern" is stochastic. Planning practice builds a yield matrix per log class (from scanner history or sawing simulation) and plans on expected yield with safety stock on the products, or goes to two-stage stochastic programming when grade uncertainty is the economic core (see [uncertainty.md](uncertainty.md) and the Kazemi Zanjani sawmill papers in sources).

## Shift scheduling

The set-covering form (Dantzig) enumerates legal shift or tour patterns `p` with cost `c_p` and coverage `a_tp` (pattern `p` covers period `t`):

```
min   sum_p c_p z_p
s.t.  sum_p a_tp z_p >= r_t     for all periods t   (required heads)
      z_p integer >= 0
```

Enumerate patterns when the rule set is compact (start times x lengths x break placements often lands in the hundreds or low thousands); generate columns when rules explode. The LP bound is strong and the rounding gap small, so this formulation has survived since 1954. Assignment of named people to the chosen anonymous shifts is a second stage; individual-level rules (skills, rest chains, preferences, fairness) push that stage to CP-SAT, which handles dense boolean rule sets far better than a MILP with big-M rows (see the solver table in SKILL.md).

## Transportation and flow

The transportation LP, transshipment, and min-cost flow share one property that changes engagement economics: with integer supplies, demands, and capacities, the constraint matrix is totally unimodular, so the LP optimum is integral without any branching. Solve them as pure LPs at any scale; HiGHS handles millions of arcs. The property dies when you add fixed charges per lane, lane minimums, or multicommodity capacity sharing; each of those turns the model into a MILP and the formulation-strength playbook above applies again (fixed-charge lanes want VUB-style forcing rows with tight lane capacities).

Worth memorizing for network sanity checks: total supply short of total demand means the model needs a dummy source with shortage pricing before the solver sees it; silent infeasibility here is the most common first-run failure in freight models.
