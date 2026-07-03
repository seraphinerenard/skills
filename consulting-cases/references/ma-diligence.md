# M&A diligence depth

<!-- allow:C1 synergy is the M&A term of art throughout this file -->

The dedicated M&A researcher for this build was cut off before returning a
URL-verified sheet, so this file cites by name and flags what needs a fetch
before client use; the mechanics themselves are standard practice.

## Retention benchmarks for reading a data room

Practitioner ranges, stated as ranges because segment mix moves them
(verify against a current benchmark study before quoting to a board):
enterprise SaaS typically holds GRR 90-95% and NRR 105-120%; mid-market runs
several points looser on both; SMB books commonly sit at GRR 75-85%, where
the durability constant in SKILL.md bites hardest (at GRR 80% and a 10%
discount rate the existing book is worth ~2.6 years of current revenue).
Read cohorts, never blended rates: a blended NRR of 110% built from an
expanding top decile over a churning base is a different asset from a
uniform 110%, and the cohort curves from `assets/cohort_engine.py` separate
the two in one chart. Compute GRR and NRR from the raw transaction tape
yourself; management-computed retention embeds definitional choices
(logo-weighted, seat-weighted, excluding "strategic churn") that flatter.

## Quality-of-earnings red flags, detectable in data

| Signature in the data | What it suggests | First check |
|---|---|---|
| Revenue spikes in the last week of quarters, receivables growing faster than revenue | Pull-forward / channel stuffing | Shipment-date vs order-date distributions by quarter-week; DSO trend |
| Rising share of revenue from "one-time" items reclassified period to period | Adjusted-EBITDA management | Reconcile every adjustment line to the GL over 8+ quarters |
| Gross margin stable while unit economics deteriorate underneath | Cost capitalization moved | Capitalized-cost roll-forward against engineering headcount |
| Deferred revenue falling while bookings claims rise | Recognition timing pulled | Contract-level waterfall from the tape |
| Growing gap between EBITDA and operating cash flow | Accruals absorbing the story | Cash conversion by quarter, working-capital bridge |

Enforcement anchors exist for each pattern (US enforcement actions on
pull-forward disclosure and on expense-management misconduct at large
consumer companies in 2020-2021 are the usual citations); pull the specific
case documents before naming names in a report.

## Concentration and contract diligence

Compute customer concentration as both top-N shares and an HHI on revenue;
pair it with contract terms, because a 30% customer on a 5-year contract
with 24-month termination notice is a different risk from the same share on
rolling 30-day terms. Churn-adjust the concentration: weight each account's
share by its cohort's survival curve to get expected revenue at risk per
year. Flag related-party revenue and reseller chains that hide end-customer
concentration.

<!-- allow:C1 synergy is the M&A term of art -->
## Synergy realization, the base rates

Consultancy surveys (McKinsey and Bain both publish recurring versions)
<!-- allow:C1 synergy is the M&A term of art -->
repeatedly find cost synergies mostly land near announced targets while
revenue synergies land far below them and later than modelled; treat those
as directionally reliable survey claims and fetch the current edition for
numbers. The modelling consequences, which stand on their own: build cost
synergies bottom-up with named actions, dates, and one-time costs; discount
<!-- allow:C1 synergy is the M&A term of art -->
revenue synergies separately and steeply for realization risk; never let a
terminal value capitalize a synergy that has a ramp.

## ML and technology diligence protocol

1. Re-run the target's headline model metric on a holdout you construct
   from their raw data, with their preprocessing frozen; accept only
   metrics that reproduce within noise. (The Epic sepsis external
   validation, AUC 0.63 against a reported 0.76-0.83, is the canonical
   citation for why vendor-reported metrics need local validation.)
2. Audit for leakage in their pipeline (temporal splits, target-derived
   features, group contamination) with the feature-engineering skill's
   taxonomy; leakage inflates every claimed metric.
3. Data rights: confirm the training data survives the transaction
   (licenses, consent scope, residency), because a model whose training
   data cannot be re-licensed is a depreciating asset with no maintenance
   path.
4. Retraining dependency: who retrains it, on what cadence, at what cost,
   and what happened the last three times; a model without a retraining
   history is untested against drift.
5. Key-person and vendor concentration on the pipeline itself.

Score each dimension pass / conditional / fail with the evidence attached;
the deliverable sentence for a conditional is what it costs to cure.
