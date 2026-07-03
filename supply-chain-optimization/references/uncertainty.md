# Optimization under uncertainty

Mathematics and craft behind the uncertainty decision table in SKILL.md. The ordering principle for engagements: a deterministic model with correctly sized buffers wins most of the value, scenario analysis on that model wins most of the rest, and a full stochastic program earns its complexity only when first-stage decisions are lumpy or irreversible and recourse costs are asymmetric. Sources in [sources.md](sources.md).

## Two-stage stochastic programs

General form, with first-stage decisions `x` (capacity, network, commitments) fixed before uncertainty `xi` realizes and recourse `y` chosen after:

```
min  c'x + E_xi[ Q(x, xi) ]
Q(x, xi) = min { q(xi)' y : W y = h(xi) - T(xi) x, y >= 0 }
```

With a finite scenario set `{xi_s, p_s}` this is one large LP or MILP (the deterministic equivalent): replicate the recourse variables per scenario and weight recourse costs by `p_s`. The newsvendor is the smallest instance (one first-stage variable, recourse is selling and salvaging), so quantile logic keeps reappearing at larger scale. A scenario CLSP keeps `y_it` and setup structure first-stage and lets production or inventory recourse vary by scenario when the client can retime lots inside the frozen fence.

Diagnostics worth computing on every stochastic engagement because they are cheap and decide whether the machinery stays:

- EVPI (expected value of perfect information): solve each scenario to optimality separately, average, subtract from the stochastic optimum. Small EVPI means uncertainty barely matters here.
- VSS (value of the stochastic solution): fix the first stage to the expected-value model's answer, evaluate it across scenarios, compare with the stochastic optimum. Small VSS means the deterministic model plus buffers was already adequate, and the honest recommendation is to keep it. Definitions and properties are textbook material (Birge and Louveaux, Introduction to Stochastic Programming, 2nd ed., Springer 2011).

Sample average approximation gives the statistical footing when scenarios are sampled: solving `M` replications of an `N`-scenario problem yields a lower-bound estimate with a confidence interval, and evaluating any candidate `x` on a large fresh sample yields the upper bound (Kleywegt, Shapiro, and Homem-de-Mello, SIAM J. Optimization 12(2), 2002). Report the SAA gap next to the MIP gap; clients read one number, so combine them honestly.

## Scenario generation from forecast quantiles

The demand-forecasting skill emits per-period quantile forecasts; scenarios need joint paths, and quantiles alone say nothing about dependence across periods or items. The practical hierarchy:

1. Error-path resampling (default). Keep the point forecast, collect historical multi-period forecast-error paths, add resampled whole paths to the current forecast. Dependence across periods and items rides along for free because the paths are real. This needs the same history the empirical safety-stock quantiles need (see [inventory-theory.md](inventory-theory.md)), so the data work is shared.
2. Quantile grid plus a dependence model. Sample marginals through the forecast quantile function and couple them with a Gaussian or empirical copula fitted on forecast errors. Use when history is short and the forecaster is new.
3. Parametric simulation of the demand process itself, when a fitted process (AR, croston-class intermittent, promo-response) already exists and is trusted.

Scenario counts used in planning practice sit in the tens to low hundreds for two-stage problems; past that, reduce. Forward selection under a probability metric (Dupacova, Groewe-Kuska, and Roemisch, Mathematical Programming 95, 2003; Heitsch and Roemisch, Computational Optimization and Applications 24, 2003) is the standard, and k-means on scenario paths is the workable approximation most code uses. Keep an out-of-sample evaluation set that reduction never touched, and report candidate plans against it; reduced-set objectives flatter the plan that the reduction was tuned on.

Tooling: mpi-sppy handles scenario-decomposed Pyomo models at scale (Knueven et al., Mathematical Programming Computation, 2023); SDDP.jl covers multistage problems with stagewise-independent uncertainty (Dowson and Kapelevich, INFORMS Journal on Computing, 2021). Both are open source. For two-stage models of consulting size the plain deterministic equivalent in one MILP with HiGHS is usually enough and far easier to hand over.

## Robust optimization

