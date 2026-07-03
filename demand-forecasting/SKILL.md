---
name: demand-forecasting
description: Demand forecasting across industries (retail and CPG SKU-store-week, grocery perishables, building materials and aggregates, lumber, utility load, spare parts) covering method selection, censored demand, promotion effects, hierarchical reconciliation, and honest evaluation; use it when asked to forecast demand, sales, volumes, or load, to build an M5-style pipeline, to size intermittent spare-parts stock, or to vet a client's existing forecast.
---

# Demand forecasting

This skill assumes full textbook knowledge of ETS, ARIMA, gradient boosting,
and deep forecasters. It carries what generalist knowledge gets wrong on
client work: which method wins under which data shape and why, the industry
data traps that poison targets before any model sees them, the math worked
with real numbers, and the mid-2026 state of the field with sources. Runnable
code sits in assets/; derivations and extended notes sit in references/.

Sibling skills own adjacent ground: supply-chain-optimization (newsvendor and
inventory math), price-forecasting (price paths), price-optimization
(elasticity for decisions), causal-inference (promo attribution),
retail-analytics (foot traffic, phantom inventory), model-operations (drift,
retraining, forecast governance), feature-engineering (generic tabular
features). Cross-references below are deliberate boundaries.

## Method selection

Choose by data shape, then earn complexity through forecast value added. The
evidence anchor for the middle rows is M5: 42,840 hierarchical Walmart
series, where the winner (a pooled-LightGBM average, Tweedie objective)
scored WRMSSE 0.520, 22.4% better than the strongest statistical benchmark,
only 7.5% of 5,507 teams beat that benchmark at all, and every top-50 method
trained one model across many series (M5 accuracy paper, IJF 38(4) 2022;
research/m5-competition-lessons.md).

| situation | default method | mechanism |
|---|---|---|
| under ~50 series, 3+ years of history, weak covariates | per-series statistical (AutoETS, AutoARIMA, AutoTheta; MSTL when seasonality is multiple or m > 24) | nothing to pool across; auto-selection on rolling origin beats hand-picking |
| dozens to a few hundred related series, or a client who needs coefficients | pooled regularized regression: global ridge AR with generous lag order, Poisson or negative-binomial GLM for counts | a global linear AR matches per-series methods with up to two orders of magnitude fewer parameters (Montero-Manso and Hyndman, IJF 2021), and the coefficients survive a planning-meeting cross-examination |
| hundreds to tens of thousands of related series with price, promo, calendar covariates | global GBM (LightGBM default; the library choice reasoning is below), Tweedie for the point forecast, per-quantile pinball models for the distribution | cross-learning: one complex model amortized across series beats many simple ones (Montero-Manso and Hyndman, IJF 2021); covariates enter naturally |
| same, plus sub-daily granularity, very long horizons, or 100k+ series with a platform team | add deep global models (PatchTST, NHITS, TFT, DeepAR-style) as challengers | amortized training pays off only at scale; Zalando runs a 53M-parameter transformer over 1M+ articles in production (arXiv 2305.14406) |
| intermittent series, average demand interval >= 1.32 periods | Croston-family rate (SBA, TSB) plus an explicit lead-time demand distribution | per-period point forecasts and MAE-family metrics degenerate on zero-heavy series; see the spare-parts archetype |
| load or energy with weather physics | GAM or spline structure on weather with calendar interactions, plus a weather-scenario ensemble for quantiles | the temperature response is smooth, nonlinear, and stable; EDF and PJM run exactly this shape operationally |
| new items, new stores, histories under a year | attribute-based analogues plus a zero-shot foundation model | pretraining and analogues substitute for missing history |
| ELSE | seasonal naive as the floor, zero-shot Chronos-2 or Moirai-2 as the day-one baseline, global LightGBM as the first challenger; promote whatever wins rolling-origin FVA | the baseline pair costs an hour and referees every later claim |

