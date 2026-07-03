---
name: causal-inference
description: Causal measurement for consulting engagements. Use for geo experiments and matched-market tests, price and promo incrementality tests, switchback and clustered designs, CUPED variance reduction, staggered difference-in-differences and event studies, synthetic control, uplift validation, and marketing mix models calibrated with experimental lift. Trigger phrases include "did the campaign work", "design a test", "incrementality", "holdout", "geo test", "measure the price change", "MMM", "synthetic control", "diff-in-diff".
---

# Causal inference for consulting engagements

This skill assumes full command of potential outcomes, regression, and the
standard estimators. It records the judgment layer: which design answers which
client question, the math that sizes a test before anyone commits revenue to
it, the observational estimators that survive referee scrutiny in 2026, and
the traps that produce confident wrong answers. Runnable implementations sit
in `assets/`; every number quoted from them below is the actual output of the
demo on synthetic data with known truth.

The consulting frame differs from the platform-experimentation frame in one
structural way: experiments here exist to validate the parameters other models
assume. The elasticity in a pricing engine, the uplift in a retention
programme, and the channel contribution in a media plan are all claims that a
well-designed test either confirms or kills. Budget the test as part of the
model's cost.

## Choosing the design

| Client question | Data situation | Design | Analysis |
|---|---|---|---|
| Does the national campaign lift sales | Few large units (markets, regions) | Geo experiment, treated markets vs synthetic control | `assets/synthetic_control.py` with placebo inference |
| Does the price change move volume and margin | Store or region panel, price under our control | Randomized price test across stores or geos, guardrailed | Diff-in-means with CUPED, cross-reference price-optimization |
| Does the retention offer work | Individual-level randomization possible | RCT with uplift analysis | Cross-reference customer-analytics for Qini evaluation |
| Does the marketplace or logistics change work | One market, interference between units | Switchback | Burn-in exclusion, cluster-level inference |
| Policy already rolled out, staggered by unit | Panel with adoption dates | Staggered DiD, group-time ATTs | `assets/staggered_did.py`; never plain TWFE |
| Policy hit one unit at a known date | Long pre-period panel of untreated peers | Synthetic control | Placebo tests over donors |
| How do channels share credit for revenue | Weekly spend and outcome history, few or no experiments | MMM, calibrated with any lift test available | `assets/mmm_calibrated.py` |
| ELSE | Nothing randomizable, no panel structure | Say plainly that causal measurement is not available; deliver descriptive analysis labelled as such and a design proposal for the next quarter | AskUserQuestion if scope is ambiguous |

Two rules sit above the table. First, the design conversation happens before
the intervention, because retrofitted identification is weaker than designed
identification at any sample size. Second, when the client asks for a causal
number that the data cannot support, the deliverable is that sentence, with
the design that would support it and what the design costs.

## Pre-registration with the client

Agree four things in writing before launch: the primary metric, the minimum
detectable effect, the duration and stop rule, and who sees interim numbers.
This is thirty minutes of work that prevents the two standard failure modes:
the metric that migrates after results arrive, and the test that ends early
because someone peeked at week two.

The MDE conversation needs numbers, and simulation on the client's own
history beats formulas because it inherits the real autocorrelation and
cross-market covariance. `assets/power_sim.py` runs the full loop: fit the
synthetic control on pre-period history, inject synthetic lifts, and count
rejections. Its demo, sized like a small consumer test (25 geos, 92 weeks of
history, 5 treated geos, a 4-week test, one-sided alpha 0.05), lands at an
MDE of 1.4% lift at 80% power, and the same run shows the honest
false-positive rate at zero lift (0.08, near its nominal level). When the
hoped-for effect is 1% and the MDE comes back at 3%, the options are a longer
test, more treated units, a lower-variance metric, or CUPED; running anyway
and reporting a null is the one option that costs money and answers nothing.

Holdout politics is a sizing constraint. Treated markets in a pricing test
carry real margin risk, and a control group in a media test is revenue the
media team believes it is losing. Size the treated fraction to the smallest
set that clears the MDE, present the opportunity cost per week alongside the
information value, and put an abort threshold in the pre-registration so a
badly wrong price exits on a rule.

## Geo experiments

### Market selection and the synthetic control

Select treated markets so that the remaining donors can reproduce their
pre-period path; the pre-period fit is the design's quality gauge. The
implementation in `assets/synthetic_control.py` fits simplex-constrained
ridge weights (weights are non-negative and sum to one, so the counterfactual
never extrapolates outside the donor hull) on the pre-period, then carries
them forward. In its demo (25 geos, 70 pre-period weeks, 10 test weeks, true
lift +5.0%), the fit reaches a pre-period RMSPE of 1.155 on a treated level
near 55, recovers +4.82%, and concentrates weight on three donors
(0.40/0.24/0.24), which is typical and fine.