<!-- allow:C1 "robust optimization" is the field's proper name throughout this section -->
Use robust optimization when the client cannot or will not stand behind a distribution and feasibility matters more than expected cost: contractual service floors, capacity commitments, single-shot network decisions. The budget-of-uncertainty model (Bertsimas and Sim, Operations Research 52(1), 2004) keeps the problem linear. For a row `sum_j a_j x_j <= b` with each coefficient allowed to deviate within `[a_j - ah_j, a_j + ah_j]` and at most `Gamma` coefficients deviating adversely, the counterpart adds one dual variable per row and one per uncertain coefficient:

```
sum_j a_j x_j + Gamma z + sum_j p_j <= b
z + p_j >= ah_j u_j,   -u_j <= x_j <= u_j,   z, p_j >= 0
```

<!-- allow:C1 robustness budget is the named RO parameter -->
<!-- allow:B9 the probabilistic guarantee is the mathematical object -->
Derivation: the inner maximization over the adversary's deviation set is an LP whose dual has exactly these variables; strong duality collapses the max-min into one minimization. The guarantee scales usefully: with `Gamma` around `z_alpha * sqrt(n)` for `n` uncertain coefficients, the row holds with probability near `alpha` even though `Gamma << n`, which is the paper's "price of robustness" argument. In supply-chain terms: protect a capacity row against `Gamma = 3` of 20 suppliers slipping simultaneously and the cost premium is small; protect against all 20 and the model buys warehouses nobody needs.

<!-- allow:C1 robust optimization is the named method -->
Scope honestly: published industry deployments of formal RO concentrate in power systems and finance; in supply-chain consulting the budget counterpart earns its place on hard rows (capacity, contractual floors) inside an otherwise deterministic model, and distributionally robust variants (Wasserstein-ball DRO, Mohajerin Esfahani and Kuhn, Mathematical Programming 171, 2018) remain mostly academic as of 2026. Tooling when needed: RSOME in Python (rsome.readthedocs / xiongpengnus.github.io/rsome) models RO and DRO directly.

## Chance constraints

`P(row holds) >= 1 - eps` comes in two consulting flavours:

- Right-hand-side uncertainty only (demand on a service row). The constraint reduces to the deterministic row at the `1 - eps` demand quantile. This is the newsvendor trick again; no special machinery, and it is exactly how service levels enter MILPs cleanly.
- Coefficient uncertainty with a normal model gives `mu'x + z_{1-eps} * ||Sigma^{1/2} x||_2 <= b`, a second-order cone row. HiGHS does not solve SOCPs as of version 1.11, so either linearize (budget counterpart above, or a tangent-plane outer approximation) or move that model to a conic solver.
- Joint chance constraints ("all rows hold with 95%") need scenario indicators: binary `v_s` marks scenarios allowed to violate, `sum p_s v_s <= eps`, big-M relaxes the rows where `v_s = 1`. This is a MILP that grows hard fast; question first whether the client's promise is really joint or per-row.

## Rolling horizon, and why deterministic often survives contact

Nearly every planning model deploys inside a rolling loop: solve, freeze the near horizon, execute, re-solve next period with fresh data. The loop itself is a recourse mechanism, and it is the main reason expected-value models with empirical buffers perform close to two-stage models in re-planned settings; the stochastic model's advantage concentrates in the frozen, lumpy decisions (setups inside the fence, opened facilities, signed commitments). Budget the modelling effort by asking what is actually frozen.

Craft for the loop:

- Warm-start each re-solve from the previous plan shifted one period; on MIPs pass the previous integer solution as a start (HiGHS accepts MIP starts; PuLP exposes `setInitialValue` with `warmStart=True`). Typical effect is that the solver begins with a good incumbent and spends its budget proving or improving, which stabilizes solve times inside tight replanning windows.
- End-of-horizon distortion: a finite model empties inventories and skips setups near the horizon edge. Extend the horizon past the decision window and discard the tail, or add terminal inventory targets priced from the inventory policy.
- Plan churn is a client-relations constraint with a mathematical handle: penalize deviation from the previous plan, or hard-freeze the first `k` periods. Report churn as a metric next to cost, because planners reject optimizers that thrash even when each plan is individually optimal.
