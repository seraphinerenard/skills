---
name: feature-engineering
description: |
  Cross-cutting feature craft for ML and analytics consulting datasets. Trigger on:
  "engineer features for this model", "build lags and rolling windows", "target-encode
  this column", "join weather to sales", "clean POS / scanner / ERP / SCADA data for a
  model", "my CV score beats the live run", "when do I stop adding features",
  "/feature-engineering". Owns leakage discipline, the panel feature canon, industry
  data-source traps, and the completeness criteria. Vertical model choice lives in the
  sibling skills: demand-forecasting, price-forecasting, predictive-maintenance,
  customer-analytics, retail-analytics, supply-chain-optimization, causal-inference,
  model-operations.
---

# Feature engineering

This skill assumes the reader already holds the textbook: it skips definitions and
carries only judgment, worked numbers, and the traps that recur in consulting data.
Five runnable modules live in `assets/` (leak-safe panel factory, OOF target encoder,
adversarial validation, null importances, residual diagnostics); depth notes and all
source URLs live in `references/`. When a vertical skill (demand-forecasting,
predictive-maintenance, customer-analytics) names a feature family, this skill owns
how to build it without leaking.

## 1. Where hand-crafted features still pay (2024-2026)

Tabular foundation models moved the floor for small static tables. TabPFN v2
(Hollmann et al., Nature 637:319-326, January 2025) officially supports up to 10,000
rows, 500 features, and 10 classes, and beats default XGBoost on essentially every
benchmark dataset under that size; TabPFN-2.5 (arXiv 2511.08667, November 2025)
extends the envelope to roughly 50,000 rows and 2,000 features and tops the
TabArena-lite benchmark in a single forward pass, with AutoGluon 1.4's four-hour
"extreme" ensemble (which itself includes TabPFNv2) as the reference line. On data
inside that envelope, the model prices in interactions and monotone transforms on
its own, so hand-crafted crosses and binnings add little.

The envelope excludes most consulting work. Feature engineering keeps paying
wherever the information sits outside the training matrix the model sees:

| Situation | Where to spend effort |
|---|---|
| Static table, under ~50k rows, no time axis | Run a TabPFN-2.5 baseline first; hand-craft only domain joins and ratios the raw columns cannot express |
| Panel or time series, any size | Feature-built GBM (lags, rollings, calendar, price) remains the deployed default; the M5 evidence and the Nixtla mlforecast toolchain both sit here; run a time-series foundation model (Chronos-Bolt, TimesFM) as a challenger only |
| Wide tables past ~100k rows | LightGBM or CatBoost on engineered features; AutoML ensembles for the last point of accuracy |
| Text or image side data | Pretrained embeddings appended as columns; do this before any manual parsing of the text |
| ELSE | Build the engineered-GBM baseline, add one foundation-model challenger, and keep whichever wins under honest time-aware CV |

Leakage discipline (section 2) and train-serve alignment transfer to every cell of
this table; no model family removes them. Automated feature generators exist (OpenFE,
arXiv 2211.12507; LLM-driven CAAFE, arXiv 2305.03403) and work as candidate
generators; every candidate they emit still runs the same null-importance and
ablation gauntlet as a hand-written feature (section 5).

## 2. Leakage taxonomy

Every class below has burned a real engagement. The table names the case, the
detection, and the fix; the paragraphs after it carry the mechanics.

| Class | Concrete case | Detection | Fix |
|---|---|---|---|
| Target leakage | Maintenance work orders logged after a model-triggered inspection appear in the feature window; the label's consequence became a feature | Single-feature screen: any column that alone predicts the label with AUC > 0.90 gets a timestamp audit | Snapshot features as of the decision timestamp; keep a feature-availability ledger (one recorded-at timestamp per column) |
| Label contamination | Churn labels include customers a retention campaign already treated, and the campaign targeted the last model's scores | Cross-reference campaign logs against label windows; lift curves that invert on treated segments | Censor treated customers or model treatment explicitly; the causal-inference skill owns the estimator |
| Temporal leakage | Rolling mean without shift; scaler or encoder fit on full history; a global model whose SKU statistics span the test window | Shuffled-split CV beats time-split CV by a wide margin; `assets/panel_features.py::leak_check` fails a probe date | Shift before rolling; fit every transform inside the fold on past rows only |
| Group leakage | The same customer sits in train and test under plain KFold | KFold score beats GroupKFold score on the same features | GroupKFold (or time-grouped splits) on the entity key |
| Train-serve skew | Actual weather in training, forecast weather at inference | Adversarial validation between the training matrix and logged serving payloads | Train on archived forecasts at the serving lead time (GEFS v12 reforecast covers 2000-2019, free on AWS); the model-operations skill owns serving logs |
| ELSE (unexplained CV-live gap) | Any model that scores far better offline than live | Assume leakage before drift: rerun leak_check, the single-feature screen, and adversarial validation against serving data | Fix the found leak; only then consider drift |

