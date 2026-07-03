---
name: simulation-digital-twins
description: >
  Simulation and digital-twin work in operations consulting. Use when the task
  is to build or review a discrete-event simulation of a plant, mine, port, or
  warehouse; to debottleneck a throughput chain; to quantify capital-project or
  throughput risk with Monte Carlo; to scope, audit, or name a "digital twin";
  to calibrate a simulator against plant data; or to optimize a policy over a
  stochastic simulation (fleet sizing, buffer sizing, schedule rules).
  supply-chain-optimization owns the optimization models whose plans this skill
  stress-tests; predictive-maintenance supplies the failure models that feed
  maintenance scenarios; model-operations owns drift monitoring once a twin
  runs in production.
---

# Simulation and digital twins

The reader already knows the textbook methods. This file carries the judgment
calls, the silent errors, and the worked numbers. Every quantitative claim
below that comes from the bundled demos is reproducible: run the module named
next to it. Sources for external claims sit in references/sources.md with
access dates.

## Method selection

Pick the method from the client question, before any tooling talk. The most
common consulting failure here is a DES built for a question a queueing
formula answers in an afternoon.

| Client question | Method | Reason |
|---|---|---|
| Where does throughput die; what does the queue look like if we add a truck, a berth, a nurse | Discrete-event simulation | The answer lives in the interaction of variability, contention, and failures; averages destroy it |
| What are the P10/P50/P90 of NPV, cost, or schedule for this project | Monte Carlo on a static cash-flow or schedule model | No queueing dynamics; correlated input uncertainty dominates |
| How do competitors, customers, or infections respond to each other and to our move | Agent-based model | Interaction between heterogeneous decision-makers is the mechanism of the answer; budget double the validation time of a DES, because micro-behaviour rules resist direct measurement |
| What does this policy do over years when feedback loops and delays bite (workforce pipelines, service reputation and demand) | System dynamics | Aggregate stocks and flows with delays; the client needs loop insight, and precision below 10 to 20 percent is unattainable anyway |
| Which plan minimizes cost or maximizes service subject to constraints | Plain optimization; route to supply-chain-optimization | Deterministic structure dominates; bring the plan back here for stochastic validation |
| What will demand or price be | Route to demand-forecasting or price-forecasting | Forecasting owns the input; simulation consumes it as scenarios |
| Which setting of a few knobs is best when each evaluation is a simulation run | Simulation-optimization, section below | Noise-aware search beats grid sweeps at 20+ candidate settings |
| ELSE | Start with a queueing approximation and a spreadsheet | Kingman's VUT formula gives queue time within tens of percent for one station: Wq is roughly u/(1-u) times (ca2+cs2)/2 times service time. At u 0.85, ca2 1.0, cs2 0.5, service 2.5 min, Wq is about 0.85/0.15 x 0.75 x 2.5 = 10.6 min. If that precision answers the question, deliver it this week and skip the build |

Use the VUT number even when you do build the DES: a simulated queue time
that lands 5x away from the Kingman estimate signals a model bug or a
misread parameter long before validation formally starts.

## The twin spectrum and honest naming

Kritzinger et al. (2018, IFAC-PapersOnLine) split the space by data-flow
automation: a digital model (manual flows both ways), a digital shadow
(automatic physical-to-digital flow), and a digital twin (automatic flow in
both directions). Their review found true twins scarce in the literature, and
2024-2026 industrial surveys keep finding the same gap between the label and
the deployed system: most systems sold as twins run as models or shadows.
Price the naming into the proposal, because the word "twin" without a stated
data cadence is the classic overpromise.

| What will actually exist | Name it in the proposal as | Data contract to state |
|---|---|---|
| Offline what-if model fed by CSV or historian exports | Simulation model | Named export tables, refresh on request |
| Live state mirror and dashboards, no simulation lookahead | Digital shadow | Feed list, update latency, no decision automation |
| Shadow plus a periodically recalibrated simulator for lookahead and what-if | Predictive digital twin | Recalibration cadence, drift alarm owner, lookahead horizon |
| Twin that writes setpoints or schedules back to plant systems | Prescriptive digital twin | OT integration scope, safety case, human-approval gate; rare in practice and priced as a control-systems project |
| ELSE | Simulation model | Under-claim; upgrading the name later is free, walking it back is expensive |

