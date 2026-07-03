# Inventory theory as used on engagements

Derivations and worked numbers behind the inventory sections of SKILL.md. The recurring theme: the classical formulas are conditional on independence and normality assumptions that real demand series break, and the fixes are empirical quantiles and simulation. Sources in [sources.md](sources.md).

## Newsvendor

One period, order `Q` before demand `D` realizes. Underage cost `cu` per unit short (lost margin plus any penalty), overage cost `co` per unit left (cost minus salvage). Marginal analysis: the `Q`-th unit sells with probability `P(D >= Q)`, earning `cu`, and goes unsold with probability `P(D < Q)`, costing `co`. At the optimum the expected marginal profit is zero:

```
cu * (1 - F(Q*)) = co * F(Q*)   =>   F(Q*) = cu / (cu + co)
```

`Q*` is a quantile of the demand distribution, which is precisely what a quantile demand forecast provides; no distributional fit is needed. Worked numbers from `assets/newsvendor_safety_stock.py`: price 10, cost 6, salvage 5 give `cu = 4`, `co = 1`, critical fractile 0.800. For a high-variance slow mover (lognormal, median 90, CV about 0.95) the 0.8 quantile is 176.5. Fitting a normal to the same mean and standard deviation gives 222.7, an over-order of 46 units, and Monte Carlo prices the shortcut at 2.81% of expected profit per period. At moderate variance (CV 0.35) the same experiment costs only 0.07%: the newsvendor objective is flat near its optimum, so quantile precision matters at high CV and extreme fractiles and barely matters otherwise. Spend forecasting effort accordingly, and read the fractile off the forecast's empirical quantiles whenever the demand-forecasting pipeline emits them.

Two engagement-grade corrections:

- Censored demand. Sales data truncated by stockouts biases every quantile downward. Uncensor first (the demand-forecasting skill owns the methods) or the newsvendor systematically under-orders exactly where service already failed.
- Salvage below marginal production cost across many SKUs is a portfolio decision (markdown cascades, donation, disposal fees); price `co` from the realized recovery curve, since assumed salvage values are the most common silent error in retail newsvendor deployments.

## Base stock, order-up-to, and (s,S)

Periodic review with review period `R` and replenishment lead time `L`: an order placed now arrives after `L`, and the next chance to correct is `R` later, so the order-up-to level `S` must cover demand over the protection interval `H = L + R`:

```
S = E[D_H] + SS,   SS = q_alpha(D_H - E[D_H])
```

with `alpha` the target cycle-service level and `q_alpha` the error quantile. Continuous review `(s, Q)` protects over `L` only; `(s, S)` behaves like order-up-to with a reorder trigger and suits fixed-cost-per-order settings. Every formula below is about estimating that `q_alpha` of `H`-period total demand error.

## Where the textbook safety-stock formula fails

The standard formula, with `sigma_1` the one-step forecast-error standard deviation:

```
SS = z_alpha * sigma_1 * sqrt(H)
```

assumes forecast errors are independent across the protection interval, identically distributed, and normal. Each assumption fails in a specific, diagnosable way:

