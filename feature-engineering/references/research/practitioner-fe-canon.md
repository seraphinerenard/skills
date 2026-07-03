<!-- Compiled 2026-07-12. -->

---

# Practitioner feature-engineering canon: time-series & panel ML (2018–2026)

## 1. M5 Accuracy & M5 Uncertainty

**M5 Accuracy winner (YeonJun In, 1st).** Equal-weight mean of many LightGBM models, pooled at three grains: per-store (10 models), store-category (30), store-department (70); two variants each (recursive and non-recursive/direct), 220 models total, each series = mean of 6 models. Objective = **Tweedie** (maximize Tweedie negative-log-likelihood, `tweedie_variance_power` in (1,2)), which suits non-negative sales with a probability mass at zero. No early stopping. [M5-methods repo; IJF M5-accuracy paper; Nicault writeup]

**Canonical public-notebook feature set (Yakovlev lineage, used across top solutions).** All lag/rolling features **shifted ≥28 days** to match the 28-day horizon and avoid leakage. [keshusharmamrt repo; Artefact; M5-methods]
- **Lags:** sales lagged 28,29,…,42 (shift-28 base).
- **Rolling stats on shift-28 target:** rolling mean and std over windows **7, 14, 30, 60, 180**; also exponentially-weighted mean.
- **Price features:** relative diff of current price vs its historical mean (flags promos), `price_max/min/std/mean`, `price_norm` (price ÷ max), `price_momentum` (price ÷ prior-week price), momentum vs month and vs year, cross-store and within-category price comparisons.
- **Calendar/event:** `event_name/type` (with a −15…0…+15-day event window), **SNAP** flags (CA/TX/WI), weekday, week-of-month, month, year, day, weekend flag.

**The "magic multiplier" pitfall.** Sales rose every May→June for 5 prior years, so many teams multiplied forecasts by a trend factor tuned on the public 28-day window; it lifted the public LB but the trend did not repeat in the private window, causing a large shake-up. The 2nd and 5th solutions also used multipliers, but **derived from higher-aggregation-level forecasts** (2nd place Anderer: LightGBM per store × N-BEATS-based factors ~0.9/0.93/0.95/0.97/0.99), a principled adjustment vs blind LB-tuning. Lesson: bias adjustments must be validated out-of-sample, not fit to one public window. [Nicault; IJF M5-accuracy; Anderer repo]

**M5 Uncertainty winner (Lainder & Wolfinger, IJF 2022).** Single LightGBM family producing the **9 required quantiles** via quantile ("pinball") loss, plus heavy **data augmentation**, careful **hyperparameter tuning**, and **time-series cross-validation**; same recipe won the Kaggle COVID-19 series. Emphasis on guarding GBMs against leakage/overfitting under non-stationary, collinear targets. [IJF S0169207021002090; ScienceDirect S0925527324003062]

## 2. Target encoding

**Micci-Barreca (2001) sigmoid smoothing** — blend category mean toward global mean by group size:
`S_i = λ(n_i)·(n_iY/n_i) + (1−λ(n_i))·(n_Y/n_TR)`, with `λ(n) = 1/(1+exp(−(n−k)/f))`.
`n_iY/n_i` = category target mean (posterior), `n_Y/n_TR` = global mean (prior), `k` = inflection point (count where λ=0.5; category_encoders `min_samples_leaf`, H2O `inflection_point` default 10), `f` = smoothing steepness (H2O `smoothing` default 20; smaller f = sharper). [KDD 2001; category_encoders docs; H2O docs]

**m-estimate / additive-smoothing form** (sklearn `TargetEncoder`): `enc_c = (n_c·ȳ_c + m·ȳ)/(n_c + m)`; `m=smooth`, `"auto"` sets m via empirical-Bayes using category variance. [sklearn docs]