Integration reality, so estimates land: at mining clients the data comes from
the fleet-management system (Modular DISPATCH, Cat MineStar, Wenco) and a
process historian (AVEVA PI, Ignition); at manufacturers from the MES and
historian; at ports from the TOS. First engagement phase always runs on
exports; live buses come later if the client funds them. The visualization
layer converging across vendors is OpenUSD/Omniverse (FlexSim exports USD
with simulation properties since its 2025 releases), and FMI 3.0 is the
co-simulation standard when a vendor model must plug in; details and sources
sit in references/research/des-tooling.md.

## Tool choice for DES builds

Facts below are condensed from the researched fact sheet in
references/research/des-tooling.md (access dates 2026-07-12).

| Situation | Tool | Basis |
|---|---|---|
| Consulting build that must live in git, CI, and the Python data stack, handed to client engineers | SimPy | Stable core (4.1.2, May 2026, after an 18-month gap); no built-in stats, streams, or animation, so you own those, and the assets in this skill supply the statistical layer |
| The audience needs animation to believe the model | salabim, or SimPy plus vidigi | salabim 26.x is actively developed by one maintainer, yieldless by default since 23.3.0, with native 2D/3D animation and video capture |
| Queueing-network study needing multiple customer classes, baulking, reneging, deadlock detection | Ciw | Packages deadlock detection no commercial tool offers |
| Client already licenses a commercial tool and their engineers will own the model | Their tool (AnyLogic, FlexSim, Plant Simulation, Simio) | Handoff beats elegance; note Arena has had no major release since 16.20 in 2022, so treat an Arena estate as a migration conversation |
| High-fidelity material handling, AGVs, 3D warehouse | FlexSim (Autodesk since Nov 2023) or Plant Simulation | Prebuilt material-handling libraries; building conveyors in raw SimPy burns weeks |
| Hybrid agent plus DES plus system dynamics in one model | AnyLogic | The multimethod position is real; browser-based AnyLogic 9 is in technology preview |
| ELSE | SimPy | Default for this practice; zero licence friction at handoff |

## DES craft

### Model architecture

assets/mine_haulage_sim.py is the reference pattern: a pit-to-crusher-to-port
chain with shovels as a Resource, the crusher as a PreemptiveResource whose
failure process interrupts dumps (resume the remaining service time after
repair), the stockpile as a Container whose full state blocks the crusher,
and the train loadout as a periodic drain. Two structural rules carry most of
the value:

1. Let congestion emerge. Model the truck cycle as queue-load-haul-queue-dump-
   return with contention at shovel and crusher. A cycle modelled as one
   sampled duration bakes yesterday's congestion into the inputs, and every
   scenario then reproduces the old queueing no matter what the policy changes.
2. One named RNG stream per stochastic process per replication, seeded from
   (replication, process name) and never from the policy. This is what makes
   common random numbers survive a policy change; a single global stream
   desynchronizes the moment a policy reorders event execution.

### Input modelling

The highest-damage silent error in industrial DES input fitting: fleet and
MES timestamp fields frequently include queueing inside nominal activity
times (a "load time" measured spot-to-spot contains wait-at-shovel).
Fit that contaminated field, then simulate contention on top, and the model
double-counts congestion; it validates poorly and, worse, every
debottlenecking scenario under-delivers because the baseline congestion is
frozen into the input. Decompose to pure service time from event states
before fitting, or re-derive service as cycle length minus measured waits.

| Input situation | Fit | Basis |
|---|---|---|
| Service and repair durations | Lognormal or gamma by MLE; judge with QQ plots, since at n above a few thousand every GoF test rejects | Durations are right-skewed and positive; a normal fit produces negative draws and the wrong right tail (Law, 5th ed., ch. 6; full title in references/sources.md) |
| Repair records cut at shift boundaries or open work orders | Censored MLE; scipy.stats.CensoredData feeds rv_continuous.fit since SciPy 1.11 | Ignoring censoring biases MTTR low, which biases availability high |
| Rich data, 200+ observations, tail immaterial to the decision | Empirical distribution (interpolated inverse CDF, as in assets/monte_carlo_copula.py) | Zero distributional assumption |
| Rich data and the tail drives the answer | Empirical body, generalized Pareto above a threshold | The empirical CDF caps the maximum at the observed maximum and understates tail risk |
| Arrivals with shift or hour-of-day pattern | Non-stationary Poisson via thinning | A stationary rate flattens the peaks that create the queues the client feels |
| No data, only operator knowledge | Triangular or PERT from min/mode/max elicitation, tagged as elicited | Replace after the first data pull; see the consulting section |
| ELSE | Lognormal by MLE with a stated caveat | Least-bad default for positive durations |