Mechanics worth spelling out:

- The unshifted rolling is the highest-frequency bug in panel work. The window at
  row t must end at t-1, so the idiom is `shift(1)` before `rolling(w)`, per group.
  The M5 winners went further and shifted every lag and rolling feature by at least
  28 days, the full forecast horizon, so a direct model at horizon h reads nothing
  newer than t-h (sources: M5 references sheet).
- A scaler fit on full history looks harmless and moves scores on trending series:
  the 2023 fold learns the 2025 variance. The rule generalizes: any fit_transform
  (scaling, PCA, target encoding, imputation constants) happens inside the fold.
- Global pooled models leak through their encodings. A LightGBM trained across all
  SKUs with a SKU target-encoding computed over the full span hands each SKU its own
  test-window mean. The encoding must be out-of-fold in time as well as in rows.
- `leak_check` in `assets/panel_features.py` mechanizes detection: it masks the
  observed columns from a probe date onward, rebuilds the features, and diffs the
  probe rows. The demo catches a shift=0 rolling in 4 of 4 probes and passes the
  shifted build in 0 of 4.

## 3. The panel feature canon

The families below cover what wins retail, energy, and maintenance panels in
documented practice (M5, Rossmann, Favorita, Optiver, Enefit; see
`references/research/practitioner-fe-canon.md` for the per-competition detail).

### 3.1 Lags, rollings, exponential decay

- Lags at the target's own seasonal offsets (1, 7, 14, 28 for daily retail) plus a
  block at the horizon (M5 canon: lags 28 through 42 on a shift-28 base).
- Rolling mean and std over 7, 14, 30, 60, 180 on the shifted series; the long
  windows carry level, the short windows carry momentum, and the std columns let a
  GBM condition on volatility.
- Exponentially weighted means at two or three halflives replace a stack of rolling
  windows with fewer columns and no window-edge cliffs.
- Recursive models regenerate lag features at every step from their own predictions;
  direct models need shift >= horizon at build time. Pick one and audit the shifts
  against it. Nixtla's mlforecast implements both with incremental updates and is
  the practitioner default for per-series GBM pipelines.

### 3.2 Event distances and calendars

- `days_since_event` and `days_until_event` beat raw event flags because lift decays
  and pull-forward builds; both are one `searchsorted` per group
  (`assets/panel_features.py::add_event_distance`). `days_until` is legitimate only
  for plan data known in advance: promo calendars, holidays, scheduled price changes.
  For events observed after the fact, build `days_since` only.
- The M5 canon used event windows of -15 to +15 days around named events plus SNAP
  flags; the general form is one distance pair per event family, capped (365 works)
  so the "no event" case stays finite.
- Calendar features stay bounded and repeating: day-of-week, day-of-month, month,
  week-of-year. Fiscal calendars need their own dimension table (section 4, ERP).

### 3.3 Fourier terms

Harmonic count K follows AICc, with a hard cap at half the period (FPP3, section
10.5). Working defaults: weekly seasonality in daily data takes K=2 or 3 (cap 3);
yearly seasonality in daily data takes K between 5 and 12; the FPP3 monthly worked
example lands at K=6, which for m=12 equals full seasonal dummies. Fourier terms
handle long and non-integer periods (m=365.25) that seasonal dummies cannot, and
they extrapolate cleanly because they repeat.

### 3.4 Extrapolation and what to keep out of a tree

A regression tree stores a constant per leaf, so every date past the training range
falls into the last leaf and inherits that period's mean forever. Raw date ordinals,
row counters, and cumulative sums therefore flatline at inference and simultaneously
hand the adversarial classifier a perfect train/test separator; the
`assets/adversarial_validation.py` demo reads AUC 1.000 with the date ordinal in and
0.496 with it out. Handle trend outside the tree: difference or detrend the target,
or fit the tree on detrended residuals and add the trend back (the Rossmann winner
used a ridge trend adjustment on top of XGBoost). Keep the tree's inputs bounded,
repeating, or ratio-scaled.

### 3.5 Target encoding, worked

The m-estimate form: `enc(c) = (n_c * ybar_c + m * prior) / (n_c + m)`, with m in
pseudo-observations. With prior 0.20 and m 20:

- Category seen 8 times with mean 0.50: enc = (8*0.50 + 20*0.20)/(8+20) = 8/28 =
  0.2857. The prior dominates: 8 observations buy 29% of the distance to 0.50.
- Category seen 2,000 times with mean 0.31: enc = (2000*0.31 + 20*0.20)/2020 =
  624/2020 = 0.3089. The data dominate: the prior moves the estimate by 0.001.

m sets the count at which the encoder trusts the category as much as the prior;
m between 10 and 50 covers most panels. sklearn's `TargetEncoder` uses this formula
with `smooth="auto"` fitting m empirically and cross-fits by default; CatBoost's
ordered statistics (Prokhorenkova et al., NeurIPS 2018) reach the same goal by
encoding each row from earlier rows in a permutation.

The OOF discipline carries the whole value. Encoding fit on the same rows it
transforms feeds every row a diluted copy of its own label:
`assets/oof_target_encoder.py` measures the damage on a 300-level categorical with
zero real signal: the naive encoding correlates +0.287 with the target in-sample and
a linear model on it reports train R^2 = 0.083; the OOF encoding reports +0.036 and
0.001. Holdout R^2 sits at zero for both, so the naive version's entire promise was
fiction. In panels the folds must also respect time: encode from past rows only.

### 3.6 High-cardinality strategies, ranked

| Situation | Strategy |
|---|---|
| Under ~20 levels | One-hot or native categorical; nothing fancier earns its keep |
| 20 to ~1,000 levels, GBM | Native categorical handling (LightGBM `categorical_feature` with `min_data_per_group` raised; CatBoost ordered stats), or OOF target encoding |
| Past ~1,000 levels (SKU, customer, postal code) | OOF target encoding with m 10-50, plus a count/frequency column so the model sees how much to trust the encoding |
| Neural model in the ensemble | Entity embeddings (Guo & Berkhahn, arXiv 1604.06737, the Rossmann 3rd-place result); reuse the embedding as a GBM feature |
| Unbounded vocabulary, online serving | Feature hashing; accept the collisions, version the hash seed |
| ELSE | OOF target encoding with m=20 plus a count column |

### 3.7 Ratios and rates trees cannot synthesize

A tree approximates the decision boundary of a ratio with a staircase of axis-aligned
splits; supplying the ratio collapses the staircase to one split. Group-relative
features go further: a row-wise model has no access to other rows at all, so
same-day shares and group z-scores carry information no depth of splitting recovers.
The Optiver 2023 winners' alpha came almost entirely from this family (order-book
imbalance ratios and cross-sectional aggregates across stocks). Build these
deliberately:

- `discount_depth = shelf_price / base_price`, with base price as a rolling median
  of non-promo weeks; promo detection and elasticity both live in this column.
- `sell_through = units_sold / units_on_hand`; separates demand from availability.
- `share_of_category = sku_units / same_day_category_units` per store; needs other
  rows, so compute it in the pipeline, never in the model.
- `velocity = units / %ACV_distribution` in syndicated data (section 4); growth
  decomposes into distribution times velocity, and a model missing one of the two
  factors learns the other polluted.
<!-- allow:C1 utilization here is the capacity-usage ratio, a metric name -->
- Utilization, defect rates, claims per policy-month: numerator and denominator both
  drift, the rate stays stationary, and stationary features survive the adversarial
  check (section 5.1).
- Group z-scores as of t, past-only windows: `(y_lag1 - group_mean) / group_std`.

## 4. Industry dataset traps

Full detail with formulas sits in `references/industry-data-quirks.md`; the traps
that cost real days:

- POS: returns land as negative-quantity rows on the return date, so netting them
  into sales creates negative demand days that break Tweedie and log models; model
  gross sales and treat returns as their own series. Promo flags record plans;
  stores execute late or partially, so derive realized promos from price (shelf
  price under ~95% of the rolling 8-week base-price median). GS1 eliminated GTIN
  reuse for items active on 2019-01-01 or later, and histories before that legally
  recycled codes after 48 months (30 for apparel); build a surrogate item key over
  the remap chain and validate the splice by velocity continuity.
- Syndicated scanner (NielsenIQ, Circana): %ACV weights distribution by store
  volume; TDP sums %ACV across items and weeks. Panel (household) and POS-projected
  numbers disagree by construction, and the store universe rebases periodically,
  which steps every level series; carry a universe-version column across rebases.
