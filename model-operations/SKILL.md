---
name: model-operations
description: |
  Keep delivered models alive in client operations after the build team leaves.
  Covers drift measurement with its failure modes, retraining policy priced as an
  economic decision, forecast governance (FVA stairsteps, override scoring, plan
  stability), monitoring design the client keeps using, and handoff artifacts
  (runbooks, model cards, retraining playbooks). Trigger on: "is the model
  drifting", "when should we retrain", "set up model monitoring", "forecast value
  added", "score the planner overrides", "hand the model to the client team",
  "model health report", "post-delivery support", "/model-operations".
---

# Model operations

Delivered models die from three causes, in rough order of frequency: upstream
data changes the model never sees, retraining that nobody owns, and alert
channels the client learned to ignore. Ten years of outages on one large Google
ML pipeline were mostly data and distributed-systems failures; the learned model
itself was rarely the cause (Papasian and Underwood, OpML 2020). Across four
industries and four model families, 91% of dataset-model pairs degraded
measurably as time since training grew (Vela et al., Scientific Reports 2022).
This skill owns everything after delivery: measuring drift without fooling
yourself, pricing retraining, governing forecasts inside a planning
organization, and handing the system to the people who stay.

Sibling skills build the models (demand-forecasting, price-forecasting,
predictive-maintenance, customer-analytics); daemon-ops owns the scheduling
mechanics (launchd/systemd units, heartbeats, log rotation) and the house
alerting doctrine. This skill decides what runs, what it watches, and when
retraining is worth the money.

## Drift measurement and where it lies

### PSI moves with the binning, so publish the binning

PSI is the standard the client's risk team will already know:

```
PSI = sum_i (a_i - r_i) * ln(a_i / r_i)
  r_i = reference share in bin i, a_i = current share
  bins fitted on the REFERENCE sample only, then frozen
```

The number depends on the bin scheme as much as on the data. One synthetic
right-skewed feature, a genuine +0.35 sd shift, 20,000 rows per side
(`assets/drift.py`, seeded, reproducible):

| binning | PSI |
|---|---|
| equal width, 10 bins | 0.106 |
| equal frequency, 10 bins | 0.117 |
| equal frequency, 5 bins | 0.108 |

An 11% spread from binning choice alone, sitting right on the 0.10 "watch"
folklore line. Now the same shift with 20 legacy outliers (a currency bug, 40x
scale) left in the reference extract:

| binning | PSI |
|---|---|
| equal width, 10 bins | 0.0003 |
| equal frequency, 10 bins | 0.116 |
| equal frequency, 5 bins | 0.107 |

Equal-width bins stretched to the outliers, the whole body of the distribution
landed in one bin on both sides, and a real shift scored as dead calm. Rules
that follow: fit bins equal-frequency on the reference, freeze them, and print
the bin count and the empty-bin epsilon beside every PSI you report, because a
PSI without its binning is a number without units.

### The thresholds are folklore and the null depends on n

The 0.10/0.25 action thresholds come from credit-scoring practice (Siddiqi
2006 records them as rules of thumb); they carry no distributional argument.
Yurdakul (2018) derived the null: with B bins and samples of n and m,

```
PSI under NO drift  ~  (1/n + 1/m) * chi-square(B-1)
B=10, n=m=100:     E[PSI] = 0.180, 95th percentile 0.35   (pure noise reads "act")
B=10, n=m=1,000:   E[PSI] = 0.018, 95th percentile 0.034
B=10, n=m=10,000:  E[PSI] = 0.0018
Simulation with assets/drift.py bins, 400 null draws: matches to two figures.
```

So a monthly PSI on a 100-row segment crosses 0.25 regularly with zero drift,
and a 0.10 alarm on a million-row feed fires on shifts far too small to act
on. Set thresholds from the null at your n and B, or from the backtested cost
of the action the alarm triggers.

### KS and Wasserstein, and when each misleads