### Warm-up and replications

Welch's procedure on the hourly-throughput series: average across 10
replications, smooth with a centred moving average (window 25 h), and take
the point where the curve flattens. The demo model flattens at 52 h; the
production run then deletes the first 52 h of every replication.
assets/mine_haulage_sim.py automates the flat-point call with a 2 percent
band held for 24 h; plot the curve before trusting any automated pick.
MSER-5 is the defensible automated alternative (Hoad, Robinson, Davies,
Journal of Simulation 2010).

Replication count comes from the pilot, worked: 10 pilot replications of the
demo model give daily throughput sd 2,327 t/day, so the 95 percent CI
half-width sits at t(9) x 2327/sqrt(10) = 1,665 t/day. For a target of plus
or minus 500 t/day, solve t(n-1) x 2327/sqrt(n) <= 500 iteratively: n = 86.
The naive z-formula gives 84 here and understates by 30 percent and more
when the answer is small (under about 15); assets/replication_calculator.py
implements the iterated solve, Law's relative-precision variant with the
gamma/(1+gamma) correction, and a sequential procedure whose empirical
coverage at these settings measures 0.955 against the nominal 0.95.

### Variance reduction, with its measured payoff

Comparisons are where DES studies earn or lose their precision budget. For
policy B minus policy A over n paired replications, Var(Dbar) =
(sA2 + sB2 - 2 rho sA sB)/n. Common random numbers push rho toward 1. The
demo comparison (8 trucks against 7, 15 replications) measures rho = 0.998:
the paired CI comes out plus or minus 199 t/day against plus or minus 991
t/day for independent seeding, a 24.9x variance ratio, which means the same
precision at roughly 25x fewer replications. Two disciplines make this real:
the per-process named streams above, and paired-t analysis (CRN correlates
the arms, so two-sample formulas are invalid).

Antithetic variates pair each replication with its mirrored draws and cut
the variance of a mean when the model responds monotonically to its inputs.
On the Monte Carlo demo's NPV mean the measured reduction is 13.9x at equal
sample count. Antithetic pairs do nothing useful for tail quantiles; size
the run for the quantile standard error regardless.

### Validation

Follow Sargent's framework (Sargent 2010, WSC tutorial lineage), with the
weight on three tests:

1. Trace validation against history. Feed the recorded period's inputs and
   reproduce its KPIs; the trust test below sets the bar.
2. Face validity with operators. Walk the animation or event trace with
   shift supervisors; they catch wrong dispatch logic and impossible states
   faster than any statistic.
3. Extreme-condition tests. Zero trucks must give zero throughput; an
   infinite crusher must move the bottleneck to the shovels; doubling MTTR
   must cut availability by a computable amount. These tests are the main
   defence against compensating errors, where two wrong parameters cancel
   on the baseline and diverge on every scenario.

## Monte Carlo risk models

assets/monte_carlo_copula.py is the working engine: Gaussian copula with
Spearman targets, antithetic option, quantile standard errors, and a partial
rank correlation tornado.

Correlation mechanics that practitioners get wrong in order of frequency:

1. Elicit dependence as Spearman ("when price runs, opex runs"), then map to
   the latent normal correlation with r = 2 sin(pi rho_s/6) (Kruskal 1958).
   Feeding the Spearman value in raw under-correlates by up to 0.018 at mid
   range; small, and free to remove.
2. Elicited pairwise matrices are frequently not positive definite as a set;
   repair with eigenvalue clipping or Higham's projection before Cholesky.
