---
name: predictive-maintenance
description: Failure forecasting and condition monitoring for heavy industry. Use for mining maintenance forecasting (haul trucks, shovels, conveyors, SAG mills), component-life and survival analysis on CMMS or SAP PM extracts, oil-analysis and vibration alerting, remaining-useful-life requests, alert-threshold and inspection-policy economics, and the evaluation of failure-prediction models under censoring.
---

# Predictive maintenance

This skill covers failure forecasting and condition monitoring for heavy
industry, with mining as the reference domain. It assumes full command of
the standard methods and records the judgment layer: which method the data
can actually support, the traps specific to maintenance data, and the
economics that turn a model into a maintenance decision. Source IDs (S1,
S2, ...) resolve in `references/sources.md`; all URLs were accessed
2026-07-12. Adjacent lanes: the feature-engineering skill owns the general
leakage taxonomy (this skill owns the maintenance-specific instances), the
supply-chain-optimization skill owns spare-parts inventory and consumes the
failure forecasts produced here, and the model-operations skill owns
retraining governance including the intervention-feedback problem that
maintenance triggers.

## 1. The data reality that decides the model

Five facts hold across essentially every mining and heavy-industry
engagement, and each one forces a modelling choice before any method
discussion starts.

| fact | typical magnitude | consequence for the model |
|---|---|---|
| failures are rare | under 0.5% of asset-weeks; tens of failures per component class per decade of fleet history | few-parameter survival models fit; per-asset deep models do not. Pool the fleet and spend effort on labels, never on architecture |
| censoring dominates | 40 to 80% of component lifetimes end in preventive replacement or are still in service | every fit must carry the censoring likelihood term; any KPI computed from corrective work orders alone (mean life of replaced parts) is biased short, 32% short in the worked example below |
| event dates are wrong | notification, order, and completion dates differ by days to weeks; work orders get batch-entered at shift end | rebuild event times from malfunction start plus engine-hours readings; a label placed at order creation teaches the model to detect paperwork (see `references/cmms-data-reality.md`) |
| labels live in free text | damage codes are sparse and miscoded; a code-list trim raised coding accuracy from 41% to 89% in one published case (S9) | budget one to three weeks for work-order cleaning and a human-audited label sample before any fit (S8, S10) |
| fleets are heterogeneous | same truck model across ore bodies, haul profiles, operators, rebuild states | pooling heterogeneous wear-out populations drags the apparent Weibull shape toward 1, which reads as random failure and wrongly kills age-based policies; stratify or add duty covariates first |

The consulting sequence follows from the table: reconstruct lifetimes with
censoring flags (recipe in `references/cmms-data-reality.md`), fit the
simplest survival model the failure count supports, and put the effort
into the decision layer (section 5), where the money is.

## 2. Choosing the reliability method

| IF the data look like | THEN fit | notes |
|---|---|---|
| non-repairable component lifetimes, 15+ failures | Weibull with right censoring (`WeibullFitter`) | the workhorse; report shape with its CI, B10, and the censoring fraction |
| lifetimes plus fixed covariates (site, duty class), roughly 10 failures per covariate | Cox proportional hazards | the events-per-variable budget binds long before sample size does |
| covariates that change over a life (payload, ore hardness, operating hours per week) | Cox with start-stop rows (`CoxTimeVaryingFitter`) | hazard ratios only; it has no `predict_survival_function`, so pair it with a parametric or landmark model for forward risk scores (S6) |
| proportional hazards fails (crossing survival curves across strata, failed `check_assumptions`) | Weibull or log-normal AFT | AFT coefficients read as life multipliers, which planners find natural ("hard ore shortens life 18%") |
| event stream from one repairable system (repeated repairs) | trend test first, then power-law NHPP (Crow-AMSAA) if trending, plain rate if flat | fitting Weibull to inter-failure gaps is the classic error; see below |
| under 10 failures total | WeiBayes: fix the shape from engineering knowledge or a sister fleet, fit scale only | an honest scale with an assumed shape beats a two-parameter fit the data cannot support |
| hundreds of failure events plus rich sensor features, short-horizon question | gradient boosting on windowed features, evaluated event-wise (section 6) | survival machinery adds little once events are plentiful and the horizon is one to four weeks |
| ELSE | Kaplan-Meier plus a censored Weibull, then stop | escalate only when a richer model changes a maintenance decision, and say so in the report |