**CatBoost ordered target statistics (Prokhorenkova et al., NeurIPS 2018).** Fix a random permutation σ; encode each row using **only earlier rows** in σ:
`x̂_k = (Σ_{j<σ(k), x_j=x_k} y_j + a·p) / (Σ_{j<σ(k), x_j=x_k} 1 + a)` — prior `p` (e.g. global mean), prior weight `a>0` (feaz-book: `(currentCount+prior)/(totalCount+1)`, prior≈0.05). This kills the **prediction shift / target leakage** that plain (full-data) target stats and ordinary GBM both suffer. [NeurIPS 2018; feaz-book; apxml]

**Out-of-fold discipline & failures.** Encode inside each CV fold (sklearn `fit_transform` cross-fits over `cv=5`; `fit().transform()` on the same data leaks). Failure modes: rare categories overfit without smoothing; leakage if the encoding sees the row's own target; **temporal leakage** in panels (encoding on future rows) — respect time order; heavy-tailed regression targets need robust priors; often adds little over LightGBM's native categorical handling. [sklearn docs; H2O docs]

## 3. Null-importance selection & adversarial validation

**Null importances (Grellier, Kaggle 2018).** Shuffle the target **~80 times** to build a null importance distribution per feature (both **gain** and **split** importance, LightGBM RF mode). Feature score `= log(1e-10 + actual_imp / (1 + P75(null_imps)))`; also `corr_score = 100·mean(null_imps < P25(actual))`. Keep features whose real importance sits far in the right tail of their null; thresholds swept 0–99. [Kaggle notebook; databreak reproduction]

**Altmann PIMP (Bioinformatics 2010).** Permute the outcome s times (≈50–100), refit, collect null importances per feature, fit a distribution (Gaussian/lognormal/gamma) or use empirical, and report a **p-value** = P(null ≥ observed). Non-informative features get non-significant p; corrects RF/MI importance bias. [Oxford Bioinformatics 26(10):1340; PIMP R code]

**Adversarial validation.** Label train=0 / test=1, train a classifier, read **ROC-AUC**: ≈0.5 ⇒ same distribution (trust your CV); →1.0 ⇒ covariate shift. Practice: inspect the classifier's top features to find the shifting columns and drop/down-weight them; **reweight** training rows by predicted test-membership probability; or build a validation set from the train rows most "test-like." Popularized on Kaggle (Santander, FastML). [FastML; UnfoldAI; Medium/Ozturk]

## 4. Modern panel tooling (2024–2026)

- **Nixtla `mlforecast`** — `lag_transforms={lag: [transform,…]}`, e.g. `{1:[RollingMean(window_size=7)], 7:[ExpandingMean()]}`. Transforms: `RollingMean/Std/Min/Max/Quantile(window_size,min_samples)`, `SeasonalRollingMean(season_length,window_size)`, `ExpandingMean/Std`, `ExponentiallyWeightedMean(alpha)`; numba-compiled and updated incrementally during recursive prediction; **pandas and Polars** backends. Rolling transforms apply to *lags*, not raw y. Practitioner default for scalable per-series GBM forecasting. [nixtlaverse mlforecast/lag_transforms; GitHub]
- **tsfresh** — 63 characterization methods → ~**794** features by default, with built-in hypothesis-test filtering; good for classification/relevance mining, heavier for large panels. [tsfresh GitHub/README]
- **sktime / aeon** — unified TSML API (forecasting, classification, transforms) with wrappers to statsmodels/tsfresh; aeon is the maintained fork used for benchmarking. [aeon arXiv 2406.14231]
- **Polars pipelines** — favoured for lag/rolling group-by feature builds at panel scale (speed, lazy eval); mlforecast integrates it directly. [Nixtla blog]

## 5. Fourier / harmonic seasonality (Hyndman FPP3)