3. The Gaussian copula has zero tail dependence for any correlation below 1,
   so joint catastrophes are structurally understated. When the client
   question is "what happens when grade, price, and recovery all go wrong
   together", switch to a t copula: at pairwise 0.5 and 4 degrees of
   freedom the tail-dependence coefficient is 0.253, against 0.082 at 10 df
   and exactly 0 for the Gaussian (worked in references/copula-and-risk-math.md).

Sensitivity: Sobol indices via Saltelli sampling cost N(d+2) model runs, so
d = 8 at N = 1024 means 10,240 runs; spend that only when the model is
vectorized-cheap or a surrogate exists, and remember classical Sobol assumes
independent inputs. With a correlated input set, present a partial rank
correlation tornado (in the asset) or Shapley effects.

Report P10/P50/P90 with their Monte Carlo standard errors (the demo prints
P90 = 1,553 MUSD with SE 14 MUSD at n = 20,000) and quote no digits the SE
cannot support. Add P(NPV < 0) whenever the distribution straddles zero;
executives anchor on it, and it changes the conversation from bands to
decisions.

## Calibration and the twin lifecycle

### Bayesian calibration and its identifiability trap

The Kennedy-O'Hagan frame models observations as y(x) = eta(x, theta) +
delta(x) + epsilon: simulator, discrepancy, noise. The known trap is
confounding between theta and delta: without constraints, many
(theta, delta) pairs fit equally well, and dropping delta makes the theta
posterior concentrate confidently on wrong values (Brynjarsdottir and
O'Hagan, Inverse Problems 2014). Consulting stance that survives review:
calibrated parameters are tuning values with predictive validity inside the
operating envelope of the calibration data; physical interpretation of theta
requires an informative discrepancy prior and a defence of it.

### History matching as the practical default

For expensive simulators, history matching with implausibility beats full
Bayes on defensibility per compute dollar (canonical treatment: Vernon,
Goldstein, Bower, Bayesian Analysis 2010). Rule out parameter regions where
I(theta) = |z - E[eta(theta)]| / sqrt(V_emulator + V_obs + V_discrepancy)
exceeds 3 (Pukelsheim's three-sigma rule), refit the emulator on the
survivors, repeat in waves. Worked single evaluation: observed 41,200 t/day,
emulator mean 39,000 with sd 800, observation sd 600, discrepancy sd 1,000
gives I = 2,200/sqrt(800^2 + 600^2 + 1000^2) = 1.55, so that theta survives
the wave. The discrepancy variance term is where honesty lives; setting it
to zero silently converts "our model is imperfect" into "the data must fit".

Simulation-based inference (the sbi package, community-maintained from the
Tuebingen mackelab lineage) makes neural posterior estimation practical when
you can afford 10k+ simulator runs; adoption through 2026 remains
concentrated in physics and neuroscience, so treat it as a research option
for DES calibration and lead with history matching at clients.

### Drift and recalibration cadence

A twin decays the day the plant changes a truck, a shift roster, or a feeder
setting. Watch the residual between twin prediction and actual on the KPIs
the twin exists for, with a CUSUM or a simple control chart; recalibrate when
the residual mean shift exceeds the simulation CI at the current replication
count, and review on a calendar tied to decision tempo (monthly for a
planning twin, weekly for a scheduling twin). Instrument this exactly like a
deployed ML model; model-operations owns the monitoring patterns, and the
twin's residual stream plugs into them unchanged.

### Fidelity economics

Model subsystems earn their place by changing a decision. Every added
subsystem multiplies input-data plumbing, validation surface, run time, and
post-handoff maintenance, so the twin that survives is usually the smallest
one that reproduces the KPIs the decision needs. When someone asks for "the
whole plant", price the maintenance burden of each subsystem separately and
watch the scope shrink to the bottleneck chain.

## Simulation-optimization

Two regimes, split by the design space:

| Design space | Method | Notes |
|---|---|---|
| Up to about 20 discrete candidates (fleet sizes, rule variants) | Ranking and selection: KN procedure or OCBA | Statistically airtight best-arm selection; composes with CRN, which BO's standard GP machinery does not exploit |
| Continuous or mixed knobs, expensive noisy evaluations | Bayesian optimization with a noise-aware acquisition | qLogNEI in BoTorch (Ament et al., NeurIPS 2023) under Ax (1.0 since Nov 2025) for production; assets/sim_opt_bayes.py exposes the mechanics in plain numpy/scipy |
| A vendor tool's built-in optimizer (OptQuest inside AnyLogic, Simio, Arena) | Scatter search plus tabu (OptTek); no noise model by default | Set replications per iterate explicitly or it optimizes noise |
| ELSE | Ranking and selection over a shortlist the client already believes | Shortlist plus airtight comparison persuades; a black-box optimum without a story does not |

Craft points the demo encodes: use the best posterior mean at an observed
point as the EI incumbent, because an incumbent taken from the best raw
observation is a lucky draw and stalls the search; and re-test every winner
on fresh replications before reporting, because training-value scoreboards
carry winner's-curse bias (the demo's random-search winner scored 8.657 in
training and 8.394 on 20 fresh replications; the BO pick held 8.493 plus or
minus 0.122). Budget rule of thumb for GP surrogates: 2d to 10d initial
points and roughly 20d total evaluations reaches a usable optimum for d up
to about 10; treat it as a starting budget to extend on evidence of an
unconverged posterior.

Pairing with supply-chain-optimization runs one way: the optimizer proposes
a plan under deterministic or scenario constraints, the simulator disposes
by scoring it under variability and failures, and the readout reports the
degradation (plan promises 100, simulation delivers 91 with a CI of 2). A
plan that survives simulation at 95 percent of its promise is a deliverable;
a plan only ever scored by its own optimizer is a hypothesis.

## Consulting intricacies

### The baseline-reproduction trust test

No scenario result lands until the model reproduces a recent historical
period the client remembers. Reproduce last quarter: daily throughput mean
inside the model's own CI around the actual, distribution shape checked by
QQ overlay, downtime fraction within a point. Show that overlay first in
every readout. This test, passed once in front of the operations manager,
buys more scenario credibility than any statistical appendix; failed once,
it ends the engagement's authority quietly and permanently.

### Operators are an input-data source

The historian shows what happened; operators know why. Interview shift
supervisors for the failure modes absent from the data (the crusher liner
change every 6 weeks, the wet-season haul slowdown, the unofficial 10
percent over-nameplate day-shift run rate), elicit min/mode/max for
distributions with no data, and tag every elicited input in the model
config. Two effects: the inputs improve, and the operators become co-authors
who defend the model in the readout at the moment someone senior attacks it.

### Handoff without decay

The model outlives the engagement, so build the exit on day one: a pinned
environment (lock file, exact interpreter), seed-reproducible runs, one
command that rebuilds the baseline and one that runs a named scenario, input
data pulled by a documented script with a stated refresh cadence, and a
client engineer who owns the model, named in the closeout. The reproducibility
audit of open DES models by Heather, Monks et al. (arXiv:2501.13137) found
most published models fail to rerun for want of exactly these basics. When
the client declines to fund the data pipeline that keeps a twin current,
deliver a documented offline simulation model and say so with the Kritzinger
naming; a stale twin sold as live is the worst outcome this practice
produces.

## Files in this skill

| Path | Contents |
|---|---|
| assets/mine_haulage_sim.py | SimPy pit-to-port chain; Welch warm-up, replication sizing, CRN comparison; the numbers quoted above print from its demo |
| assets/monte_carlo_copula.py | Copula MC engine; antithetic option, quantile SEs, PRCC tornado; open-pit NPV demo |
| assets/replication_calculator.py | Fixed-n, relative-precision, and sequential replication procedures with a coverage check |
| assets/sim_opt_bayes.py | GP plus expected improvement over a noisy SimPy flow line, against a random-search baseline with honest re-testing |
| references/des-statistics.md | Derivations: replication math, CRN and antithetic algebra, Welch and MSER, input-modelling details, Sargent tests |
| references/copula-and-risk-math.md | Copula derivations, rank-correlation mappings, tail dependence, quantile SEs, sensitivity-analysis costs |
| references/calibration-and-sim-opt.md | Kennedy-O'Hagan, history matching worked, SBI status, ranking and selection, BO tooling, drift monitoring |
| references/research/des-tooling.md | Researcher fact sheet on 2024-2026 DES tooling, with URLs |
| references/sources.md | Every external claim's source with access date |
