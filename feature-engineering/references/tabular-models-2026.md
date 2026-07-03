# Tabular models 2024-2026 and the economics of hand-crafted features

Depth note behind SKILL.md section 1. URLs in `sources.md`.

## The TabPFN family

- TabPFN v2 (Hollmann et al., "Accurate predictions on small data with a tabular
  foundation model", Nature 637:319-326, January 2025): a transformer pre-trained on
  synthetic tabular tasks that predicts in one forward pass, no gradient fitting on
  the client dataset. Official support: up to 10,000 rows, 500 features, 10 classes,
  numerical and categorical inputs with missing values. Under that envelope the
  published and third-party benchmarks show it beating default XGBoost on
  essentially every dataset and matching or beating hours of tuned AutoML in
  seconds; past ~10k rows memory and accuracy both degrade and gradient boosting
  takes back the lead (independent benchmark: HumbleBeeAI, November 2025).
- TabPFN-2.5 (Prior Labs, arXiv 2511.08667, November 2025): the envelope grows to
  roughly 50,000 rows and 2,000 features. On TabArena-lite it outperforms every
  single model in a forward pass, and the fine-tuned Real-TabPFN-2.5 gains further;
  AutoGluon 1.4 "extreme" (a 4-hour tuned ensemble that already includes TabPFNv2)
  is the horizontal reference line the paper plots against.
- A "Closer Look at TabPFN v2" (arXiv 2502.17361) documents strengths and the
  failure modes: high-dimensional, large, and strongly non-IID tables remain weak
  spots, which covers most panel and time-series consulting data.

## What this changes for feature work

Inside the envelope (static table, tens of thousands of rows or fewer, IID-ish
sampling), interaction crosses, monotone transforms, and binning are priced into
the model; hand-crafting them buys little. Run the foundation model as the first
baseline: it is the cheapest strong benchmark available, and it calibrates how much
headroom manual work has.

Outside the envelope the pre-2024 economics hold, because the missing information
never reaches the matrix:

- Temporal structure in panels: lags, rolling stats, event distances (SKILL.md
  section 3) exist only if the pipeline builds them. Time-series foundation models
  (Chronos-Bolt, TimesFM, Moirai) forecast raw series without covariates well, and
  documented competition practice on covariate-rich retail panels still runs
  feature-built GBMs (M5 evidence and the mlforecast toolchain; see
  `research/practitioner-fe-canon.md`).
- Cross-row group statistics (shares, group z-scores) and domain joins (weather,
  promo calendars, distribution data) sit outside any single-table model's reach.
- Leakage discipline, train-serve alignment, and the completeness checks bind
  regardless of model family; a foundation model overfits a leaked feature exactly
  as happily as LightGBM.

## Automated and LLM-assisted feature generation

OpenFE (arXiv 2211.12507, ICML 2023) generates and filters arithmetic feature
candidates at scale; CAAFE (arXiv 2305.03403, NeurIPS 2023) has an LLM propose
semantically motivated features from column descriptions. Both are candidate
generators with the same acceptance bar as a hand-written feature: out-of-fold
evaluation, the null-importance screen, and the family ablation of SKILL.md section
5. Their observed wins concentrate on small datasets where a few interactions carry
signal; on panel data they do not build the temporal canon for you.

## Working defaults

| Data shape | Default | Challenger |
|---|---|---|
| Static, under ~50k rows | TabPFN-2.5 forward pass | Tuned LightGBM + engineered ratios/joins |
| Static, past ~50k rows | LightGBM/CatBoost + engineered features | AutoGluon ensemble |
| Panel / time series | Feature-built GBM per SKILL.md section 3 | Chronos-Bolt or TimesFM zero-shot |
| ELSE | Engineered-GBM baseline; add one foundation-model challenger; keep the honest-CV winner | Revisit when the vendor envelope moves again |
