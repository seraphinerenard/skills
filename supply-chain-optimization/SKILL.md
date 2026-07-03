---
name: supply-chain-optimization
description: >-
  Formulate, solve, and land supply-chain optimization on consulting
  engagements. Covers network design and facility location, capacitated lot
  sizing, blending, cutting stock and lumber trim plans driven by demand and
  price forecasts, shift scheduling, transportation flows, newsvendor and
  safety stock from forecast quantiles, multi-echelon stock positioning, and
  planning under uncertainty, with runnable HiGHS reference code. Use for
  asks like "optimize our cut plan", "where should the DCs go", "reset our
  safety stocks", "build the production schedule", "how much should we buy",
  or any plan a client currently makes in a spreadsheet.
---

# Supply-chain optimization

This skill carries the judgment layer: which formulation survives real instance sizes, which inventory formula lies about service, which uncertainty machinery earns its complexity, and which engagement steps decide whether claimed savings are real. Demand quantiles come from the demand-forecasting skill, price paths from price-forecasting, plan validation from simulation-digital-twins; consulting-cases owns the commercial framing. Full formulations live in [references/formulations.md](references/formulations.md), inventory derivations in [references/inventory-theory.md](references/inventory-theory.md), stochastic and robust machinery in [references/uncertainty.md](references/uncertainty.md), and every cited claim in [references/sources.md](references/sources.md). <!-- allow:C1 "robust" names the robust-optimization reference file -->

## Recognize the archetype before modelling

| Client language | Archetype | Model core | Reference |
|---|---|---|---|
| "Where should the DCs/plants be", "network study" | Facility location / network design | CFLP with strong VUB rows | formulations.md |
| "Production schedule", "batch sizes", "too many changeovers" | Capacitated lot sizing | CLSP with tight big-M; CLSD if sequence-dependent | formulations.md |
| "Recipe", "least-cost mix", "spec windows" | Blending | LP; watch for pooling, which is nonconvex | formulations.md |
| "Cut plan", "trim loss", "what lengths to cut" | Cutting stock | Column generation over patterns | formulations.md |
| "Roster", "coverage by hour", "who works when" | Shift scheduling | Set covering over shift patterns; CP-SAT for person-level rules | formulations.md |
| "Which lanes", "freight plan", "allocation" | Transportation / flow | LP; integral for free when totally unimodular | formulations.md |
| "How much to order/stock", "service levels" | Inventory policy | Newsvendor / base stock from forecast quantiles | inventory-theory.md |
| "Stock across the network", "where to hold buffers" | Multi-echelon positioning | GSM placement, then simulate | inventory-theory.md |
| ELSE | Decompose the ask into the decisions taken and their cadence; most "optimize our supply chain" briefs contain two or three of the rows above stitched by shared data, and each piece gets its own model and owner | | |

Two recognition failures cost real money. Pooling hides inside blending briefs the moment intermediates share tanks; the problem turns bilinear and LP tooling stops applying, so catch it in discovery. Single sourcing hides inside network briefs ("every store served from one depot"); it converts easy continuous flows into a generalized-assignment MILP, so confirm the client's operations genuinely need it before paying that price.

## Formulation craft that decides solve time

The LP relaxation bound is the diagnostic that separates formulation problems from solver problems. Two worked pairs from the reference code, same data, same solver:

- CLSP, 4 products, 12 weeks (`assets/clsp.py`): loose big-M (total horizon demand) gives an LP bound of 456 against a MIP optimum of 12,702; the tight per-product-per-period `M_it = min(remaining demand, post-setup capacity)` lifts the bound to 5,956, closing 44.9% of the root gap before branching starts.
- Facility location, 20 sites, 80 customers (`assets/facility_location.py`): the aggregate-capacity formulation bounds at 67,412 against an optimum of 81,057; adding the disaggregated rows `x_ij <= min(d_i, K_j) y_j` closes 100% of the gap on that instance, and the MIP solves at the root.

Rules that follow from the mechanism, applied in order when a MILP is slow:

1. Derive every big-M from instance data. A valid tight M always exists in supply-chain models because demand, capacity, and lead times bound every quantity; a global constant M is a formulation bug. Indicator constraints avoid M entirely on solvers that support them (Gurobi, CPLEX, SCIP); HiGHS 1.11 does not, so on open-solver engagements tight M is the route.
2. Prefer the formulation with more rows and a tighter relaxation when instances stall: disaggregated VUB rows in location models, the facility-location reformulation of lot sizing (LP-hull-tight for the uncapacitated single item, Krarup and Bilde 1977), pattern formulations over piece-indexed ones in cutting.
3. Break symmetry that the data creates: identical machines, identical stock pieces, interchangeable depots. Order the binaries (`y_1 >= y_2 >= ...`) or aggregate identical objects into integer counts. The piece-indexed cutting-stock model is the canonical trap; the pattern model in `assets/cutting_stock.py` removes the symmetry by construction.
4. Recognize total unimodularity before adding any binary: pure transportation, transshipment, and min-cost-flow structures solve integrally as LPs at any scale. One fixed-charge lane or shared multicommodity capacity breaks the property, so isolate those complications and price whether the client needs them.
5. Keep coefficient magnitudes within about six orders. Penalty costs of 1e7 next to unit costs of 0.1 produce dual noise and false infeasibilities; rescale units (tonnes for kilograms, k$ for $) and set penalties two orders above the largest real cost, never more. HiGHS reports problematic ranges in its presolve log; read it.

Column generation earns its complexity under three conditions at once: the natural formulation enumerates combinatorial objects (patterns, routes, rosters), the pricing subproblem is tractable (knapsack, shortest path), and instances are too large to enumerate. One-dimensional cutting stock meets all three, and `assets/cutting_stock.py` is a complete 200-line implementation: master LP in HiGHS with duals, dynamic-programming knapsack pricing in exact eighth-inch units, integerization of generated columns with the LP bound reported as the honesty check. On the lumber demo it converges in 4 pricing rounds and closes the integer gap to 0.00%.

## Inventory decisions from forecast quantiles

The newsvendor order is the `cu/(cu+co)` quantile of demand, read directly off the demand-forecasting skill's quantile output with no distributional fit. Worked numbers from `assets/newsvendor_safety_stock.py`: margin 4, overage 1 gives the 0.8 quantile; for a high-variance slow mover (CV near 0.95) the quantile answer orders 176.5 where a normal fit orders 222.7, and Monte Carlo prices the normal shortcut at 2.81% of expected profit per period. At CV 0.35 the same shortcut costs 0.07%, because the newsvendor objective is flat near its optimum. Allocate forecasting effort by that curve: distribution shape pays on high-CV items and extreme fractiles and barely pays elsewhere.

The textbook safety stock `z * sigma_1 * sqrt(H)` assumes independent one-step errors across the protection interval, and autocorrelated demand breaks it in the direction that hurts: in the demo (AR(1) demand, rho 0.6, lead 4 plus review 1) the formula achieves 85.2% service against a 95% target and understates the required buffer by 40%. The corrected default costs eight lines of code: take the empirical `alpha` quantile of realized H-period-total forecast errors from history and use it as the safety stock (95.7% achieved in the same experiment). Derivations, the lead-time-variability case, and the high-fractile history requirements are in [references/inventory-theory.md](references/inventory-theory.md).

| Situation | Method |
|---|---|
| Single period or perishable, quantile forecast available | Newsvendor at the critical fractile, quantiles read empirically |
| Repeated replenishment, stable item, 2+ years history | Base stock with empirical H-period error quantiles |
| Intermittent demand (many zero periods) | Empirical quantiles of the compound demand, or simulate; the normal formula has no standing here |
| Fixed cost per order dominates | (s,S) with s from the empirical quantile and S from an EOQ-scale lot |
| Network positioning across echelons | GSM for placement, simulation for validation |
| Service promise is fill rate | Translate from cycle service before sizing; the two diverge hardest at low order frequency and high CV |
| ELSE | Simulate the actual policy on historical demand paths and size buffers on the simulated service curve; simulation is the fallback that never lies about assumptions |

