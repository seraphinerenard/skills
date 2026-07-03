# DES output and input statistics, derived and worked

Companion to assets/mine_haulage_sim.py and assets/replication_calculator.py.
Every number labelled "demo" prints from those modules with their committed
seeds.

## Replication count

Across-replication observations X_1..X_n are IID by construction (each
replication reseeds every stream), so the plain t interval applies:

    Xbar +/- t_{n-1, 1-alpha/2} * S / sqrt(n)

Demo pilot, n = 10 replications of steady-state daily throughput:
mean 79,496 t/day, S = 2,327 t/day, so the 95 percent half-width is
2.262 x 2327 / 3.162 = 1,665 t/day.

Target half-width h* = 500 t/day. Solve the smallest n with
t_{n-1} S / sqrt(n) <= h*. The z shortcut gives (1.96 x 2327/500)^2 = 83.2,
so 84; iterating the t quantile settles at n = 86. The gap grows as the
answer shrinks: for a target that needs n around 8, the z-formula says 6,
a 30 percent understatement, because t_7 = 2.36 sits far above 1.96.

Law's relative-precision form ("within gamma of the mean") divides by |Xbar|
and tightens gamma to gamma/(1+gamma). The correction exists because the
half-width criterion is measured against the estimate while the analyst
means it against the truth; skipping it turns a nominal 5 percent into an
actual 5.26 percent (Law, 5th ed., eq. 9.1).

The sequential procedure (add replications until the interval closes) peeks
at the data, which costs coverage in principle. Measured on the demo's
synthetic stand-in (2,000 trials, target 500, sd 2,300): empirical coverage
0.955 at nominal 0.95, so the penalty is negligible at that sd-to-target
ratio; it grows when the target is loose enough that stopping happens near
the n0 floor.

Batch means is the alternative when one long run is cheaper than many
replications (steady-state only): split the post-warm-up run into 20 to 30
batches longer than the autocorrelation time and t-interval the batch means.
Fewer than 10 batches wastes information; hundreds of short batches leave
correlation between batches and the interval lies narrow.

## Common random numbers

For policies A and B compared on the same replications,

    Var(Dbar) = (sigma_A^2 + sigma_B^2 - 2 rho sigma_A sigma_B) / n

so the paired design beats independent seeding by a factor near
1/(1 - rho) when the sigmas are close. Demo measurement (7 trucks against 8,
n = 15): rho = 0.998, paired CI +/- 199 t/day against +/- 991 independent,
variance ratio 24.9x, so the paired design reaches equal precision at about
1/25th the replications.

What produces rho near 1, in order of importance:

1. Stream discipline. One named generator per stochastic process per
   replication, seeded from (replication, process name) with the policy
   absent from the seed. assets/mine_haulage_sim.py derives seeds as
   SeedSequence((BASE, rep, crc32(name))).
2. Synchronization under structural change. When policy B adds a truck,
   trucks 0..6 must consume exactly the draws they consumed under A, so the
   streams hang off the truck id and the new truck draws from a fresh
   stream. Sharing one stream across trucks breaks this: the extra truck
   shifts every later draw and rho collapses toward 0.
3. Common warm-up and horizon.