Two-sample KS is binning-free, and its p-value is the trap: at production
sample sizes it rejects on operationally empty shifts. From the module demo, a
+0.03 sd mean shift (nothing, in business terms) scores p=0.55 at n=500,
p=0.04 at n=5,000, and p<0.0001 at n=50,000, while the D statistic stays near
0.015. Wasserstein-1 divided by the reference standard deviation reads as
"shift in sd units" and stays stable as n grows; the same non-shift scores
W1/sd of about 0.03 at every n. Evidently's per-column defaults encode this
lesson: KS with p<0.05 for reference samples up to 1,000 rows, scaled
Wasserstein with threshold 0.1 above that (Evidently documentation, accessed
2026-07-12).

| Situation | Test | Reason |
|---|---|---|
| Continuous feature, n <= 1,000 per side | KS statistic with its p-value | Binning-free; the p-value still means something at this scale |
| Continuous feature, n > 1,000 | Wasserstein-1 / reference sd, threshold near 0.1 | Effect size in sd units; immune to the p-value-at-scale trap |
| Client already governs with PSI | PSI, equal-frequency 10 bins, eps and B printed | Comparability with their scorecard practice beats metric elegance |
| Discrete or zero-inflated feature | PSI on category shares, rare categories floored | Ties invalidate KS p-values; quantile bins collapse |
| Model scores (outputs) | PSI or scaled W1 on the prediction distribution | Cheapest single alarm; catches pipeline breaks weeks before labels do |
| ELSE | Scaled W1 and equal-frequency PSI together | When they disagree, inspect tails and binning before believing either |

### The seasonal alarm and the calendar

A drift alarm that fires every December is a feature set without calendar
context, and the fix belongs in the model. Run a second comparison against the
same period last year: an alarm that fires against the trailing window and
stays quiet against last December is seasonality; an alarm that fires against
both is real. Chronic seasonal alarms mean the reference window and the
features need the calendar (route to the demand-forecasting skill), and until
then the alarm trains the client to ignore the channel.

### Covariate drift, concept drift, and the label gap

Covariate drift (inputs moved) is observable on day one. Concept drift (the
input-to-output relationship moved) is only observable once labels arrive, and
in business systems labels run late: demand actuals close weeks after the
forecast, churn is defined over 30-90 day windows, equipment failures take
months and get censored by the very work orders the model creates. Monitoring
that waits for labels is a post-mortem. Lead with proxies:

| Model | Typical label delay | Leading proxies |
|---|---|---|
| Demand forecast | Days to weeks (period close) | Bias and WAPE on the last closed period; forecast-to-confirmed-orders ratio; prediction-distribution drift |
| Churn / retention | The churn window itself, 30-90 days | Score-distribution PSI; precision on early cancellations, which arrive first; CBPE where calibration holds |
| Predictive maintenance | Months, censored by interventions | No-fault-found rate on work orders (rising NFF is precision decay); alert volume against plan; drift on the top-weighted sensor features |
| ELSE | Measure the delay before promising any metric | Prediction drift plus top-5 feature drift, reviewed weekly against fixed thresholds |