- ERP: order date measures intent; shipment and invoice dates measure fulfillment and
  revenue recognition. Demand models on shipment dates learn the warehouse (stockouts,
  batching), so forecast on order date with requested-delivery as the timing signal.
  Backorder releases pile weeks of demand onto one day; flag them. Units of measure
  vary per item (eaches, cases, catch-weight); convert through the item-UoM table.
  4-4-5 fiscal calendars insert a 53rd week every 5 to 6 years, so fiscal
  year-over-year lags run 52 fiscal weeks through a calendar dimension; lag-364 on
  Gregorian dates silently misaligns.
- Sensor/SCADA: historians store exception-plus-compression output (deadband at the
  interface, swinging-door in the archive), so the archive is a piecewise-linear
  reconstruction; resample with time-weighted means and treat sample counts and
  variance as artifacts of the compression settings. Missing has two meanings:
  report-by-exception (no point = unchanged; forward-fill is correct) and comms
  outage (no point = unknown; forward-fill fabricates data); separate them with
  heartbeat or quality tags before any imputation.
- Weather: pick airport stations from GHCN-Daily, screen completeness (80-90%
  non-missing is the working cutoff), inverse-distance-weight 2 or 3 stations. HDD =
  max(0, base - Tmean) with Tmean = (Tmax+Tmin)/2 and base 65 F / 18.3 C; fit the
  balance point by change-point regression against actual load when the portfolio
  warrants it. Train on archived forecasts at the serving lead time; ERA5 runs 5
  days to 3 months behind real time, so it trains and backtests and never serves.
- Geospatial: H3 res 7 hexes average 5.16 km^2, res 8 0.737 km^2, res 9 0.105 km^2;
  trade-area work lives in res 7-9. Trees split lat/lon with axis-aligned
  staircases, so add one or two rotated coordinate pairs, then OOF-target-encode H3
  cell IDs for discrete catchment effects. Valhalla and openrouteservice serve
  isochrones natively; OSRM needs a table-service workaround.
- Money: deflate long-history prices and revenue with CPI (consumer) or sector PPI
  (B2B) so a tree's price splits mean the same thing across a decade; keep the
  nominal column too where price points matter (99-endings). Convert FX at the
  transaction-date rate.
- Clocks: store UTC, feature-ize in site-local time, join hourly data in UTC only.
  DST days run 23 and 25 hours; the fall-back day duplicates a local hour, and a
  local-time join doubles that hour's weather or load.

## 5. Completeness, or when the feature set is done

Feature work stops on evidence. Five checks, then the economics.

### 5.1 Adversarial validation (distribution shift)

Train a classifier to separate training rows from test/serving rows on the feature
matrix (`assets/adversarial_validation.py`). Read the OOF AUC: under 0.55 the sets
are exchangeable and the CV estimate deserves trust; 0.55 to 0.70 means mild shift,
so inspect the top adversarial features (usually time proxies) and repair them with
differences, ratios, or within-date ranks; above 0.70 means material shift, so drop
or transform culprits, reweight training rows by p/(1-p), or rebuild validation
from the most test-like rows. The demo walks 1.000 (date ordinal in) to 0.609 (a
0.6-sigma shifted column) to 0.496 (clean).

### 5.2 Null importances (does the feature beat chance)

Gain importances inflate high-cardinality and high-variance columns, so compare each
feature's actual importance against its own shuffled-target distribution
(`assets/null_importance.py`; Grellier's protocol used ~80 shuffles and scored
`log(1e-10 + actual / (1 + p75(null)))`; Altmann's PIMP fits a null distribution and
reports p-values). Keep features clearing the null 95th percentile. Two traps the
module handles: sklearn normalizes importances to sum to one, which lets strong
features push weak-but-real ones below an equal-share null, so read unnormalized
per-tree gains; and 30 shuffles screen adequately while production runs deserve 80+.
The demo keeps x1/x2/x3 (true signal, weakest at 2.7% of variance) and rejects a
2,000-level random ID that outranks nothing under raw gain comparison.

### 5.3 Permutation plateau with a noise probe

Append one Gaussian noise column, compute permutation importance on holdout, and
drop every feature scoring at or below the probe. Correlated features share
importance and can both look dead, so drop in clusters and re-check, once. When two
passes in a row remove nothing, this check is done.

### 5.4 Learning curves, two axes

Over samples: a rising validation curve with a wide train-validation gap says
variance; prune features and regularize before engineering more. Both curves flat
and low says bias; only new information (a join, a new measurement) moves it, and
more transforms of existing columns will not. Over features: add feature families in
a fixed order under the same time-aware CV and plot the score; stop when the
marginal family's gain drops inside the fold-to-fold standard deviation.

### 5.5 Residual diagnostics (the search directive)

Residuals name the missing feature (`assets/residual_diagnostics.py`):