Inference is permutation over donors: assign the treatment to each donor in
turn, compute each post/pre RMSPE ratio, and rank the treated unit. The demo
returns a ratio of 2.72 and a placebo p-value of 0.040, and that value equals
1/25, the floor for 25 units. This floor is the load-bearing planning fact:
with N units the smallest achievable p-value is 1/N, so a 10-geo test can
never clear 0.05 by permutation. Plan unit counts around the floor, or run
multiple treated units and pool.

Augmented synthetic control (ridge correction on the gap when the hull fit
is poor) is worth reaching for when donors cannot bracket the treated market;
the base implementation flags this through pre-period RMSPE, and a poor fit
is an instruction to change the design before launch.

### When geo tests fail

Geo designs fail on too few units (the 1/N floor), on national media that
contaminates controls, on spillover across market borders (commuters,
e-commerce delivery zones), and on concurrent events that hit treated and
control markets asymmetrically. The first two are visible at design time.
For border spillover, buffer or drop adjacent markets. For concurrent
events, the placebo distribution absorbs symmetric shocks; asymmetric ones
need an event log kept during the test, agreed as part of pre-registration.

## Switchbacks and clustered designs

Switchbacks (whole-system toggling over time windows) handle interference
that unit randomization cannot, and they pay for it with carryover: each
window inherits state from the previous condition. Exclude a burn-in prefix
from every window, sized from the system's relaxation time (queue drain time,
driver repositioning time), and randomize windows in blocked pairs so
time-of-day confounds cancel.

Cluster randomization prices its correlation. With mean cluster size m and
intra-cluster correlation rho, the design effect is 1 + (m - 1) * rho, and
the effective sample size divides by it. Twenty stores of 500 transactions
each at rho = 0.05 give a design effect of 1 + 499 * 0.05, near 26, so the
10,000 transactions carry the information of roughly 385 independent ones.
Store-level tests are geo tests in miniature; analyze at the cluster level
and treat the transaction count as decoration.

## Variance reduction with CUPED

CUPED subtracts the predictable part of the outcome using pre-period data:
with theta = cov(y, x) / var(x), analyze y - theta * (x - mean(x)). The
variance falls by the factor 1 - rho^2, where rho is the pre-post
correlation, and that identity is exact, so expectations can be set before
the test from the observed rho. At rho = 0.70 the variance halves. The demo
in `assets/cuped.py` (n = 20,000 per arm, rho = 0.697) cuts the standard
error from 0.101 to 0.072, a 49% variance reduction matching 1 - rho^2 =
0.515, and is equivalent to raising n from 20,000 to 38,873. Revenue-type
metrics on returning customers usually carry rho between 0.5 and 0.8, so
CUPED buys back a third to two thirds of the sample; new-customer metrics
carry no pre-period and CUPED does nothing. CUPED never changes what is
estimated, only the noise around it.

## Observational methods, ranked by defensibility

When randomization is off the table, the estimators below run from most to
least defensible. The ranking is about how much the audience must take on
faith, and a consulting deliverable states which rung it stands on.

### Staggered difference-in-differences