Two failure modes of the global-model default. First, heterogeneous
assortments: pooling fashion with hardware in one model with weak series
identifiers drags both toward the pooled mean; fix with segment models or
strong static features before abandoning globality. Second, sparse bottom
levels: M5 gains over statistical benchmarks collapsed from 22% overall to
near zero at product-store level, and plain Croston beat seasonal naive
there; global ML earns its keep at and above the levels where signal exists.

## The wider model space

The table compresses a model space that deserves its reasoning stated,
because the compressed version reads as "always LightGBM" and that is wrong
in specific, predictable ways.

### Regressions keep three seats

Pooled regularized regression is the cheapest global model that exists: a
ridge AR over the panel with lags, seasonality dummies or Fourier terms, and
the covariates, fit in seconds. The theory result behind the whole
cross-learning story is linear (Montero-Manso and Hyndman proved the
equivalence and showed the parameter-budget asymmetry on global linear
autoregressions), so when a GBM barely beats this baseline the panel has no
exploitable nonlinearity and the engagement should spend elsewhere. Count
GLMs (Poisson, negative binomial with a log link) fit low-volume demand with
correct mean-variance behaviour and give incidence-rate-ratio coefficients a
category manager can interrogate; overdispersion decides between the two
(the spare-parts section's Poisson under-buy at 84% service is the same
mistake in stocking form). Dynamic harmonic regression (Fourier terms with
ARIMA errors) is the clean answer for long or multiple seasonal periods
where seasonal ARIMA cannot go (m = 52, 168, 365), with K chosen by AICc.
The utility GAM in the load section is this same family with splines, and
its operational track record at EDF and PJM is the strongest regression
evidence in the skill.

### Where classical per-series models keep the edge

ETS and ARIMA stay the right call when series are few, histories long,
seasonality stable, and covariates thin; automatic selection over a rolling
origin (AutoETS, AutoARIMA, AutoTheta in statsforecast) beats hand-picked
orders in that regime and costs minutes. Theta's M3 pedigree makes it the
strongest cheap univariate single; state-space forms carry two abilities
GBMs lack natively, adaptivity (Kalman-filtered level and coefficients
track drift without retraining, the EDF lockdown mechanism in the
structural-breaks section) and additive interpretability of level, trend,
and season. TBATS handles multiple seasonality inside one state space when
MSTL decomposition plus a simple forecaster underperforms. The honest
boundary: none of these ingest promo, price, and distribution covariates
gracefully, and M5's organizers measured what that costs (exogenous
regressors improved ES by 6% and ARIMA by 13%), so covariate-rich retail
leaves this family quickly.

### Which gradient-boosting library

The differences are second-order against feature quality, and they are
real. LightGBM took the M5 podium and the production default on
histogram-based leaf-wise growth, which is the fastest of the three on wide
panels, and it carries native Tweedie and quantile objectives. CatBoost's
distinguishing mechanism is ordered target statistics for categorical
features (Prokhorenkova et al., NeurIPS 2018), which encode high-cardinality
SKU, store, and customer identifiers with leakage protection the other
libraries need out-of-fold engineering to match; reach for it when
categorical cardinality dominates the feature set and tuning budget is
small, and accept slower training. XGBoost reaches parity with more tuning
and brings no demand-specific advantage; keep it when the client's platform
already standardizes on it. All three carry Tweedie-family losses, so the
zero-inflation argument selects none of them. Switching libraries buys a
point or two at most; switching objectives (squared error to Tweedie on
intermittent data) or fixing a leak buys ten.

### Deep forecasters, a selection map