Confidence-based performance estimation (NannyML's CBPE) estimates a
classifier's metrics from its calibrated scores before labels land. It holds
under covariate shift and goes blind under true concept drift, an assumption
its own documentation states; treat it as a bridge across the label gap, and
reconcile against real labels every time a batch closes.

## Retraining is an economic decision

### Price it before scheduling it

Retraining has a cost (validation, sign-off, deploy, and the risk of promoting
a worse model) and a benefit (error removed). Both are measurable, so compute
them. From `assets/retraining_policy.py`, a linear system under slow
coefficient drift, 420 scored days, 200 rows/day, $2 per unit of absolute
error, $1,500 per retrain cycle, labels 21 days late:

| Policy | Retrains | Avg MAE | Total cost |
|---|---|---|---|
| Never | 0 | 0.8083 | $135,800 |
| Weekly | 59 | 0.8001 | $222,900 |
| Monthly | 13 | 0.8004 | $154,000 |
| Quarterly | 4 | 0.8013 | $140,600 |
| Trigger (1.25x anchored) | 0 | 0.8083 | $135,800 |

Weekly beat monthly by 0.0003 MAE, roughly $100 of error, and paid $69,000 in
extra retrain cycles for it. Under slow drift, cadence past monthly bought
nothing; the honest answer for this world is quarterly or a trigger. Add an
abrupt break at day 330 (a price-rule change, a supplier swap) and the ranking
inverts: never bleeds to $168,100, the trigger fires twice and lands at
$153,000, weekly recovers fastest at the biggest bill ($230,200). The
quarterly calendar happened to land a retrain 60 days after this particular
break and tied the trigger; move the break a month and it bleeds a full
quarter. Policies rank differently by drift regime, so backtest the policy on
the client's own history with the module before committing to one.

### Trigger design rules that survive contact

Three rules from the module, each closing a real failure:

- Anchor the trigger baseline in a healthy period and never re-anchor it to a
  degraded one. A trigger that resets its baseline after each retrain
  normalizes sickness: it fires once after a break, retrains on a
  contaminated window, adopts the elevated error as the new normal, and goes
  silent while the model stays broken.
- Give retrains a cooldown of label delay plus the trigger window (21+14 days
  in the demo), so the trigger scores the new model's labelled errors before
  it may fire again. Without it the trigger machine-guns retrains at the same
  unresolved break.
- The reaction floor of any label-based trigger is the label delay. Nothing in
  the policy design removes it; only label-free proxies (prediction drift,
  contract breaks) shorten it. After a confirmed step change, train on the
  post-break window only; a trailing window that straddles the break averages
  two regimes and fits neither.

### Champion-challenger and shadow mechanics

Promote on a pre-registered rule, never on one good window. A working default:
the challenger scores every live row in shadow for a full business cycle, and
it gets promoted when it beats the champion on at least 8 of the last 12
weekly windows and loses no top-5 segment by more than 1 WAPE point. Keep the
deposed champion warm behind a flag for same-day rollback, and log both
models' scores on every row, because that log is the only artifact that
settles the "old model was better" meeting. Registries and schedulers for this
live in daemon-ops; the promotion rule is the part the client must co-sign.

### Models that write their own labels

When the model's output triggers the intervention that changes the label, the
label stream stops being ground truth (performative prediction; Perdomo et
al., ICML 2020). A maintenance model that schedules a work order prevents the
failure it predicted, so its positives vanish and retraining teaches it that
its strongest signals were false; the same mechanism appears when a rising
no-fault-found rate is read as model decay. A retention model routes offers to
its high-risk scores, the offers suppress the churn, and the retrained model
unlearns exactly its best features. Defences, in order of preference: keep a
small randomized control slice (5-10%) outside the intervention path and
retrain and evaluate on it, price that slice with the client because it has a
real cost; log every intervention as first-class data and model the outcome
conditional on treatment; when neither is possible, freeze the model and say
why. The causal-inference skill owns the estimation details;
predictive-maintenance and customer-analytics carry the domain versions of
this trap.

## Forecast governance

### The FVA stairstep, computed honestly

Forecast value added compares each step of the planning process to the step
upstream of it and to a naive baseline (Gilliland's methodology). Two rules
keep the table honest: score every step on the identical rows (a step that
only touches easy series looks brilliant on its own sample), and compute in
WAPE with bias beside it; Davydenko and Fildes (2013) showed MAPE-based
adjustment conclusions flip sign on the same data because MAPE rewards
under-forecasting. From `assets/fva.py`, 40 SKUs, 48 months, 1,440 scored
rows:

| Step | WAPE | Bias | FVA vs seasonal naive | FVA vs previous step |
|---|---|---|---|---|
| Seasonal naive | 20.4% | -1.2% | 0.0 pp | |
| Naive | 21.9% | 0.0% | -1.5 pp | -1.5 pp |
| Statistical | 15.9% | -0.3% | +4.6 pp | +6.0 pp |
| Planner | 16.6% | +3.1% | +3.8 pp | -0.7 pp |
| Consensus | 17.2% | +5.2% | +3.3 pp | -0.6 pp |

The statistical model added 4.6 points over seasonal naive; the planner
meeting gave 0.7 back and the consensus meeting another 0.6 while bias climbed
to +5.2%. Every negative number in the last column is a recurring meeting with
a price on it. Present the table exactly like this to the planning
organization: people defend their step until they see its row.

### Overrides, and what the evidence says about them

The largest published study (Fildes, Goodwin, Lawrence and Nikolopoulos 2009;
over 60,000 forecasts across four supply-chain companies) found judgmental
adjustments helped on average in three of the four firms, with sharp
structure underneath: large adjustments improved accuracy on average, small
ones damaged it, and downward adjustments beat upward ones by a wide margin
because upward adjustment carries optimism (one firm adjusted 91% of all its
forecasts). Franses and Legerstee found comparably high adjustment rates in
pharmaceutical SKU forecasts. The operational conclusions: overrides earn
their keep only when logged and scored; small habitual touches are process
cost with negative return; and a recurring, explainable override (a
distributor calendar, a promotion) is a feature request for the model.

Log every override with date, series, owner, stated reason, the statistical
number, the final number, and later the actual. `assets/override_scoring.py`
turns that log into the quarterly review tables; on its synthetic quarter the
direction-by-size table reproduces the published pattern:

| Direction, size | n | Hit rate | Net WAPE pp |
|---|---|---|---|
| Down, large | 82 | 63.4% | +9.39 |
| Down, small | 75 | 45.3% | -0.07 |
| Up, large | 15 | 46.7% | -2.45 |
| Up, small | 164 | 34.1% | -1.65 |

Run the quarterly meeting off three tables (owner scorecard, direction-by-size,
by-reason): keep the override classes that pay, move learnable reasons into
the feature set, and show the padding habit next to its price. Score owners on
net WAPE points and hit rate together; a 55% hit rate with negative net points
means many small wins funding a few large misses, and that pattern gets named
in the meeting.

### Plan stability is a deliverable

Planners consume the forecast as a plan, and a plan that whipsaws gets
abandoned even while its accuracy improves, because every revision costs
purchase orders, labour schedules, and trust. Measure churn explicitly:
period-over-period revision of the published plan, sum|F_new - F_old| /
sum|F_old| over the shared horizon (`plan_churn` in `assets/fva.py`). The demo
re-forecasts an identical quarter weekly with fresh noise and churns 9-14% a
week with zero information gain; that is pure cost. Dampen at the publication
layer: release a revision only when it clears a materiality floor (one week of
supply works as a default), batch revisions to the S&OP calendar, and report
churn next to WAPE in the monthly health report. Van Belle, Crevits and
Verbeke (IJF 2023) showed forecast stability can be optimized for directly at
little accuracy cost; the trade is usually worth making, and the client should
choose it consciously.

## Monitoring the client keeps using

### Data contracts sit upstream of every drift metric

Most production incidents enter through the data, so the first monitor is a
contract on the model's inputs, checked before scoring: schema (names, types),
null shares per column against a band, row volume against a seasonal
expectation band, unit sanity (currency, kg vs tonnes, percentage vs
fraction), and freshness (max event timestamp against the clock). Google's
TFX team built exactly this layer and reported it catching serving skew and
schema breaks that model metrics surface weeks later (Breck et al., MLSys
2019); 92% of 53 surveyed ML practitioners reported data-cascade incidents
compounding from small upstream issues (Sambasivan et al., CHI 2021). The
operating rule: every accuracy incident starts its investigation at the
contract log, and drift metrics get read second, because a unit change looks
exactly like drift and retrains catastrophically.

### The alert budget

Alerting doctrine comes from daemon-ops and applies unchanged: alerts to a
human channel are composed diagnoses with the evidence inline, never template
strings, and the channel carries a budget (two non-incident alerts per model
per week is a working default). When the budget blows, raise thresholds until
it holds; a channel the client stops reading has negative value, and every
false alarm spends trust the true alarm will need. Everything below the alert
line accumulates into the monthly report.

### The one-page monthly health report

One page, same layout every month, written as prose by whoever (or whatever)
composes the diagnosis, with the numbers pinned:

```
MODEL HEALTH - <model name> - <month>
Verdict: one sentence. Healthy / degraded / broken, and the single cause.
Volume scored:      1,204,332 rows   (+3% vs prior month, inside band)
Accuracy (closed):  WAPE 14.2%       (prior 13.8%; contract gate 18%)
Bias (closed):      +1.1%
Worst drift:        x_7 W1/sd 0.24   (unit change confirmed 2026-06-14, fixed at source)
Overrides:          net +0.4 WAPE pp quarter to date, 61% hit rate
Incidents:          1 schema break, caught at the contract, zero scoring impact
Action:             the one thing that changes before the next report
```

The verdict line is the report. A client executive reads that line for
eighteen months and then stops needing you, which is the goal.

## Handoff

### The runbook names symptoms, first checks, and responses

| Symptom | First check | Response |
|---|---|---|
| Accuracy fell off a cliff this week | Contract log, then per-column null shares | Roll back to the last good feature snapshot; never retrain onto an unexplained break |
| Drift alarm on one feature, accuracy flat | Unit or scale change upstream | Fix at the source or refit that one transform; record it as a data incident |
| Drift alarm every period-end | Calendar context missing from features | Annotate the alarm now; add calendar features at the next retrain |
| Scores collapse toward the mean | A join serving nulls or defaults into features | Roll back, then add the join to the contract |
| Trigger fired, retrain, trigger fired again after cooldown | Step change in the relationship | Retrain on the post-break window only; rerun the validation gate |
| ELSE | Reproduce one scored row end to end by hand | Escalate to the named model owner with that row attached |

### The model card states what invalidates the model

Use the model-card structure (Mitchell et al. 2019) and spend the effort on
the limitations section, written as invalidation events in the client's own
vocabulary: "trained on 2023-2025 order history; opening a distribution
centre, restructuring the price list, or running promotion mechanics unseen in
training invalidates the affected segments until retrained". The card lives in
the repo beside the model and gets updated at every retrain, because a stale
card reads as authoritative and lies. Cards written as compliance filler get
abandoned within months; cards that answer "when do I stop trusting this"
get opened during incidents.

### The retraining playbook is executable by a client analyst

One document: the exact command, the data-window rule, the validation gate
with numbers (a working default: the candidate beats the incumbent on the
last 8 closed weeks overall and loses no top-5 segment by more than 1 WAPE
point), the sign-off owner by name, the rollback command, and the calendar.
If executing it requires reading model code, it is documentation for the
authors and the handoff has not happened.

### Teach or keep managed, decided by the client's bench

| Client bench | Teach | Keep managed |
|---|---|---|
| Data-science team with an on-call rotation | Everything: retraining, thresholds, monitoring internals | Nothing; quarterly review only |
| Analysts (SQL-fluent, no ML practice) | The playbook, the health report, the override review | Threshold changes and any model change |
| IT operations only | Contract-log reading, report distribution | Retraining and monitoring, under a priced service agreement |
| ELSE (no technical bench) | Reading the monthly report | Everything, under a service agreement with a stated sunset date, said out loud in the handoff meeting |

A model that nobody on the client side owns dies quietly; the only open
question is how many quarters of bad decisions it makes first. Two calibration
stories with numbers, useful in the handoff conversation: an external
validation of Epic's sepsis model found AUC 0.63 against the vendor's reported
0.76-0.83, missing 67% of sepsis cases while alerting on 18% of all admissions
(Wong et al., JAMA Internal Medicine 2021), the cost of deploying a model
without local validation and monitoring. Unity took a revenue impact it sized
near US$110M in 2022 after bad data from one large customer fed its
ad-targeting model unchecked, the cost of a missing data contract. Resist the
"87% of models never reach production" statistic in client materials; it
traces to a 2019 VentureBeat piece with no underlying study
(references/handoff-decay.md has the provenance).

## Files

- `assets/drift.py` PSI with binning sensitivity, two-sample KS, scaled
  Wasserstein, per-column report; demo reproduces every drift number above.
- `assets/fva.py` FVA stairstep on identical-row samples plus the plan-churn
  metric; demo reproduces the governance tables.
- `assets/retraining_policy.py` calendar and trigger policies backtested on a
  drifting synthetic world with label delay and a costed ledger.
- `assets/override_scoring.py` override log to owner scorecard,
  direction-by-size table, and by-reason table.
- `references/drift-math.md` PSI null derivation, threshold tables, KS and
  Wasserstein details, categorical handling.
- `references/governance-evidence.md` the override and FVA evidence with the
  published numbers, and the stability literature.
- `references/handoff-decay.md` post-deployment decay evidence, named failure
  cases, folklore-statistic provenance, handoff practice.
- `references/sources.md` every source with URL and access date.