### Reading the Weibull shape for policy

| shape rho | reading | policy implication |
|---|---|---|
| below 1 | infant mortality | fix quality of parts, rebuilds, or workmanship; age replacement makes things worse |
| 0.9 to 1.1 | no age signal | age-based replacement has no finite optimum (worked numbers in `references/derivations.md`); go condition-based or run to failure |
| above 1.1 | wear-out | age-based replacement can pay; run the renewal-reward computation of section 5 |
| ELSE (CI spans 1, or the fit pools suspect strata) | undetermined | split by site and duty before concluding; the mixture-pulls-shape-toward-1 trap in section 1 usually explains a flat-looking hazard |

Worked fit (`assets/survival_models.py`, seed 7): 150 components, true
Weibull shape 2.6 and scale 14,000 h, preventive change-out at 14,000 h,
52% censored. The censoring-aware fit recovers shape 2.46 (95% CI 1.96 to
2.96) and scale 14,802 h. Dropping the censored units gives scale 10,111 h
and B10 4,785 h against the true-model 5,937 h: the estimate every
spreadsheet of "average life at replacement" quietly produces.

### The repairable-system trap

Component lifetimes (non-repairable, replaced on failure) and repairable
systems (the same truck fails and returns to service repeatedly) need
different machinery, and the visible symptom of confusion is a Weibull fit
on inter-failure gaps. Gaps from a deteriorating system are neither
independent nor identically distributed, and the fit lands near shape 1,
which reads as random failure. The demo (`survival_models.py`, part C)
makes it concrete: a system simulated with power-law intensity beta = 1.6
(strongly deteriorating) gives a gap-Weibull shape of 0.90, while the
Laplace trend test (u = 3.13) and the Crow-AMSAA MLE (beta = 1.56)
recover the truth. Run the trend test before any distribution fit on
repairable-system data; with no trend, a plain rate carries the analysis,
and time-to-first-failure alone supports a Weibull.

## 3. RUL or short-horizon probability

Remaining useful life is the most requested deliverable and usually the
wrong one. The planner's question is "which assets get my six inspection
slots this week" or "does this component survive to the September
shutdown", and both are probability questions over discrete horizons.

| IF | THEN deliver |
|---|---|
| a scalar health index exists and moves monotonically (liner wear, envelope band energy, wear-metal rate) | RUL as a distribution from degradation-curve extrapolation, tied to a datable intervention |
| a library of run-to-failure trajectories exists for the component | similarity-based RUL (match the current trajectory, read quantiles of matched remaining lives); the match set is inspectable, which buys planner trust |
| failures are rare, degradation is stepwise or hidden, planning runs weekly | P(failure within h) for h = 1 week, 4 weeks, next shutdown, plus a ranked list sized to inspection capacity |
| the client insists on RUL for fleet screening | reframe: show that a 4-week failure probability with event recall at fixed false-alarm budget answers their scheduling question, and price the RUL alternative honestly |
| ELSE | short-horizon probabilities; they subsume RUL for every weekly-cycle decision the fleet actually makes |

Published C-MAPSS results (RMSE 11 to 13 cycles on FD001) do not transfer
to fleets, for identifiable reasons: the 125-cycle label cap rewards
predicting the cap, test trajectories are truncated (right-censored) while
training units all run to failure, per-unit normalization leaks trajectory
endings, and a decade of tuning on four fixed splits produced a winner's
curse (S4, S5). The full argument, plus the mid-2026 status of time-series
foundation models in PHM (research traction, no documented production
deployments), is in `references/rul-benchmarks.md`. Quote it when a client
arrives with a paper claiming 12-cycle RMSE and asks for the same.

## 4. Condition monitoring that earns its keep