One row in the table hides a family with internal structure. DeepAR-style
autoregressive RNNs produce parametric distributions (negative binomial for
counts) and sample coherent paths, and they accumulate error over long
horizons because each step feeds on the last; M5's third place was a
43-network DeepAR-style ensemble at WRMSSE 0.536 against the winner's 0.520
(research/m5-competition-lessons.md). Direct multi-horizon quantile
architectures (the MQ-CNN to MQTransformer lineage) avoid that accumulation
and are what Amazon has run in production since 2018. N-BEATS and N-HiTS
are univariate pattern engines with strong long-horizon behaviour; M5's
second place used N-BEATS at aggregate levels only, to derive trend
multipliers applied onto per-store LightGBM, which is the right mental
model for them: level and trend readers, weak covariate citizens (N-BEATSx
adds exogenous inputs). TFT separates static, known-future, and observed
covariates explicitly and shows attention weights a client can read, at
2-3x the training cost. PatchTST and iTransformer earn consideration at
long context lengths and sub-daily granularity. Practical judgment that
does not appear in papers: deep results vary across seeds enough that
production systems ensemble 3+ seeds; per-series scaling choices move
accuracy more than architecture swaps; parametric count losses (negative
binomial, Tweedie) beat Gaussian heads on retail data every time; and the
break-even against a tuned GBM sits around tens of thousands of series with
a platform team to own GPU training, which is where Zalando (53M-parameter
transformer, 1M+ articles) and Amazon operate.

### Hybrids and combinations

The M competitions' most durable finding is combination. M4's winner was a
hybrid (Smyl's ES-RNN: exponential-smoothing normalization with a shared
dilated LSTM learning what the local model cannot), M4's runner-up was a
meta-learner weighting nine statistical methods by series features
(FFORMA), and M5's organizers reported equal-weight averages of diverse
models beating tuned weighted schemes almost everywhere (Finding 2). The
production translation: run the statistical baseline and the global model
side by side and average them per series when their rolling-origin errors
are within a few points, blend statistical level-and-season with ML on
promo weeks (the residual-on-baseline pattern: forecast the statistical
model's residuals with the GBM and add back), and prefer two diverse
mediocre models to one tuned champion when the evaluation window is short.
Combination is also the cheap insurance against regime change, since
diverse failure modes average out where a single model's failure
concentrates.

## Evaluation before modelling

Set the protocol before touching features, because every later claim rests
on it.

Rolling-origin cross-validation is the only defensible protocol: pick 3+
cutoffs spaced by the forecast cycle, train strictly on data whose target
dates precede each cutoff, forecast the next horizon, refit per cutoff.
Reusing one fit across cutoffs leaks later windows into earlier scores.
assets/global_lgbm.py implements the harness; assets/evaluation.py implements
the metrics.

Metrics, with their sharp edges:

- MASE scales MAE by the in-sample seasonal-naive MAE, so 1.0 means "no
  better than naive" and values compare across series. Use season=1 scaling
  on intermittent data (the M5 convention) and start the denominator at the
  first non-zero observation.
- RMSSE is the squared-error twin; M5 chose it because absolute error is
  minimized by the median, and on zero-heavy series the median is zero, so an
  MAE-family tournament crowns the all-zero forecast. WRMSSE weights RMSSE by
  each series' dollar share over the last 28 training days. Worked numbers:
  in the assets/evaluation.py demo, a lumpy series scores RMSSE 0.75 while
  the same forecast posts sMAPE 181%, and the WRMSSE of 1.083 is pulled by
  the two high-weight series at 1.01 and 1.15, with the lumpy series (weight
  0.4%) irrelevant.
- sMAPE saturates at 200% on every missed demand event and its ranking is
  dominated by near-zero periods; keep it out of intermittent and promo-heavy
  evaluations.
- Pinball loss per quantile plus empirical coverage for intervals. Quantile
  GBMs under-cover out of the box: the assets demo hits 71% at nominal 80%.
  Check coverage before quoting any interval, and widen by conformal
  calibration on held-out residuals when it misses.
- Forecast value added (FVA) versus seasonal naive is the client-facing
  number: FVA = 1 - MASE_model / MASE_snaive. The assets demo posts +67.9%
  for the global GBM on promo-driven synthetic retail. Negative FVA against
  seasonal naive is common in real S&OP stacks and ends the modelling
  conversation until the pipeline is fixed.

Leakage traps specific to global demand models, each observed repeatedly in
client code:

1. Rolling statistics computed including the current row; shift first, then
   roll (assets/global_lgbm.py builds every feature at the forecast origin).
2. Random-fold CV across a panel: rows from one series land in train and
   test at the same timestamps. Folds must be temporal.
3. Per-series normalization fitted on the full series, test period included.
4. "Known-future" covariates that are known only in hindsight: weather
   actuals at inference time, promo flags reconstructed from the sales spike
   they caused, in-stock flags derived from sales.
5. Static features computed from outcomes (lifetime average sales as an
   embedding input).
6. Price as a covariate carries endogeneity: retailers mark down slow
   movers, so the fitted price coefficient mixes elasticity with reverse
   causation. Fine for forecasting under an unchanged pricing policy; wrong
   for what-if simulation, which belongs to causal-inference and
   price-optimization.

## Retail and CPG at SKU-store-week

The reference architecture is one global LightGBM per assortment segment,
direct multi-horizon (origin features plus a horizon-step feature), Tweedie
for the point, pinball models for quantiles, bottom-up aggregation to
planning levels. M5's field validated the shape; the traps below decide
whether it works on client data.

Censored demand. Sales = min(demand, availability); training on raw sales
teaches the model that stockouts mean low demand, orders follow, and service
spirals down. Dingdong measured 7.37% systematic underestimation from raw
sales in fresh grocery (arXiv 2505.16319). Mask out-of-stock periods from the
training loss (the Zalando and AWS pattern), impute from within-period
profiles when partial availability gives a profile share, or fit censored
likelihoods (Tobit ETS, censored negative binomial). Correct for substitution
before crediting a stocked-out SKU with all recovered demand. Worked EM
iteration, profile arithmetic, and the substitution and phantom-inventory
caveats are in references/unconstraining-and-promo.md; phantom-inventory
detection itself belongs to retail-analytics.

Promotions. A promo week mixes true incremental lift, forward-buying that
the next weeks give back, and cannibalization of substitutes. Worked
decomposition in references/unconstraining-and-promo.md: an observed 2.8x
lift of 180 incremental units shrinks to 160 after the post-promo trough and
to 145 after cannibalization, a 19% haircut on the naive read. In the model:
promo indicators split by mechanic and discount depth, promo lags 1 and 2 so
the trough is learned and the baseline stays honest, log(price /
regular_price) with the reference price from a rolling mode, and partial
pooling of uplift by category-mechanic for SKUs with two promos of history.
M5's statistical benchmarks quantify the covariate value: promo/event
regressors improved ES by 6% and ARIMA by 13% (organizer Finding 7).

Calendar. Paydays and benefit schedules move weekly demand by whole
percentage points in grocery; M5's SNAP flags (about 10 flagged days per
month per state) were load-bearing features for top teams. Moving-date
holidays break naive dummies: Easter shifts across March and April, Ramadan
walks 11 days a year through the solar calendar. Use fractional holiday
variables keyed to observed weekday (the PJM fuzzy-holiday construction in
references/industry-notes.md transfers directly) and distance-to-holiday
features on both sides.