- Dynamic harmonic regression: `y_t = a + Σ_{k=1}^{K}[α_k sin(2πkt/m) + β_k cos(2πkt/m)] + η_t`, with `η_t` an ARIMA error to absorb short-run dynamics. [otexts fpp3 §10.5]
- **Choose K by minimizing AICc**; hard cap **K ≤ m/2**. Larger K = wigglier seasonal shape. FPP3 monthly eating-out example: **K=6** minimizes AICc (K=6 for m=12 ≡ full seasonal dummies). [otexts fpp3 dhr; Hyndman ACEMS 2018 PDF]
- Multiple seasonalities: one Fourier block per period. Daily data typical (AICc-tuned, not fixed): weekly `m=7` → K≈2–3 (max 3); yearly `m≈365` → small K (≈5–12). Advantage: handles long/non-integer periods that seasonal ARIMA cannot. [otexts fpp3]

## 6. Recent competitions (2023–2026): features & leakage traps

- **Optiver "Trading at the Close" (2023).** Feature engineering was the alpha. Key: order-book **imbalance** features (imbalance size/flag, `far`/`near` price, WAP), cross-sectional stock aggregations (median/std of size, price) capturing market-wide moves, **lagged features** via shift/diff/pct_change grouped by `stock_id` over windows (1,2,3,10), and feeding back the **revealed target** from the prior day. Leakage trap: ordinary k-fold leaks via autocorrelation → winners used **time-based split / Purged K-Fold** to kill look-ahead. Models: single robust LightGBM, or LightGBM+MLP ensemble. [Optiver 1st-place writeup; ESANN 2024; nimashahbazi/liyiyan repos]
- **Enefit "Predict Energy Behavior of Prosumers" (2023–24).** Segment keys: county, business/consumer flag, product/contract type; **installed PV capacity**; **historical + forecast weather** (temperature, dewpoint, cloud cover, solar radiation); electricity and gas prices; calendar (hour, day-of-week, holidays); **target lags** (prior-day and prior-week production/consumption). Leakage watch-points: forecast vs historical weather must be aligned to prediction time, and installed-capacity/target lags fed via the time-series API without peeking ahead. [Kaggle Enefit competition; bonskotti/Musone repos; Smart Energy Intl]
- **Rossmann (2015, canonical retrospective).** 1st place = XGBoost with heavy time+exogenous feature construction plus a **ridge trend adjustment**; 3rd place (Guo & Berkhahn) introduced **entity embeddings** of categoricals (arXiv 1604.06737) — the first strong NN result on Kaggle forecasting and now standard for high-cardinality panel keys. [Kaggle 3rd-place interview; arXiv 1604.06737; Bojer & Meldgaard]
- **Corporación Favorita (2018).** Top solutions = blends of LightGBM over rich lag + rolling-window statistics on shifted sales, promotion flags, and calendar features; direct multi-step (one model per horizon) plus NN ensembles. General M-lesson echoed here: GBDT on engineered lag/rolling/price/promo features is the retail-panel workhorse. [Favorita competition; btrotta/antklen repos; Bojer & Meldgaard]

---