- Ljung-Box per series on holdout residuals at the seasonal lag and twice it. The
  rejection share across series sits near the 5% false-alarm rate when clean; a
  share past ~20% says add lags or seasonal terms (working convention, calibrated on
  the demo where a missing day-of-week feature rejects in 100% of series).
- Binned mean-residual profile against each candidate column, scored by eta-squared
  (between-bin share of residual variance). On holdout residuals, eta^2 past ~0.02
  marks a candidate worth adding; the demo's missing day-of-week reads 0.875 before
  and 0.000 after.
- Bias tables (mean residual by group, by calendar slice, by price band) with
  counts, so a 2% bias on the largest store outranks a 20% bias on a tiny one.

### 5.6 Ablation and the marginal-feature economics

Ablate feature families (never single columns; correlated columns alibi each other)
under the same temporal CV and read mean delta against fold standard deviation: a
family earns its place when mean improvement exceeds one fold-std (working default;
tighten for regulated deliverables).

Then price it. A worked example with consulting numbers: a weather join moves a
grocery demand model's holdout WRMSSE from 0.640 to 0.637, a 0.5% relative gain. The
client's safety-stock simulation values 1% of forecast accuracy at about $12k/yr of
holding cost on a $1.5M average inventory position (their figure), so the join earns
about $6k/yr. It costs an archived-forecast feed at $4k/yr plus roughly half a
consulting day per quarter of pipeline maintenance (another $4k/yr at rate), plus
one train-serve skew incident to diagnose in year one. Expected value lands below
zero, so the join dies unless the client already licenses the feed. The same
arithmetic keeps a promo-calendar join that moves WRMSSE 4% at zero incremental data
cost. Accuracy deltas convert to dollars before they convert to roadmap.

### 5.7 Stopping table

| Check | Stop signal | Keep-working signal |
|---|---|---|
| Adversarial AUC (5.1) | Under 0.55 against test and against serving logs | Any feature you cannot repair below 0.70 |
| Null importances (5.2) | Every kept feature clears its null p95 | New candidates keep clearing the null |
| Permutation probe (5.3) | Two consecutive passes remove nothing | The probe outranks live features |
| Learning curves (5.4) | Marginal feature family lands inside fold noise | A family still clears fold noise |
| Residuals (5.5) | Ljung-Box rejection share near 5%; no candidate eta^2 past 0.02 | Any candidate column explains holdout residuals |
| Economics (5.6) | Next feature's priced value falls below its carry cost | A cheap join still buys measurable accuracy |
| ELSE | All six read stop: freeze the feature list, version it, and hand the pipeline to model-operations | Any single row reads keep-working: do that row's work next, nothing else |

## Assets

All five modules run on numpy/pandas/scikit-learn/scipy alone (exact pip names in
each header) and carry a `__main__` demo on synthetic data; measured demo results:

- `assets/panel_features.py`: lags, rollings, EWMs, event distances, calendar,
  Fourier, and `leak_check`. Demo: 0 violations on the shifted build, 4/4 probes
  caught on an unshifted rolling.
- `assets/oof_target_encoder.py`: m-estimate smoothing with KFold/GroupKFold OOF.
  Demo: naive encoding fakes corr +0.287 and train R^2 0.083 on pure noise; OOF
  reports +0.036 and 0.001.
- `assets/adversarial_validation.py`: OOF AUC plus permutation-ranked culprits.
  Demo: 1.000 -> 0.609 -> 0.496 across the three bands.
- `assets/null_importance.py`: unnormalized-gain null screen. Demo keeps the three
  real signals, rejects two noise columns and a 2,000-level ID.
- `assets/residual_diagnostics.py`: Ljung-Box per series, eta-squared profiles,
  bias tables. Demo: rejection share 1.00 -> 0.00 and eta^2 0.875 -> 0.000 after
  adding the missing feature.

## References

- `references/industry-data-quirks.md`: POS, scanner, ERP, SCADA, money, clocks,
  with formulas and numbers.
- `references/tabular-models-2026.md`: the TabPFN family, benchmark evidence, and
  what it changes for feature economics.
- `references/completeness-protocols.md`: the five stopping checks as step-by-step
  protocols with thresholds.
- `references/research/practitioner-fe-canon.md`: researcher fact sheet on
  M5, target encoding, null importances, tooling, and recent competitions (verbatim,
  with sources).
- `references/research/weather-geospatial-joins.md`: researcher fact sheet
  on GHCN, HDD/CDD, forecast archives, ERA5, H3, and isochrones (verbatim, with
  sources).
- `references/sources.md`: every URL with access dates.