New items. Attribute-based analogues: match on category, brand tier, price
band, pack size; take a similarity-weighted average of the analogues'
first-13-week curves; scale by planned distribution points; blend into the
item's own history with weight n/(n+6) at n weeks of actuals. Fashion
variants add image embeddings for similarity (documented in the fact sheet
trail, research/censored-demand-unconstraining.md). Do this deliberately or
the global model does it accidentally through the category feature, with no
control over the analogue set.

What deploys in 2026: global GBMs remain the production default at grocery
and general-merchandise scale; deep multi-horizon quantile models run where
platform teams exist (Amazon's MQ lineage, Zalando's transformer); foundation
models serve as baselines and cold-start engines (see the dedicated section).

## Grocery perishables and foodservice

The deliverable is a quantile, never a point. Waste (overage) and lost sales
plus substitution damage (underage) price the two error directions
asymmetrically, so the order-up-to level is the critical fractile q* =
Cu / (Cu + Co). A sandwich retailing at 4.00, costing 1.50, salvaging 0:
Cu = 2.50 margin lost per missed sale, Co = 1.50 wasted per unsold unit,
q* = 2.50 / 4.00 = 0.625, so stock the 62.5th percentile of daily demand.
The newsvendor derivation and multi-period extensions belong to
supply-chain-optimization; the forecasting job is a calibrated quantile at
exactly that level, which argues for direct pinball-loss training at q* and
empirical coverage checks per store-item, and for daily granularity with
day-of-week and weather interactions. Waste-tracking data doubles as the
censoring flag: a day that sold out by 15:00 is a censored observation and
the within-day profile method applies.