Mining splits cleanly by asset class: fixed plant (mills, crushers,
conveyor drives, fans, pumps) gets vibration monitoring because speed and
load are steady; mobile equipment (trucks, shovels, loaders) gets oil
analysis and onboard telemetry because variable speed and duty wreck
spectral baselines. Conveyor idlers are a population problem (thousands of
cheap bearings) and get thermal or acoustic drive-by screening; treat them
as a ranking problem, never as per-asset modelling.

### Vibration features

| feature | failure stage where it moves | trap |
|---|---|---|
| overall RMS or ISO 20816 velocity zone (S15) | late | zone limits apply to overall velocity on steady machines only; useless for early bearing defects |
| kurtosis, crest factor | early impulsive stage | non-monotone: both fall back toward normal as damage spreads and impacts smear; a falling kurtosis with rising band energy means advanced damage |
| band energies around structural resonances | early to mid | pick bands by spectral kurtosis (which band is most impulsive), never by fixed tables |
| envelope spectrum lines at BPFO, BPFI, BSF, FTF | earliest for rolling-element bearings; weeks-to-months lead | demodulate the resonance band first; the defect frequencies live in the envelope, and the raw spectrum hides them under shaft and gear tones |

The demo (`assets/vibration_features.py`) plants an outer-race fault and
shows the trap chain end to end: full-band RMS moves 1.4% and full-band
kurtosis stays near 3.0 (tones dominate), while the 2.8 to 3.6 kHz band
energy rises fivefold and the envelope spectrum shows BPFO x1 through x4
exactly. A kurtosis-picked band (2,900 to 3,700 Hz) finds the resonance
without prior knowledge of the geometry.

### Oil analysis

Spectrometric wear metals are fleet bread and butter on mobile equipment:
iron for steel wear, copper for bushings and thrust washers (and cooler
leaching, which trends copper without any wear), lead for overlay
bearings, chromium for rings and liners, silicon for dust ingress. Read
silicon with aluminum: rising together at roughly 3:1 means dirt entry,
silicon alone often means sealant or additive. Two well-known gotchas
carry most of the analytical value. First, ICP spectrometry is blind to
particles larger than about 5 to 10 microns, so severe wear can hold
spectrometric iron flat while the PQ (ferrous debris) index climbs; a
PQ-to-Fe divergence is an alarm in itself. Second, ppm readings dilute
with oil top-ups, so normalize by hours-on-oil and correct for makeup
volume before trending; a truck burning oil looks like it is healing.
Set limits statistically per fleet and compartment (baseline mean plus 2
to 3 sigma, plus a rate-of-change rule), never from generic tables:
compartment chemistry and duty differ enough that generic limits either
flood the planner or sleep through failures.

### Drift detection with worked constants

Health indicators drift slowly, and Shewhart limits wait for a 3-sigma
excursion. Use EWMA (lambda = 0.20, L = 2.859) or CUSUM (k = 0.5 sigma,
h = 5 sigma), both tuned to an in-control ARL near 370 to 465 samples;
`assets/control_charts.py` re-verifies those ARLs by Monte Carlo (375,
365, 466) and shows a 0.0375-sigma-per-sample drift caught by EWMA 5
samples after onset against 46 for Shewhart. Derivations and the design
table are in `references/derivations.md`. On quarterly-sampled oil data an
ARL0 of 370 means one false alarm per compartment per 90 years, so tighten
L when the sampling cadence is slow and the miss cost is high; the
threshold economics of section 5 give the exchange rate.

### Anomaly detection and its false-alarm economics

Isolation forests and autoencoders fit the maintenance data shape (healthy
majority, unlabeled) and fail on economics when deployed as alerting. The
arithmetic that decides: a 120-asset fleet at a 0.5% weekly failure rate
produces 0.6 true events per week; a detector with a 1% weekly false-alarm
rate produces 1.2 false alerts per week, so precision cannot exceed about
33% even at perfect recall. That precision is workable when an alert costs
a $1,800 inspection against a $165,000 miss premium (section 5), and fatal
when alerts page a control room. Use unsupervised scores as features and
screening ranks, put a control chart or a supervised layer between them
and any human, and price the false-alarm budget explicitly in
planner-hours per week.