Analysis discipline: CRN correlates the arms, so two-sample intervals and
tests are invalid; analyze the paired differences. With k > 2 policies,
share the streams across all arms and report paired contrasts (Bonferroni
or Nelson's MCB when the client needs "best against the rest").

CRN sharpens differences only. Absolute levels get no help, and a CRN run
count sized for the comparison is usually too small to quote levels at the
same precision; say so in the readout.

## Antithetic variates

Pair replication draws U with 1-U (in the normal driver, Z with -Z). The
pair mean has variance sigma^2 (1 + rho)/2 with rho = Corr(f(U), f(1-U)),
and rho < 0 whenever f responds monotonically to the driving uniforms.
Measured on the Monte Carlo NPV demo (assets/monte_carlo_copula.py, a
monotone DCF): variance of the mean estimator falls 13.9x at equal n.

Boundaries that practitioners miss: antithetic pairing helps the mean, does
nothing dependable for P10/P90 (quantile estimators are order statistics,
where the pairing argument fails), and can backfire on non-monotone
responses. Inside a DES with many interacting streams the induced
correlation dilutes, so measure before promising anything; typical DES gains
are tens of percent where the copula demo's are multiples.

## Warm-up determination

Welch's procedure: run R replications (10 in the demo), record the output
series (hourly tonnes), average across replications at each hour, smooth
with a centred moving average, and pick the hour where the smoothed curve
flattens. Window guidance: start near 25 observations and keep the window
under a quarter of the run; a window that big enough to flatten everything
hides a slow drift. The demo automates the eyeball call with a rule (within
2 percent of the terminal level, held 24 h) and lands on 52 h; treat any
automated pick as a proposal and look at the curve.

MSER-5 is the alternative with the best published performance among
automated rules (Hoad, Robinson, Davies, Journal of Simulation 2010, from
the AutoSimOA project): batch the series into groups of 5, delete the
prefix that minimizes the half-width of the remainder. It needs no window
parameter, which makes it the better choice inside pipelines that rerun
without a human.

Two structural alternatives beat both rules when available: start the model
in a plausible loaded state (the demo seeds the stockpile at 20 kt for this
reason) so the transient shrinks, or run a terminating study (a shift, a
day from empty) where warm-up is part of the question and gets kept.

## Input modelling details

### The queue-contamination decomposition

Fleet-management "activity" durations frequently span queue plus service.
Diagnose by comparing the field's distribution across low-traffic and
high-traffic periods: pure service times are traffic-invariant, contaminated
ones shift right with traffic. Fix by decomposing from event states (arrive,
start-service, end-service timestamps where the FMS exposes them) or by
subtracting measured waits from cycle length. Fitting the contaminated
field, then simulating contention, double-counts congestion and freezes the
historical queueing into every scenario.

### Censored repair data

Work orders closed at shift handover truncate long repairs; open orders at
the data pull right-censor them. MLE with censoring:

```python
from scipy import stats
data = stats.CensoredData(uncensored=obs, right=open_order_ages)
shape, loc, scale = stats.lognorm.fit(data, floc=0)
```

CensoredData feeds rv_continuous.fit since SciPy 1.11. Ignoring the
censoring biases MTTR low and availability optimistic, which then inflates
every capacity estimate downstream of the failure model.
predictive-maintenance owns failure-model fitting in depth; import its
distributions directly for maintenance-scenario simulations.

### Tails on empirical distributions

The interpolated empirical CDF (assets/monte_carlo_copula.py,
EmpiricalMarginal) caps draws at the observed maximum. When the decision
hangs on the tail (blackout-length repairs, storm delays), splice a
generalized Pareto above the 90th or 95th percentile threshold and check
the mean-excess plot for threshold stability.

### Non-stationary arrivals

Thinning (Lewis and Shedler): draw candidate events from a homogeneous
process at rate lambda_max, accept each with probability
lambda(t)/lambda_max. Ten lines of code, exact, and it preserves the
peak-hour queueing that a fitted average rate erases.

## Validation following Sargent

Sargent's framework (Sargent, "Verification and validation of simulation
models", WSC tutorial series, 2010 edition) names the tests; the ones that
carry consulting weight:

| Test | Operational form on a haulage model |
|---|---|
| Historical data validation | Feed last quarter's dispatch inputs; daily tonnes within the model CI of actuals, downtime fraction within a point |
| Face validity | Shift supervisors walk the event trace or animation; they catch wrong dispatch logic in minutes |
| Extreme conditions | Zero trucks gives zero tonnes; infinite crusher moves the bottleneck to shovels; doubled MTTR cuts availability by the computable amount |
| Parameter variability | Elasticities carry the right signs and plausible magnitudes (a 10 percent faster crusher must move tonnes by less than 10 percent when trucks bind) |
| Internal validity | Across-replication spread is stable and seed changes move nothing systematic |
| Comparison to other models | Kingman/VUT queue estimates within tens of percent of simulated station queues |

Extreme-condition tests exist mainly to catch compensating errors: a load
time 15 percent slow and a haul time 15 percent fast can cancel on baseline
throughput while corrupting every fleet-size scenario. The baseline match
proves little on its own; the extremes and elasticities carry the proof.