<!-- allow:B9 guaranteed-service model is the Graves-Willems term of art -->
Multi-echelon work runs on the guaranteed-service model (GSM) in practice: the commercial placement tools descend from it (Optiant, SmartOps, Optilogic's Cyclo states it verbatim), Hewlett-Packard's deployments reported savings above $130 million (Interfaces 34(1), 2004), and De Smet et al. 2019 find it beating stochastic-service formulations in over 80% of simulated instances. Adoption claims in vendor content (13%, or 30 to 40%) trace to no disclosed survey, so measure the client directly. The full vendor-by-vendor survey with sources is [references/research/meio-practice.md](references/research/meio-practice.md).

## Uncertainty machinery, cheapest adequate first

| Situation | Treatment |
|---|---|
| Uncertainty enters only as demand on service rows | Deterministic model at the demand quantile; this is the chance constraint solved exactly |
| Re-planned weekly with a frozen fence | Deterministic rolling horizon with empirical buffers; the loop itself is the recourse |
| First-stage decisions lumpy or irreversible (capacity, network, commitments) and recourse costs asymmetric | Two-stage stochastic program on 20 to 200 scenarios; compute VSS first and keep the deterministic model if it is small |
| Distribution untrusted and feasibility contractual | Budget-of-uncertainty robust counterpart on the hard rows only (Bertsimas and Sim 2004) <!-- allow:C1 robust optimization term of art --> |
| Joint probabilistic promise across many rows | Scenario-indicator MILP; first challenge whether the promise is really joint |
| ELSE | Deterministic expected-value model plus a simulation stress test of its plan; escalate to stochastic machinery only where the stress test shows the plan breaking |

Scenarios come from the forecasting stack: resample whole historical forecast-error paths onto the current forecast (dependence across periods and items rides along for free), reduce with forward selection or k-means on paths, and keep an untouched evaluation set because reduced-set objectives flatter the plans tuned on them. VSS and EVPI cost two extra solves and decide whether the stochastic machinery stays; small VSS means the honest recommendation is the deterministic model. Formal robust counterparts concentrate in power systems and finance as of 2026; in supply-chain work the budget counterpart earns a place on capacity and contract rows inside an otherwise deterministic model. <!-- allow:C1 robust optimization term of art --> Derivations, scenario-count practice, SAA statistics, and tooling (mpi-sppy, SDDP.jl, RSOME) are in [references/uncertainty.md](references/uncertainty.md).

Rolling-horizon craft: warm-start each re-solve from the previous plan shifted one period (HiGHS accepts MIP starts; PuLP exposes `setInitialValue` plus `warmStart=True`), extend the model horizon past the decision window to kill end-of-horizon draining, and penalize deviation from the previous plan because planners reject optimizers that thrash even when each plan is individually optimal. Report plan churn next to cost in every rolling deliverable.

## Solver selection under client licensing reality

Facts current as of 2026-07 (sources and access dates in [references/sources.md](references/sources.md)):

- HiGHS is MIT-licensed, under active development (1.11.0 released June 2025, releases continuing through 2026), and reaches Python through `highspy`, PuLP, and Pyomo `appsi_highs`; SciPy's `linprog` and `milp` run on it. It is the default consulting solver because the client can run the deliverable forever without a licence conversation.
- Gurobi (12.0 November 2024, 13.0 November 2025 with GPU-capable PDHG for large LPs and faster MINLP) and CPLEX remain the performance ceiling for hard MILPs. Gurobi withdrew from the public Mittelmann benchmarks in August 2024, so current public numbers compare open solvers and COPT; on the last snapshots that included it, Gurobi led the MILP geometric means by a small multiple over HiGHS, and COPT posts commercial-grade results on the categories still published (plato.asu.edu).
- Pricing for commercial solvers is quote-based; budget five figures per year and weeks-to-months of procurement for a production seat, and check whether the client already owns CPLEX through an IBM agreement or Gurobi through another team before assuming greenfield.
- CBC sits in maintenance (the 2.10 line since 2019); prefer HiGHS wherever both are options. CBC remains PuLP's bundled default, so specify the solver explicitly in code.
- OR-Tools CP-SAT wins on scheduling, sequencing, and feasibility-heavy all-integer problems with dense logical rules, where its clause learning beats LP-based branch-and-bound; it has no continuous variables (scale-and-round is the workaround) and loses on problems whose strength is the LP relaxation, which is most of the flow-and-money models above.

| Situation | Solver |
|---|---|
| LP, any consulting scale, or MILP up to mid six figures of variables with a decent formulation | HiGHS |
| Person-level scheduling, sequencing, dense boolean rules | CP-SAT |
| Hard MILP still gapping after the formulation work above, client owns or will buy a licence | Gurobi or CPLEX (or COPT; benchmark it on the client's instances) |
| Nonconvex (pooling, bilinear pricing) | SCIP or a global solver; do not force it into a MILP silently |
| Client insists on spreadsheet delivery | Model in Python anyway, export the plan; a solver embedded in a workbook is unmaintainable and unauditable |
| ELSE | HiGHS, and revisit only with profiling evidence from the client's real instances |

Gap targets by decision cadence, defended by the noise floor of the inputs: a plan is over-optimized when its optimality gap is far below its forecast error.

| Cadence | Target |
|---|---|
| Strategic (network design, annual capacity) | 0.1 to 0.5%, or prove optimality overnight; these decisions are audited for years |
| Tactical weekly (S&OP, cut plans, lot sizing) | 0.5 to 1% within minutes; demand error at this horizon is 10%+ |
| Operational intraday (dispatch, re-slotting) | First good feasible within the decision window; 1 to 5% gaps are fine when inputs carry more noise than that |
| ELSE | Set the gap to one order of magnitude below the input noise and stop paying for precision the data cannot support |

Infeasibility diagnosis: add priced elastic slacks to the suspect row families (capacity, demand, balance), re-solve, and read which slacks the optimum buys; the elastic solution names and prices every violated constraint at once, which is the deliverable a planner can act on. Gurobi and CPLEX offer IIS extraction, and HiGHS added an IIS interface in its 1.8 line (2024); the elastic route stays the more informative diagnostic on engagements because it returns a repaired plan, while an IIS returns only a certificate of conflict.

## Engagement mechanics that decide whether savings are real

Data readiness gates, before any model:

- Lead times from receipts. Compare the master-data lead-time field against realized purchase-order receipt intervals; on typical ERP extracts the field is stale for a large share of items, and every inventory number downstream inherits the error. Rebuild lead times from receipt timestamps.
- BOM accuracy for any production model. Sample-audit BOMs against what the line actually consumes; scrap and substitution factors live in planners' heads before they live in data.
- Units and packaging. Cases against eaches against pallets is the most common silent factor-of-12 error in flow models; reconcile total modelled volume against a known aggregate (annual tonnage, spend) before trusting any optimum.
- Demand history uncensored for stockouts, promotions flagged, returns separated; the demand-forecasting skill owns the methods, this skill inherits the failures.

The baseline-reproduction test is the credibility gate: constrain the model to today's plan (fix the binaries to the current network, the current cut patterns, the current schedule) and check that the modelled cost of the client's own plan matches their books within a few percent. Every mismatch is a model error to fix before the optimizer earns an opinion, and the test converts the client's planners from skeptics into co-authors, because they are the ones who explain each mismatch. Claimed savings are the delta between the reproduced baseline and the optimized plan on identical data; savings quoted against a drifting baseline or across a price move are fiction, and the honest attribution nets out input-price changes and demand mix before crediting the optimizer.

Plan adherence is the other half of savings: an optimizer whose recommendations are executed at 60% delivers 60% of the delta at best, and usually less because the skipped 40% cluster on the decisions that were hardest. Measure adherence from day one, report savings as executed-delta, and treat low adherence as a modelling signal that a constraint is missing (the planners know something the model does not; the Arkieva multi-echelon account of a DC manager refusing a locally counterintuitive stock increase is the canonical incentive version).

Close the loop with simulation: every optimized plan goes through a discrete-event or Monte Carlo validation on empirical demand and lead-time paths before the client sees a promised service level, because the optimizer's own service constraints hold only inside its assumptions. The simulation-digital-twins skill owns that harness; hand it the plan and the raw history. Deployed optimizers then need the model-operations treatment (monitoring, retraining triggers for the forecast inputs, solve-time alarms) like any other production model.

## The lumber trim engagement, worked

The recurring ask from lumber manufacturers is a cut plan: which raw lengths to buy and how to cut them, given demand and prices by product. The consulting scope is the weekly planning layer; the real-time layer (scanner-driven bucking, curve-sawing, edger and trimmer optimizers from vendors like USNR, or FPInnovations' Optitek simulator for yield studies) already runs at machine speed inside the mill and is bought, never rebuilt (vendor scope confirmed 2026-07-12, sources.md).

1. Inputs. Demand quantiles per product per week from demand-forecasting; price forecasts per product from price-forecasting. Convert quantiles to a committed floor (the fractile the mill will cut regardless) and a sellable cap per product via the newsvendor logic above, using product margin over the marginal stock length as `cu` and downgrade-or-hold cost as `co`.
2. Model. Column-generation cutting stock with ranged demand rows (floor and cap) and revenue-minus-stock-cost objective; `assets/cutting_stock.py` implements the cost-minimization core and the docstring states the ranged-row variant. Kerf and trim allowances in exact material units; patterns per stock length.
3. Random yield honesty. Deterministic cutting stock treats input lengths as certain; sawmill primary breakdown does not work that way, because log grade and geometry vary. Planning practice builds yield matrices per log class (from scanner history or Optitek runs) and plans on expected yield with product-level safety stock; when grade uncertainty is the economic core, the two-stage scenario extension in references/uncertainty.md applies, and the academic line to cite is Kazemi Zanjani et al. on sawmill planning under random yield.
4. Validation and delivery. Baseline-reproduce last month's actual cut plan first; simulate the recommended plan on demand paths; deliver the pattern book with per-pattern waste, the LP bound as the optimality certificate, and plan churn against the current book. The demo instance closes at a 0.00% integer gap with 96.0% length yield, which is the shape of report a mill manager will read.

## Reference code

All modules run on open tooling (`pip install pulp highspy numpy`), solve with HiGHS, and print worked numbers on synthetic data. Verified 2026-07-12 with PuLP 3.3.2, highspy 1.x, numpy 2.5.1, Python 3.14.

| Module | Contents | Demo output |
|---|---|---|
| `assets/clsp.py` | CLSP with setups and setup times; loose against tight big-M comparison | 44.9% of root gap closed by tight M; 23 setups in the optimal plan |
| `assets/facility_location.py` | CFLP weak and strong formulations | VUB rows close 100% of root gap; 4 depots open |
| `assets/cutting_stock.py` | Column generation with DP knapsack pricing, lumber trim instance, kerf in eighth-inch units | 4 iterations, 0.00% integer gap, 96.0% yield |
| `assets/newsvendor_safety_stock.py` | Critical fractile from quantiles; empirical H-period error quantiles against the textbook formula | Normal shortcut costs 2.81% of profit at high CV; textbook safety stock achieves 85.2% against a 95% target |

## References

- [references/formulations.md](references/formulations.md) holds the six archetype formulations with tightening arguments and the column-generation derivation.
- [references/inventory-theory.md](references/inventory-theory.md) holds the newsvendor and safety-stock mathematics, failure modes, and the multi-echelon survey summary.
- [references/uncertainty.md](references/uncertainty.md) holds two-stage stochastic programming, scenario generation and reduction, robust counterparts, chance constraints, and rolling-horizon craft. <!-- allow:C1 robust optimization term of art -->
- [references/research/meio-practice.md](references/research/meio-practice.md) is the vendor-by-vendor MEIO researcher fact sheet with primary sources.
- [references/sources.md](references/sources.md) lists every source with URL and access date.