## 5. The decision layer, where the value lives

### Alert thresholds from the cost matrix

With calibrated failure probability p per asset-week, alert when
p > c_inspection / (c_unplanned - c_planned). Worked example
(`assets/alert_threshold.py`, economics consistent with trade-press
haul-truck figures, S7): $1,800 inspection, $95,000 planned change-out,
$260,000 in-service failure gives p* = 1,800 / 165,000 = 1.09%. Two
consequences follow. First, the optimal threshold sits two orders of
magnitude below the 0.5 default, so a model "only" reaching 7% precision
can be printing money. Second, the formula holds for calibrated
probabilities only: in the demo, applying p* to overconfident scores with
identical ranking skill costs an extra $149 per asset-week against an
empirically tuned threshold, roughly $930k per year on a 120-truck fleet.
Recalibrate on held-out weeks or tune the threshold empirically; never
push the closed form onto raw scores from a rebalanced training set.

### Capacity beats threshold

Planners run weekly cycles with fixed inspection capacity, so the deployed
policy is usually top-k, and the threshold argument becomes a budget
argument. From the demo run (fleet of 120, calibrated scores):

| k slots per week | precision | net value per inspection |
|---|---|---|
| 2 | 7.2% | $10,035 |
| 6 | 4.9% | $6,272 |
| 20 | 2.6% | $2,419 |

Expand k while the marginal inspection nets positive and the planning
office can absorb the work orders; k is a capacity budget, p* is the lower
bound where a slot stops paying. Precision-at-k, sized to the client's
actual slot count, is also the honest headline metric for the engagement
report; fleet-level AUROC hides everything a planner cares about.

### Inspection intervals from the P-F interval

For a failure mode with P-F interval L and per-look detection probability
d, inspections every I give P(miss) roughly (1 - d)^(L/I). Route-based
envelope analysis on bearings (L of 8 to 16 weeks, d near 0.7) on a
monthly route misses about 3.4% of developing defects at L = 12 weeks;
stretching the route to 9 weeks pushes the miss rate to 19%. The standard
L/3-to-L/2 rule is this arithmetic rounded to a heuristic; the worked math
is in `references/derivations.md`, and it also identifies the case where
no interval works (low d against a fast failure mode), where the answer is
a different detection technique.

### Age-based only when the shape says so

The renewal-reward computation prices age replacement: with shape 2.5,
scale 14,000 h, and the cost matrix above, the optimal change-out age is
9,760 h at $17.15/h against $20.93/h for run-to-failure, saving about
$22,700 per component-year. The optimum is flat (8,000 to 12,000 h all
within $0.40/h) and still leaves 33% of components failing in service,
both of which belong in the client conversation: chasing T* precision is
waste, and visible in-service failures do not mean the policy is broken.
Full table in `references/derivations.md`. Condition-based replacement
beats age-based exactly when a monitorable indicator with a usable P-F
interval exists; when it does, the threshold and capacity machinery above
prices it.

### Alarm fatigue is a budget line

Every false alert spends planner attention and erodes response to true
ones; practitioner experience across alarm-management programs is that
response quality collapses once a majority of alerts are false, so state a
false-alarm budget (per planner-week, from the capacity table) in the
design document and dimension thresholds to it. The event-based metrics of
section 6 make the budget auditable in production.

## 6. Evaluation done right

Point-wise metrics on window labels inflate and scramble at the same time,
because a latched alarm votes once per day for a single detection while a
missed event costs only a few negative days. Score events.

The rules implemented in `assets/event_evaluation.py`: a failure counts as
detected only when an alarm fires inside its actionable window (3 to 30
days before failure in the demo; alarms inside 3 days give planners
nothing to act on), consecutive alarm days collapse into one episode,
non-failing machines contribute exposure time to the false-alarm
denominator, and lead time is reported as a distribution. Demo run (60
machines, 3 years, 114 failures): point-wise precision 0.43 against
episode precision 0.21 (the latch inflation, 2x), point-wise recall 0.21
against event recall 0.70 (the scramble: most failures did get an
actionable warning), 1.9 false alarms per machine-year, lead time
p25/median/p75 of 6/10/18 days, 8% of failures alarmed too late to act.
The reporting set for any engagement: event recall, episode precision,
false alarms per machine-year, and the lead-time distribution, all at the
deployed threshold or k.