- Autocorrelated demand. Under AR(1) demand with coefficient `rho`, the variance of the `H`-period total is `sigma_d^2 * [H + 2 * sum_{k=1..H-1} (H - k) rho^k]` against the formula's `sigma_d^2 * H`. At `rho = 0.6`, `H = 5` the bracket is 13.08 against 5, so the true spread is 1.62 times the formula's. The demo in `assets/newsvendor_safety_stock.py` measures it: textbook safety stock 94.3 achieves 85.2% service against a 95% target, while the empirical quantile of `H`-period error (156.3, understated by the formula by 40%) achieves 95.7%. Persistent demand (trends, promotions bleeding across weeks, replenishment-driven store orders) behaves this way; positive `rho` is the norm in weekly series.
- Nonstationary demand. A formula parameterized on pooled history mixes promo and baseline weeks into one `sigma_1`; safety stock is then too high off-promo and too low on-promo. The fix is state-dependent errors: quantiles of forecast error conditional on the forecast itself (the demand-forecasting skill's quantile output already conditions on covariates).
- Lead-time variability. The compound formula `SS = z * sqrt(L * sigma_D^2 + mu_D^2 * sigma_L^2)` additionally assumes lead time independent of demand. Supplier congestion correlates them positively (busy periods lengthen lead times exactly when demand runs hot), so the formula understates again; the empirical route measures total demand over realized lead times and takes its quantile directly.
- Normality at high fractiles. At 99%+ targets the normal `z` sits far into a tail the data may not have; empirical quantiles need enough history (roughly `1/(1-alpha)` independent windows at minimum) and beyond that, fit a tail (POT/GPD) or simulate.

The corrected default, which the demo implements in eight lines: compute realized `H`-period-total forecast errors over history, take the `alpha` empirical quantile, use it as `SS`. It inherits every dependency structure in the data, including autocorrelation and forecast bias, and it needs no distributional assumption. Its cost is history length; with under two years of weekly data at 95%+, blend it with a parametric tail or simulate the demand process.

## Multi-echelon

Two framings dominate, and which one a software package implements decides what its numbers mean:

<!-- allow:B9 guaranteed-service is the term of art -->
- Guaranteed-service (GSM; Simpson 1958 for the base model, Graves and Willems 2000 for spanning-tree networks, Eruguz et al. 2016 for the survey): each stage quotes a deterministic service time to its customers; demand is bounded within the service window (formalized as a maximum reasonable demand, above which management intervenes); optimization places safety stock to minimize holding cost given quoted times. The problem becomes a combinatorial one over service times (dynamic programming on trees, MILP on general networks). Strengths: tractable at real network scale, outputs (decoupling points, quoted times) match how planners talk. Weakness: the demand-bound abstraction hides tail risk, the base model needs a spanning-tree BOM with deterministic lead times, and realized service depends on the intervention that truncates demand actually existing.
- Stochastic-service (SSM; Clark and Scarf 1960): stages hold stock against stochastic delays from upstream; echelon base-stock policies are optimal in series systems. Exact in its assumptions, and hard to scale beyond structured networks; commercial adoption is thinner.

<!-- allow:B9 guaranteed-service is the term of art -->
What the market implements, from the vendor survey in [research/meio-practice.md](research/meio-practice.md): the safety-stock-placement lineage runs on GSM. Sean Willems co-founded Optiant to commercialize the Graves-Willems model (acquired by Logility, 2010); SmartOps went to SAP (2013) and LogicTools to IBM; Optilogic's Cyclo documentation states verbatim that it "uses a Guaranteed Service Model (GSM) approach." The planning-and-forecasting vendors (ToolsGroup SO99+, GAINS, Kinaxis with the Wahupa engine) foreground probabilistic engines; SAP IBP's and Blue Yonder's exact formulations stay proprietary and publicly unconfirmed. The flagship GSM deployment is Hewlett-Packard, with savings above $130 million from the first two business deployments (Interfaces 34(1), 2004). On merit, De Smet et al. 2019 (IJPR 57(13)) find GSM beating SSM in over 80% of simulated instances with average total-cost improvement near 10% under stochastic lead times, so the GSM default is defensible on quality as well as tractability.

Adoption stays low relative to the marketing: a 13% figure (Arkieva) and a 30 to 40% figure (Sophus) both circulate and neither traces to a disclosed survey, so quote them as vendor estimates or measure the client's own network directly. Most networks still run single-echelon safety stock set node-by-node in the ERP, because legacy planning systems carry single-location logic. For benchmarking, Willems' MSOM 10(1) 2008 data set publishes 38 real multi-echelon chains, up to about 2,025 stages, as an Excel e-companion.

<!-- allow:B9 guaranteed-service is the Graves-Willems term of art -->
Practice guidance: use guaranteed-service framing for network-wide stock positioning studies (it answers "where should buffers sit"), then validate the resulting policies by simulation against the empirical demand and lead-time processes, since neither analytic framing survives autocorrelated demand, correlated lead times, or batching intact. The simulation-digital-twins skill owns that validation loop; hand it the policy parameters and the raw history, and treat simulated fill rate as the number the client gets quoted. When the network is shallow (one DC echelon, one store echelon) skip multi-echelon machinery entirely: set store-level stock from empirical quantiles as above and size the DC against the aggregated store orders, which are what the DC actually sees.

## Service-level semantics

Cycle service (probability of no stockout per replenishment cycle) and fill rate (fraction of units served from stock) diverge widely at low order frequencies and high demand variance; clients almost always mean fill rate while formulas almost always deliver cycle service. Translate before promising: for base-stock systems, expected shortfall per cycle over expected demand per cycle gives the fill-rate complement, and the empirical-quantile machinery above extends to it by averaging simulated shortfalls. Contract the metric in writing during data discovery (the discovery skill's brief has a slot for it) because a one-point fill-rate promise at 98% is a materially different stock investment from 98% cycle service.