## Building materials and aggregates

Project-driven, lumpy, weather-gated. A few DOT contracts and large pours
dominate plant volume, so the forecast is a blend: the order book converted
through booking-curve realization rates for near horizons, a workable-days
seasonal baseline for far horizons, with the blend weight at lead h equal to
the booking-curve share of final volume visible at h (if 80% of delivered
volume is booked 4 weeks out, the order-book component carries weight 0.8).
Leading indicators (housing permits and starts, DOT lettings, the
Architecture Billings Index at its 9-to-12-month lead) inform annual plans
at regional aggregate level and add nothing at SKU-week. Forecast the top
accounts individually with sales input logged as scored overrides. The full
logic, including the workable-days construction, is in
references/industry-notes.md.

## Lumber

Demand derives from residential construction: single-family starts times
roughly 15,000 board feet of framing per start (NAHB estimates), lagged over
the build schedule, plus the smoother repair-and-remodel channel. The
lumber-specific trap is channel inventory feedback: dealers pre-buy into
rising prices and destock into falling ones, so mill shipments overstate
end-use demand in rallies and understate it in slides, and the gap
mean-reverts. Forecast end-use and channel motion as separate components;
the price path itself belongs to price-forecasting.
References/industry-notes.md carries the detail.

## Utility load

Short-term load is a solved feature-engineering problem with published
operational specifications; copy them before inventing. The EDF GAM terms
(day-type interactions, load lags at one day and one week, cyclic
time-of-year, a time-of-day by temperature tensor, exponentially smoothed
temperatures at 0.95 and 0.99 for thermal inertia) and PJM's weather
constructions (wind-adjusted winter temperature, a humidity index kicking in
at 58 F, four-section temperature splines, fuzzy holiday fractions) are laid
out with formulas in references/industry-notes.md. Durable GEFCom lesson:
probabilistic load comes from a conditional model crossed with a weather
ensemble; the quantile-GAM-plus-temperature-scenarios method won both
GEFCom2014 tracks (Gaillard, Goude, Nedellec, IJF 2016) and the shape still
runs in 2026 with NWP ensembles.

<!-- allow:CAN behind-the-meter names the metering device; spelling is correct -->
Three current complications. Behind-the-meter solar makes net load look like
decay; either reconstruct gross load from irradiance and capacity registries
or forecast net directly with irradiance covariates (a 2026 feeder-level
study finds direct more accurate but biased high; references and trade-offs
in industry-notes.md). EV and data-centre growth enters as scenario adders,
and ERCOT's 2025 practice (haircut new data-centre requests to 49.8%, delay
in-service dates 180 days) is the worked example of disciplining
interconnection-request inflation, after its 2030 data-centre estimate
jumped from 29.6 GW to 78.0 GW in one forecast vintage. And inference-time
weather is a forecast, never an actual: backtest on archived NWP forecasts
or report the actuals-based backtest as an upper bound; CAISO's day-ahead
miss of 3,211 MW at the July 2024 heat-wave peak shows the size of the gap
this hides.

Hierarchical feeder and substation forecasts reconcile the same way retail
hierarchies do (next section); the published pattern is per-substation GAMs
with MinT-shrink reconciliation on AMI data.

## Spare parts and intermittent demand

Classify first with the Syntetos-Boylan-Croston cutoffs (average demand
interval 1.32, size CV squared 0.49), then forecast a rate and a
distribution. Croston smooths sizes and intervals separately; its ratio
estimator is biased high by Jensen's inequality, and SBA's (1 - alpha/2)
deflator removes most of the bias. Simulation with true rate 1.500 and
alpha 0.2: long-run Croston mean 1.631 (+8.8%), SBA 1.468 (-2.1%), TSB 1.506
(+0.4%). TSB updates the demand probability every period, so it alone decays
after obsolescence; use it whenever the portfolio has phase-outs. Formulas,
the worked recursion, and ADIDA temporal aggregation are in
references/intermittent-demand.md.