SOURCES (accessed 2026-07-12)
- M5 Accuracy results, IJF — https://www.sciencedirect.com/science/article/pii/S0169207021001874 — winner pooling grains, Tweedie, and multiplier findings.
- M5-methods repo (organizers) — https://github.com/Mcompetitions/M5-methods — official winning code/benchmarks.
- Anderer 2nd-place M5 — https://github.com/matthiasanderer/m5-accuracy-competition — LightGBM×N-BEATS multipliers (0.9–0.99).
- Nicault M5 writeup — https://www.christophenicault.com/post/m5_forecasting_accuracy/ — clearest account of the multiplier/June-trend shake-up.
- Artefact M5 lessons — https://medium.com/artefact-engineering-and-data-science/sales-forecasting-in-retail-what-we-learned-from-the-m5-competition-445c5911e2f6 — price/event-window features and Tweedie(1–2).
- keshusharmamrt M5 repo — https://github.com/keshusharmamrt/M5-Walmart-Sales-Forecasting — shift≥28 lag/rolling/EWMA + SNAP/date features.
- M5 Uncertainty winner (Lainder & Wolfinger) — https://www.sciencedirect.com/science/article/abs/pii/S0169207021002090 — quantile LightGBM, augmentation, TS-CV.
- Micci-Barreca 2001 (KDD Explorations) — https://dl.acm.org/doi/10.1145/507533.507538 — origin of target/impact encoding with sigmoid smoothing.
- category_encoders TargetEncoder — https://contrib.scikit-learn.org/category_encoders/targetencoder.html — min_samples_leaf/smoothing S-curve blend.
- sklearn TargetEncoder — https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.TargetEncoder.html — m-estimate formula + cross-fitting to stop leakage.
- H2O Target Encoding — https://docs.h2o.ai/h2o/latest-stable/h2o-docs/data-science/target-encoding.html — inflection_point=10, smoothing=20, KFold/LOO holdout + noise.
- Prokhorenkova et al. 2018 (CatBoost, NeurIPS) — https://proceedings.neurips.cc/paper/2018/hash/14491b756b3a51daac41c24863285549-Abstract.html — ordered TS/boosting vs prediction shift.
- feaz-book CatBoost encoding — https://feaz-book.com/categorical-catboost — ordered-TS formula (currentCount+prior)/(totalCount+1).
- Grellier null-importances notebook — https://www.kaggle.com/code/ogrellier/feature-selection-with-null-importances — 80-shuffle null distribution + scoring formula.
- databreak reproduction — https://databreak.netlify.app/2019-04-21-null_importance/ — exact score/corr-score formulas.
- Altmann et al. 2010 (PIMP) — https://academic.oup.com/bioinformatics/article/26/10/1340/193348 — permutation p-values for importance.
- FastML adversarial validation — https://fastml.com/adversarial-validation-part-one/ — origin + AUC≈0.5 interpretation.
- UnfoldAI adversarial validation — https://unfoldai.com/adversarial-validation/ — practice thresholds and reweighting.
- mlforecast lag_transforms — https://nixtlaverse.nixtla.io/mlforecast/lag_transforms.html — Rolling/Expanding/Seasonal/EWM API + Polars.
- tsfresh — https://github.com/blue-yonder/tsfresh — ~794 auto features + relevance filtering.
- aeon toolkit — https://arxiv.org/html/2406.14231v1 — maintained sktime-fork TSML API.
- FPP3 §10.5 Dynamic harmonic regression — https://otexts.com/fpp3/dhr.html — K by AICc, K≤m/2, eating-out K=6.
- Hyndman ACEMS 2018 dynamic regression — https://robjhyndman.com/acemsforecasting2018/3-Dynamic-Regression.pdf — Fourier term selection guidance.
- Optiver 1st-place writeup — https://www.kaggle.com/competitions/optiver-trading-at-the-close/writeups/hyd-1st-place-solution — imbalance features, revealed target, purged CV.
- ESANN 2024 Optiver paper — https://www.esann.org/sites/default/files/proceedings/2024/ES2024-159.pdf — feature families and validation.
- Enefit competition — https://www.kaggle.com/competitions/predict-energy-behavior-of-prosumers — data/features + time-series API leakage constraints.
- bonskotti Enefit repo — https://github.com/bonskotti/predict-energy-behavior — weather/price/capacity/segment features.
- Rossmann 3rd-place interview — https://medium.com/kaggle-blog/rossmann-store-sales-winners-interview-3rd-place-neokami-inc-ed67c7a2c3ca — entity embeddings context.
- Guo & Berkhahn entity embeddings — https://arxiv.org/pdf/1604.06737 — categorical embeddings for panels.
- Bojer & Meldgaard, Kaggle forecasting retrospective — https://arxiv.org/pdf/2009.07701 — cross-competition feature/validation lessons (PDF; abstract-level access).

Note on limits: Kaggle discussion pages and several IJF/arXiv PDFs render as JS shells or binary under automated retrieval, so a few exact per-solution numbers (precise M5 window list, Enefit lag specifics) are grounded in reproductions and the peer-reviewed summaries rather than the original private writeups. Those cases are flagged inline.