Plain two-way fixed effects on staggered adoption is broken under
heterogeneous effects: already-treated units serve as controls for
later-treated ones, and the implied weights can turn negative
(Goodman-Bacon decomposition). The demo in `assets/staggered_did.py` makes
the size of the problem concrete: with a true overall ATT of 3.07, group-time
aggregation recovers 3.02 while TWFE returns 2.36, a fifth of the effect
gone, and the max pre-period placebo sits at 0.07. Estimate group-time ATTs
(Callaway and Sant'Anna) with never-treated or not-yet-treated controls,
aggregate to event-study and overall effects, and bootstrap at the unit
level.

Python tooling, verified 2026-07-12 against PyPI and GitHub (details and
URLs in `references/research/staggered-did-implementations.md`):

| Package | Status | What it covers |
|---|---|---|
| pyfixest 0.60.0 | active, mirrors R fixest | Sun-Abraham (`sunab`), Gardner `did2s`; no Callaway-Sant'Anna |
| csdid 0.4.2 | maintained; Sant'Anna among maintainers | Port of the R `did` package |
| differences 0.3.0 | revived Apr 2026, low activity | Faithful `ATTgt` |
| diff-diff 3.7.0 | six months old, broad, unproven | CS, Sun-Abraham, imputation, HonestDiD bundled |
| R `did` 2.5 | the reference implementation | Validate any Python result against it for high-stakes work |
| ELSE | none of the above installable | Hand-rolled group-time aggregation as in `assets/staggered_did.py` |

### Pre-trends, honestly

Flat pre-trends support the design; they do not establish it. Roth (AER:
Insights, 2022) shows conventional pre-trend tests often lack power, and
conditioning on passing them distorts both estimates and coverage. So report
the event-study plot with its pre-period placebos, and pair it with
Rambachan-Roth sensitivity: how large a parallel-trends violation, relative
to the largest pre-period deviation, would erase the result. A conclusion
that survives violations twice the observed pre-trend wobble is worth
presenting; one that dies at half of it is a hypothesis.

### Synthetic control against DiD

Use DiD when many units adopt and the counterfactual is an average; use
synthetic control when one or few units are treated and a weighted donor
combination tracks them closely pre-period. The two disagree most when the
treated unit sits at the edge of the donor distribution, where DiD
extrapolates and synthetic control refuses to; in that situation the refusal
is information.

### Flexible estimators and instruments

Double ML and causal forests estimate heterogeneous effects under selection
on observables, and the assumption travels with the estimate: no unobserved
confounder survives the controls. In business data the confounder is usually
management choosing where to intervene, which no covariate set fully
carries. Use them to rank segments for a follow-up experiment; hesitate to
bill the CATE itself as the finding. Instruments in business data are mostly
weak: report the first-stage F, and below roughly 10 (or under modern
heteroskedasticity-adjusted thresholds, well above it) treat the IV estimate
as unreported.

## Marketing mix models

MMM regression with carryover and saturation: spend transforms through
geometric adstock (x*_t = x_t + theta * x*_{t-1}) and a Hill curve
(z / (z + K)), then enters a regression with seasonality and base demand.
The likelihood is nearly flat along two ridges: theta trades against K
(carryover mimics saturation on weekly data), and collinear channels trade
contribution between themselves. This is a property of the data, and more
sampling does not remove it.

The working fix is calibration: fold any experimental lift estimate in as a
prior on that channel's contribution. `assets/mmm_calibrated.py` runs MAP
plus a Laplace approximation with a geo-test prior on one channel; in its
demo (156 weeks, 3 channels, true contributions known), the uncalibrated
model assigns channel 1 a contribution of 42.8 with posterior sd 43.9,
while the calibrated run lands at 59.8 with sd 8.8 against a truth of 59.0,
and the collinear partner channel corrects with it. One geo test tightened
the whole system. Deliverables report marginal ROAS at current spend with
intervals (the demo prints 1.14 [0.70, 1.56] for the calibrated channel),
and every MMM deliverable carries a scope statement naming the channels the
model cannot separate and the spend ranges outside the observed data.

Tooling: pymc-marketing (0.19.4, May 2026, verified on PyPI) carries the
maintained open-source MMM with adstock and saturation built in; the
household names in closed and semi-open tooling change quickly, and this
session could not verify their current status, so check before recommending
one by name.

## Cross-cutting traps

- Novelty and Hawthorne effects inflate early weeks; read effects from the
  stabilized window the pre-registration named.
- Seasonality confounds any before-after comparison; that is what the
  control side is for, and a "test" without one is a trendline.
- Interference between test and control stores (shared distribution
  centres, cross-store shoppers, reallocated field teams) biases toward
  null in some designs and away in others; walk the operational graph
  before assigning units.
- Peeking without alpha-spending turns a 5% test into a 20% one; if the
  client needs interim looks, build them in with group-sequential bounds.
- The metric moved after launch is the analysis dying quietly; the
  pre-registered metric is the deliverable, everything else is exploratory
  and labelled so.

## Files in this skill

- `assets/synthetic_control.py` simplex-ridge weights, gaps, placebo
  inference; demo recovers +4.82% on a true +5.00% with p = 0.040.
- `assets/power_sim.py` simulation power analysis over client history;
  demo MDE 1.4% at 80% power on 25 geos.
- `assets/cuped.py` CUPED with the 1 - rho^2 identity checked in the demo.
- `assets/staggered_did.py` group-time ATTs, event-study aggregation,
  TWFE comparison, unit bootstrap.
- `assets/mmm_calibrated.py` adstock + Hill MMM with lift-test calibration
  and posterior contributions.
- `references/research/staggered-did-implementations.md` sourced tooling
  survey with URLs, verified 2026-07-12.
- `references/sources.md` the source list with verification status.

Every asset runs on numpy/pandas/scipy alone and prints a smoke test with
known truth; run them before first client use and after any environment
change.