Evaluation ties to achieved service, never to per-period point error: the
zero forecast wins MAE whenever demand probability is below one half. In the
assets/stats_baselines.py demo the zero forecast posts the best MAE (1.56 vs
2.52-2.63) while achieving 63.6% service against a 95% target; SBA with a
negative-binomial lead-time distribution sized from the training variance
achieves 95.9%, and Poisson sizing from the rate alone under-buys at 84%
because lumpy demand is overdispersed. Deliver the rate, the distribution,
and the achieved-service simulation together; the stocking decision math is
supply-chain-optimization's.

## Hierarchical reconciliation

Independent forecasts at each level disagree with their own sums;
reconciliation projects them onto the coherent subspace with
G = (S' W^-1 S)^-1 S' W^-1. Worked numbers (verified in
references/reconciliation.md): base forecasts [Total 105, A 40, B 70] with
residual variances (3, 1, 2) reconcile to [107.5, 39.17, 68.33]; the 5-unit
incoherence is allocated in proportion to error variance, so the most
trusted forecast moves least. MinT with Schafer-Strimmer shrinkage
(mint_shrink) is the default serious choice and needs in-sample residuals
(pass fitted values, or hierarchicalforecast raises its best-known error).
Bottom-up wins when the bottom level carries covariates the aggregates
cannot see, so M5 winners forecast product-store directly and
summed; MinT wins when sparse bottom series need correction from cleaner
aggregates. Run BottomUp, MinTrace(ols), MinTrace(mint_shrink) side by side
per level (assets/mint_reconciliation.py prints the table; in its demo
mint_shrink improves region-level RMSSE from 1.012 to 0.997 while bottom-up
degrades the total from 0.740 to 0.819). For coherent intervals use
Bootstrap or PERMBU reconciliation; Gaussian assumptions understate
zero-heavy retail tails.

## Structural breaks

Three usable treatments for a COVID-shaped break, in order of preference
when the process resumed its old physics: indicator variables spanning the
break (global models absorb these naturally), downweighting or truncating
the break window, and adaptive coefficients (EDF kept its GAM through the
2020 lockdown by putting a Kalman filter on the coefficients, the published
production example, arXiv 2009.06527). Truncate history entirely only when
the break is permanent (assortment reset, channel shift), because global
models pay for lost history across every series.

Changepoint discipline: automated changepoint detection generates
candidates, never verdicts. A changepoint enters the model only with a named
mechanism and a client-confirmed date; otherwise promo effects, weather
runs, and stockouts get eaten as trend breaks, which is the classic failure
of Prophet-style default changepoints on demand data.

## Foundation models as of mid-2026

Zero-shot pretrained forecasters (Chronos-2, Chronos-Bolt, TimesFM 2.5,
Moirai-2, TiRex, TimeGPT) are now the mandatory day-one baseline: one
function call, no features, competent probabilistic output. On GIFT-Eval
(97 configurations, 55 datasets) Chronos-2 leads win rate and skill under
both weighted quantile loss and MASE, ahead of TiRex and TimesFM-2.5, and it
accepts covariates zero-shot (arXiv 2510.15821). They win outright on cold
start, short history, and the uneconomic long tail; they lose on
covariate-rich SKU-store retail, where tuned global GBMs with promo and
price features still hold the frontier, and on intermittent tails, where
calibration audits find their weakest coverage (arXiv 2510.16060). Treat
AWS's 250x Chronos-Bolt speedup and 90% Chronos-2 win-rate figures as vendor
benchmarks. Full roster, benchmark numbers, and the deployment playbook are
in references/foundation-models.md. The operational rule: if the engineered
model cannot beat zero-shot Chronos-2 on rolling-origin FVA, fix the
pipeline before adding capacity.

## Judgmental overrides in client organizations

Client planners will override the model; govern the overrides as data.
The empirical base: Fildes, Goodwin, Lawrence and Nikolopoulos (IJF 2009)
found about 75% of statistical forecasts manually adjusted across four
supply-chain companies, with large adjustments (which carry real
information, like a known tender) tending to improve accuracy and small
cosmetic ones tending to add noise, and optimistic adjustments performing
worse than pessimistic ones. Operating rules that follow: every override is
logged with owner, size, and stated reason; overrides are scored quarterly
as their own FVA line against the untouched statistical forecast, per
planner and per reason code; small-adjustment classes that lose get
abolished by policy, which typically removes most override volume while
keeping the tender-sized information. The scoring infrastructure and
retraining governance belong to model-operations; the forecasting engagement
delivers the baseline, the override log schema, and the first scorecard.

## Library quick reference

Versions checked on PyPI 2026-07-12 (`research/nixtla-ecosystem.md` has the
full audit):

| library | version | role | sharpest gotcha |
|---|---|---|---|
| statsforecast | 2.0.3 | statistical baselines, Croston family, MSTL | 2.x changed AutoARIMA defaults (allowmean/allowdrift now True), so 1.x results do not reproduce; AutoETS caps seasonal period near 24, route weekly m=52 through MSTL |
| mlforecast | 1.1.0 | global GBM feature pipelines, conformal intervals | 1.0 removed window_ops/numba lag transforms; pre-1.0 code breaks; direct multi-step via max_horizon |
| hierarchicalforecast | 1.5.1 | reconciliation | 1.0 renamed the summing-matrix argument to S_df and dropped indexed DataFrames; mint_shrink demands in-sample fitted values via Y_df |
| neuralforecast | 3.2.0 | deep global models, 30+ architectures | v3.2.0 replaced cpus/gpus params with ray_options; numpy losses deprecated in 3.1.6 |
| AutoGluon-TimeSeries | 1.5.0 | AutoML plus Chronos-2 integration | strongest one-command stack; its benchmark claims are self-published |
| Darts | 0.45.0 | broad alternative API | active; overlaps Nixtla stack, pick one per engagement |
| Prophet | 1.3.0 | interpretable baseline only | compatibility-only maintenance; routinely loses to seasonal naive and SARIMA in published comparisons; default changepoints misread promo-driven series |

Cross-cutting: the pandas 2.2 offset-alias change (ME, QE, h) breaks old
freq="M" code across the whole stack, and the Nixtla long format
(unique_id, ds, y) with explicit freq is assumed by every asset in this
skill.

## Assets

- assets/evaluation.py: MASE, RMSSE, WRMSSE, pinball, coverage, FVA, with
  the sMAPE failure demo. Pure numpy/pandas.
- assets/global_lgbm.py: leak-safe origin-based global LightGBM with
  quantile objectives and rolling-origin CV on synthetic promo retail.
- assets/stats_baselines.py: statsforecast baselines plus the
  intermittent-demand service-level evaluation with Poisson vs negative
  binomial stock sizing.
- assets/mint_reconciliation.py: BottomUp vs MinT on a store-region
  hierarchy with per-level RMSSE and coherence checks.

Each file lists its pip dependencies in the header comment and runs
standalone with a __main__ demo; all four compile and run on Python 3.13
with statsforecast 2.0.3, hierarchicalforecast 1.5.1, lightgbm 4.6.0.

## References

- references/intermittent-demand.md: Croston/SBA/TSB derivations, bias
  simulation, service-level evaluation doctrine.
- references/reconciliation.md: MinT derivation, worked projection, shrink
  estimator, probabilistic reconciliation, bottom-up conditions.
- references/unconstraining-and-promo.md: censoring treatments with worked
  EM, promo decomposition arithmetic, substitution corrections.
- references/industry-notes.md: utility formulas (EDF GAM, PJM weather,
  GEFCom recipe, net load, data-centre scenarios), building materials
  order-book blend, lumber channel dynamics.
- references/foundation-models.md: 2026 roster, GIFT-Eval standing, win/lose
  domains, deployment playbook.
- references/sources.md: every URL with access date.
- references/research/: the four researcher fact sheets with
  per-claim verification flags.