Censoring reaches evaluation too. Harrell's concordance drifts optimistic
under heavy censoring because comparable pairs over-represent short lives;
at the 40 to 80% censoring of maintenance data, report Uno's IPCW
concordance and the IPCW Brier score with an explicit horizon (S14, S16).
And the maintenance-specific leakage list, each item a real engagement
scar: labels timed by order-creation date (the model learns paperwork
rhythms), train/test splits that put the same machine on both sides (split
by machine, then by time), preventive replacements coded as healthy
negatives (they are censored, and many were incipient failures the PM
caught), RUL targets capped then scored on the capped scale (S4), and
post-deployment retraining on labels the model's own alerts created (the
intervention-feedback loop; governance belongs to the model-operations
skill). The general taxonomy lives in the feature-engineering skill; these
instances override it where they conflict.

## 7. Tooling, mid-2026

| package | version, date | use for | watch for |
|---|---|---|---|
| lifelines 0.30.3 (S1) | 2026-03-05, Python 3.11+ | Weibull/AFT fitters, Cox, CoxTimeVarying | `CoxTimeVaryingFitter` fits hazard ratios only, no survival prediction (S6); use `cluster_col` for sandwich standard errors when one machine contributes several rows |
| scikit-survival 0.28.0 (S2) | 2026-07-05 | random survival forests, IPCW concordance, Brier | pins scikit-learn >= 1.9 and < 1.10, which dictates the environment; targets are structured arrays built with `Surv.from_arrays`, the most common first-run error |
| reliability 0.9.0 (S3) | 2025-03-07, no release in 16 months | probability plots, Crow-AMSAA, quick Weibull MLE checks | maintenance mode; pin the version and smoke-test against current numpy before committing it to a delivery |
| ELSE | | numpy plus scipy and the closed forms in `references/derivations.md` | the Crow-AMSAA MLE and the renewal-reward optimum are ten lines each; a dependency is never required for them |

The stack installed clean on Python 3.14 with numpy 2.5 on 2026-07-12;
`pip install numpy scipy pandas lifelines` covers every asset module here.

## 8. Code assets

All five modules compile and their `__main__` demos ran on 2026-07-12
(Python 3.14 venv; numpy 2.5.1, scipy 1.18.0, pandas 2.3.3, lifelines
0.30.3). Every demo uses seeded synthetic data with censoring built in,
and every number quoted in this file reproduces from them.

| module | demonstrates |
|---|---|
| `assets/survival_models.py` | censored Weibull against the two naive fits; Cox with time-varying duty; Laplace trend test plus Crow-AMSAA against the gap-Weibull error |
| `assets/control_charts.py` | EWMA and CUSUM with published constants, Monte Carlo ARL verification, slow-drift detection race |
| `assets/vibration_features.py` | synthetic bearing fault, time-domain features, kurtosis-picked demodulation band, envelope spectrum recovering BPFO harmonics |
| `assets/alert_threshold.py` | closed-form p*, empirical threshold sweep, the miscalibration cost, precision-at-k against planner capacity |
| `assets/event_evaluation.py` | event-based scoring with actionable windows, episode deduplication, exposure-based false-alarm rates, lead-time distribution |

## References

- `references/derivations.md` holds the censored-MLE, renewal-reward,
  P-F, threshold, and control-chart mathematics with the worked numbers.
- `references/cmms-data-reality.md` holds the SAP PM field guide, the
  lifetime-reconstruction recipe, and the label-leakage mechanics.
- `references/rul-benchmarks.md` holds the C-MAPSS transfer argument and
  the mid-2026 status of sensor foundation models.
- `references/sources.md` holds every external claim's URL and access
  date.
