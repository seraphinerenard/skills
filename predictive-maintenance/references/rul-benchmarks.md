# Why published RUL results transfer poorly

The C-MAPSS turbofan datasets dominate the remaining-useful-life
literature, and headline results there (RMSE 11 to 13 cycles on FD001 for
LSTM and transformer models) set client expectations that field projects
cannot meet. The gap has identifiable causes. Source IDs resolve in
`sources.md`.

## What the benchmark protocol hides

1. The capped target. Standard practice clips the RUL label at 125 cycles
   (piecewise-linear target), so most of the trajectory carries a constant
   label. A model that outputs the cap until late life scores well on RMSE
   while carrying no early-warning information; the cap value itself is a
   convention with no physical basis (S4). Reported RMSE is on the capped
   scale and does not translate to hours-of-warning on any real asset.
2. Complete run-to-failure histories. Every training unit in C-MAPSS runs
   to failure. Real fleets are 40 to 80% censored because preventive
   replacement truncates lifetimes, so the supervised-regression framing
   collapses before training starts; survival formulations exist precisely
   to absorb this (S5 documents the truncated, right-censored structure of
   even the C-MAPSS test split).
3. Normalization leakage. Per-unit or per-operating-condition
   normalization uses statistics from the whole trajectory, including its
   end. Any pipeline that standardizes a unit's sensors using that unit's
   full history has told the model where the trajectory ends.
4. Homogeneity. One engine model, simulated physics, six operating
   regimes. A mining fleet's "same" component population spans ore bodies,
   operators, and rebuild states, and cross-fleet transfer is the norm at
   deployment. Domain-adaptation papers exist because vanilla transfer
   fails (S4).
5. Selection on the benchmark. A decade of papers tuned on four fixed
   test splits produces winner's-curse results; reproduction attempts with
   honest protocols land materially worse (S4 reviews the spread).

## What deploys

Two RUL method families survive contact with real fleets, and both
condition on the asset's own trajectory:

1. Similarity-based: build a library of historical health-index
   trajectories, match the current asset by trajectory distance, and read
   RUL as the weighted quantiles of the matched units' remaining lives.
   Produces a distribution and degrades gracefully when the library is
   thin: the match set is inspectable, so a planner can see which
   histories drive the estimate.
2. Degradation-curve extrapolation: fit a monotone curve (spline, gamma
   process, or a state-space trend) to the asset's own health index and
   extrapolate to the failure threshold with uncertainty. Works when a
   scalar index exists and moves monotonically (liner wear, envelope band
   energy, wear-metal rate); fails when degradation is stepwise or the
   index saturates, so check monotonicity per failure mode first.

When no monotone index exists, or when the planning question is "which
assets get the six inspection slots this week", RUL is the wrong
deliverable and a short-horizon failure probability with an event-based
evaluation is the right one; the argument with numbers is in `SKILL.md`
section 4.

## Sensor foundation models, status mid-2026

Time-series foundation models consolidated around TimesFM (Google),
Chronos-2 (Amazon), and MOIRAI-MoE (Salesforce) through 2024-2025, and
TimesFM is generally available inside BigQuery ML for forecasting (S12).
For PHM specifically, the credible evidence as of 2026-07 is research-tier:
frozen foundation-model embeddings with a light regression head report
data-efficient RUL estimation above conventional baselines on benchmark
and industrial-style datasets (S11). No independently documented
production condition-monitoring deployment of these models in mining or
heavy industry surfaced in a 2026-07 search; vendor material claiming
"10x-30x ROI" for foundation-model predictive maintenance is marketing
without a named site or a denominator (S12). The defensible consulting
position: use them as one feature extractor inside the evaluation harness
of `event_evaluation.py`, and let event recall at fixed false-alarm budget
decide against the EWMA-on-band-energy baseline, which is cheaper to run
and to explain.
