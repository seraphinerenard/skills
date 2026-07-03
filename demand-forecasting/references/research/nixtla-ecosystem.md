<!-- Compiled 2026-07-12. -->

---

# Nixtla forecasting ecosystem and adjacents — state as of 2026-07-12

All PyPI/GitHub pages accessed 2026-07-12. Where a small-model fetch returned an implausible year for a GitHub release page, the value is cross-checked against PyPI upload dates and the GitHub REST API (JSON), which are authoritative; those are the dates reported below.

## 1. Current PyPI versions and Python support (Nixtla core stack)

| Package | Latest version | Release date | Requires-Python | Classifier Python versions | Source |
|---|---|---|---|---|---|
| statsforecast | 2.0.3 | 2025-10-29 | >=3.9 | 3.9–3.13 | https://pypi.org/project/statsforecast/ |
| mlforecast | 1.1.0 | 2026-07-10 | >=3.10 | 3.10–3.14 | https://pypi.org/project/mlforecast/ |
| neuralforecast | 3.2.0 | 2026-07-10 | >=3.10 | 3.10–3.13 | https://pypi.org/project/neuralforecast/ |
| hierarchicalforecast | 1.5.1 | 2026-03-04 | >=3.10,<4.0 | 3.10–3.14 | https://pypi.org/project/hierarchicalforecast/ |
| utilsforecast | 0.2.16 | 2026-04-27 | >=3.10 | 3.9–3.13 (see flag) | https://pypi.org/project/utilsforecast/ |
| coreforecast | 0.0.18 | not captured (flag) | >=3.10 | 3.10–3.14 | https://pypi.org/pypi/coreforecast/json |
| datasetsforecast | 1.0.1 | 2026-02-24 | >=3.10 | 3.10–3.14 | https://pypi.org/pypi/datasetsforecast/json |

Flags:
- statsforecast is the laggard on Python-floor: it still declares >=3.9 while every other core package moved to >=3.10. Its latest (2.0.3, Oct 2025) is also the only core package that has not had a 2026 release, so it is the least actively iterated of the seven.
- utilsforecast shows a metadata inconsistency: Requires-Python is >=3.10 but the classifier list still includes Python 3.9. Treat 3.10 as the real floor.
- coreforecast 0.0.18 upload date was absent from the truncated JSON (0.0.14 shows 2024-11-05). Version and Python support are confirmed; the exact 0.0.18 date is unverified.

## 2. statsforecast API and gotchas

Sources: https://raw.githubusercontent.com/Nixtla/statsforecast/main/README.md ; https://nixtlaverse.nixtla.io/statsforecast/src/core/core.html (both accessed 2026-07-12).

- Class: `StatsForecast(models=[...], freq=..., n_jobs=-1, fallback_model=None)`. Methods `fit`/`predict`, plus the memory-lean `forecast(df, h, level=, prediction_intervals=, X_df=, fitted=)` and `cross_validation(df, h, n_windows, step_size, test_size, refit)`.
- Models confirmed present in the current roster: AutoARIMA, AutoETS, AutoCES, AutoTheta, AutoMFLES, AutoTBATS (auto family); ARIMA; Theta, OptimizedTheta, DynamicTheta, DynamicOptimizedTheta; MSTL, MFLES, TBATS (multiple seasonality); GARCH, ARCH; intermittent-demand ADIDA, CrostonClassic, CrostonOptimized, CrostonSBA, IMAPA, TSB; baselines HistoricAverage, Naive, RandomWalkWithDrift, SeasonalNaive, WindowAverage, SeasonalWindowAverage; and the exponential-smoothing family (SES, SeasonalES, Holt, HoltWinters). Every model named in the research brief (AutoETS, AutoARIMA, MSTL, AutoTheta, CrostonClassic, CrostonSBA, TSB, ADIDA, IMAPA, SeasonalNaive) is present.
- DataFrame contract: long format with `unique_id`, `ds`, `y`. Column names are overridable via `id_col`/`time_col`/`target_col`. As of the 2.x line the DataFrame is passed to `fit`/`forecast` (not the constructor).
- Prediction intervals: two paths. Parametric/model-based via `level=[80, 95]`. Distribution-free conformal via `prediction_intervals=ConformalIntervals(h=12, n_windows=2)` passed to `fit`/`forecast`, combined with `level`.
- Gotchas confirmed from docs:
  - Frequency: `freq` takes a pandas offset alias (e.g. `'D'`, `'ME'`, `'QE'`, `'h'`) for datetime `ds`. For an integer index you must set `freq=1` (integer step); mixing an integer `ds` with a string freq, or vice versa, is the classic failure. The library infers spacing from `freq`, not from the data.
  - `n_jobs=-1` uses all cores (process-based parallelism across series). For a large number of very short series the per-process overhead can make `n_jobs=1` faster; the parallel win is on many longer series.
  - `fallback_model=` lets you pass a model (for example `Naive()`) that is substituted whenever a primary model errors on a given series, so one bad series does not abort the batch.
  - Note the pandas offset-alias modernization: `'M'`/`'H'` style aliases were deprecated by pandas 2.2, so current examples use `'ME'` and `'h'`. Old `freq='M'` code raises pandas FutureWarnings/errors on new pandas.

## 3. mlforecast API and gotchas

Sources: https://raw.githubusercontent.com/Nixtla/mlforecast/main/README.md ; https://nixtlaverse.nixtla.io/mlforecast/forecast.html ; https://nixtlaverse.nixtla.io/mlforecast/target_transforms.html ; https://nixtlaverse.nixtla.io/mlforecast/lgb_cv.html (accessed 2026-07-12).

- Class: `MLForecast(models=, freq=, lags=[7,14], lag_transforms={1:[ExpandingMean()], 7:[RollingMean(window_size=28)]}, date_features=['dayofweek'], target_transforms=[Differences([1])], num_threads=)`. Feature engineering is keyed by lag: `lag_transforms` maps a lag to a list of transform objects (RollingMean, ExpandingMean, etc., now backed by coreforecast rather than the removed window_ops/numba).
- Recursive vs direct: recursive is the default (one model, fed its own predictions). Direct multi-step is opt-in via `fit(..., max_horizon=h)`, which trains one model per horizon step. `fit` also exposes `fitted=` (store in-sample predictions, retrievable with `forecast_fitted_values()`), `static_features=`, `dropna=`, `keep_last_n=`.
- target_transforms roster (current): `Differences`, `AutoDifferences`, `AutoSeasonalDifferences`, `AutoSeasonalityAndDifferences`, `LocalStandardScaler`, `LocalMinMaxScaler`, `LocalRobustScaler`, `LocalBoxCox`, `GlobalSklearnTransformer`. Transforms are auto-inverted at predict time so forecasts return on the original scale.
- Conformal intervals: `fit(..., prediction_intervals=PredictionIntervals(n_windows=, h=))`, then `predict(h, level=[80,95])`. v1.1.0 (2026-07-10) added transfer learning with conformal prediction.
- LightGBMCV still exists: `LightGBMCV(freq=, lags=, lag_transforms=, date_features=)` with `fit(train, n_windows=, h=, params=, static_features=, eval_every=10, early_stopping_evals=, early_stopping_pct=)`; also `setup()`/`partial_fit()` for hyperparameter loops. It trains boosters across CV windows simultaneously with early stopping.
- Gotchas: the biggest historical trap is the v1.0.0 dependency swap (see section 7) — `window_ops`/`numba` transforms were removed in favour of coreforecast classes, so pre-1.0 `lag_transforms` code using `window_ops` functions breaks. Also `dropna` behaviour around null targets changed in v0.15.0.

## 4. hierarchicalforecast API, reconcilers, and the residuals gotcha

Sources: https://raw.githubusercontent.com/Nixtla/hierarchicalforecast/main/README.md ; https://nixtlaverse.nixtla.io/hierarchicalforecast/index.html ; https://raw.githubusercontent.com/Nixtla/hierarchicalforecast/main/hierarchicalforecast/methods.py (accessed 2026-07-12).

- `aggregate(df, spec)` and the loaders return the triple `(Y_df, S_df, tags)`: the aggregated long series, the summing/structure matrix S as a DataFrame, and the `tags` dict of level -> unique_ids.
- Reconciliation via `HierarchicalReconciliation(reconcilers=[...])` then `.reconcile(Y_hat_df=, Y_df=, S_df=, tags=)`. Current signature confirmed from the docs quick-start: S is passed as a DataFrame `S_df` (not a bare numpy array), and `tags` is passed as a keyword.
- Deterministic reconcilers: `BottomUp`, `TopDown(method='forecast_proportions'|'average_proportions'|'proportion_averages')`, `MiddleOut(middle_level=, top_down_method=)`, `MinTrace(method=...)`, `ERM(method=..., lambda_reg=)`. New in the 1.4/1.5 line: `EMinT`/`emint` (an empirical MinTrace variant) and sparse-matrix support.
- MinTrace methods (from source): `ols`, `wls_struct`, `wls_var`, `mint_cov`, `mint_shrink`, plus `emint`.
- The key gotcha, confirmed in `methods.py`: `wls_var`, `mint_cov`, `mint_shrink`, `emint`, and `ERM` all require in-sample residuals. The code raises `"Check \`Y_df\`. For method \`{method}\` you need to pass insample predictions and insample values."` In practice you must generate base-model fitted values (for example `StatsForecast.forecast(..., fitted=True)` then merge the in-sample predictions) and pass the training data through `Y_df` so residuals can be computed. `ols`, `wls_struct`, `BottomUp`, and `TopDown` do not need residuals. This is the single most common hierarchicalforecast error.
- Probabilistic reconciliation classes: `Normality` (Gaussian, uses the MinTrace covariance), `Bootstrap` (Gamakumara sample-path bootstrap), `PERMBU` (rank-permutation copula reinjecting cross-series dependence before bottom-up), and `ConformalReconciliation` (distribution-free, added v1.5.0). Probabilistic methods for MiddleOut were enabled in v1.3.0.
- S matrix format: the summing matrix maps bottom-level series to all aggregate nodes, shape (n_all_series x n_bottom_series), delivered as a DataFrame whose rows are unique_ids; `S_df.reset_index(names="unique_id")` is a common prep step shown in the docs.

## 5. neuralforecast roster, losses, and maintenance

Sources: https://raw.githubusercontent.com/Nixtla/neuralforecast/main/README.md ; https://api.github.com/repos/Nixtla/neuralforecast/contents/neuralforecast/models ; https://nixtlaverse.nixtla.io/neuralforecast/docs/capabilities/objectives.html ; GitHub releases JSON (accessed 2026-07-12).

- The library advertises "more than 30 state-of-the-art models." Confirmed by enumerating the models directory. Present modules include: nbeats, nbeatsx, nhits, mlp, mlpmultivariate, lstm, gru, rnn, dilated_rnn, tcn, bitcn, deepar, deepnpts, tft, patchtst, itransformer, informer, autoformer, fedformer, vanillatransformer, timesnet, timexer, timemixer, softs, softssharp, stemgnn, tide, tsmixer, tsmixerx, dlinear, nlinear, xlinear, timellm, kan, rmok, xlstm, hint. So yes — KAN, iTransformer, PatchTST, TFT, DeepAR, TimesNet, NBEATS, NHITS are all present, plus newer additions RMoK, TimeXer, SOFTS/SOFTSSharp, TimeMixer, xLSTM, XLinear.
- Loss functions confirmed: point losses MAE, MSE, RMSE, MAPE, sMAPE, MASE, relMSE, HuberLoss, TukeyLoss, HuberMQLoss; probabilistic non-parametric QuantileLoss, MQLoss, HuberQLoss, HuberMQLoss, IQLoss, HuberIQLoss, ISQF; parametric DistributionLoss supporting Normal, StudentT, Poisson, NegativeBinomial, Tweedie, plus PMM/GMM/NBMM mixtures.
- Maintenance status: actively developed, the most active package in the stack. Ten releases from v3.1.1 (2025-09-23) through v3.2.0 (2026-07-10). Recent additions: TimeXer (v3.1.3), XLinear (v3.1.5), SOFTSSharp (v3.1.9), categorical exogenous support for univariate models and a FreDF loss (time-domain MSE + frequency-domain MAE) in v3.2.0. v3.1.6 deprecated the numpy-based loss functions; v3.2.0 removed `cpus`/`gpus` params in favour of `ray_options`.

## 6. Competing and adjacent libraries, 2025–2026

| Library | Latest | Release date | Requires-Python | Source |
|---|---|---|---|---|
| Darts (unit8co) | 0.45.0 | 2026-06-19 | >=3.10 | https://pypi.org/project/darts/ |
| GluonTS (awslabs) | 0.16.3 | 2026-06-29 | >=3.7 declared | https://pypi.org/project/gluonts/ |
| sktime | 1.0.1 | 2026-06-11 | 3.10–3.14 | https://pypi.org/project/sktime/ |
| skforecast | 0.23.0 | 2026-07-08 | >=3.10 | https://pypi.org/project/skforecast/ |
| autogluon.timeseries | 1.5.0 | 2025-12-19 | >=3.10,<3.14 | https://pypi.org/project/autogluon.timeseries/ |
| prophet | 1.3.0 | 2026-01-27 | >=3.7 declared | https://pypi.org/project/prophet/ |

Detail and status:
- Darts: actively maintained, steady cadence (0.43.0 Mar 2026, 0.44.x Apr–May, 0.45.0 Jun 2026), ~9.5k stars. Broad model zoo from ARIMA to deep learning plus anomaly detection. Source: https://github.com/unit8co/darts/releases (accessed 2026-07-12). Full change detail lives at https://unit8co.github.io/darts/release_notes/RELEASE_NOTES.html.
- GluonTS: not formally declared "maintenance mode," but cadence has slowed sharply. GitHub REST API shows six releases in 2024, only two in 2025 (v0.16.1 Apr, v0.16.2 Jun), and one so far in 2026 (v0.16.3 Jun 29). It is now PyTorch-first (v0.16.0 bumped torch to 2.2), and it is the host repository for Chronos (the "Chronos" breaking-news banner appears in its docs). The MXNet backend is legacy; a maintainer discussion (awslabs/gluonts #3088, "MXnet will not receive updates anymore, what will happen to GluonTS?") frames the MXNet path as end-of-life. Fair characterization: alive and load-bearing for AWS's foundation-model work, but low-velocity as a general forecasting library. Sources: https://api.github.com/repos/awslabs/gluonts/releases ; https://github.com/awslabs/gluonts ; https://github.com/awslabs/gluonts/discussions/3088 (accessed 2026-07-12).
- sktime: reached its 1.0 milestone (1.0.0 then 1.0.1, Jun 2026). Unified framework across forecasting, classification, clustering, anomaly detection; 64-bit only, Python 3.10–3.14. Source: https://pypi.org/project/sktime/ (accessed 2026-07-12).
- skforecast: very active (0.23.0, 2026-07-08). It has leaned hard into foundation models: a `ForecasterFoundation` / `FoundationModel` wrapper exposes Chronos-2, Google TimesFM 2.5, Salesforce Moirai-2, TabICL, TabPFN-TS, and The Forecasting Company T0 behind the standard skforecast interface (backtesting, intervals, multi-series). Sources: https://skforecast.org/latest/user_guides/foundation-forecasting-models.html ; https://github.com/skforecast/skforecast (accessed 2026-07-12).
- AutoGluon-TimeSeries: v1.5.0 (2025-12-19), the strongest AutoML story. It defaults to and integrates the Chronos family; v1.5 ships Chronos-2 (zero-shot covariate support). Vendor benchmark claims: AutoGluon v1.5 reaches up to an 80% win rate over v1.4 across its benchmarks, and Chronos-2 posts a 90%+ win rate over Chronos-Bolt; Chronos-Bolt itself is billed as ~250x faster than the original Chronos. These are AWS-published, self-reported numbers — treat as vendor benchmarks, not independent. Sources: https://auto.gluon.ai/stable/whats_new/v1.5.0.html ; https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-chronos.html ; https://aws.amazon.com/blogs/machine-learning/fast-and-accurate-zero-shot-forecasting-with-chronos-bolt-and-autogluon/ (accessed 2026-07-12).
- Prophet: the "abandoned" framing needs qualifying. Meta still tags Prophet by its 2023 "prophet in 2023 and beyond" statement (light maintenance), yet it has shipped several releases since: 1.1.6 (2024-10), 1.1.7 (2025-05), 1.2.0 (2025-10), 1.2.2 (2026-01), 1.3.0 (2026-01-27). These are dependency-compat releases (pandas>=3.0 and numpy>=2.4 support in 1.3.0; latest CmdStan in 1.2.x), not new modelling features. So: maintained for compatibility, not evolving as a model. On accuracy, the literature consensus is unflattering: in default mode Prophet is often beaten by seasonal-naive and SARIMA baselines, and Nixtla's statsforecast reimplementations beat it on speed (statsforecast README claims ~500x faster) and frequently on MAPE across M3/M4. Prophet is best positioned as an interpretable, reproducible baseline rather than an accuracy leader. Sources: https://github.com/facebook/prophet ; https://pypi.org/pypi/prophet/json ; https://arxiv.org/html/2601.05929v1 ; https://arxiv.org/pdf/2011.10715 (accessed 2026-07-12). Flag: the full text of Meta's 2023 "in 2023 and beyond" post was not retrieved; the maintenance framing is inferred from the README link plus the compatibility-only nature of recent releases.

## 7. Breaking API changes 2024–2026 to warn about (Nixtla stack)

Sources: GitHub releases JSON for each repo (accessed 2026-07-12).

- statsforecast 2.0.0 (2024-11-26): major break. Removed deprecated behaviours; AutoARIMA `allowmean` and `allowdrift` now default to True (different model selection than 1.x); ARIMA/ETS/Theta reimplemented in C++. 2.0.3 (2025-10-29) additionally removed the deprecated `df` constructor argument (pass the DataFrame to `fit`/`forecast` instead) and added Python 3.13. Warn: 1.x AutoARIMA results are not reproducible under 2.x defaults.
- mlforecast 1.0.0 (2024-12-06): removed the `window_ops` and `numba` dependencies; lag transforms now come from coreforecast. Pre-1.0 `lag_transforms` code referencing window_ops functions must be rewritten. Earlier, v0.15.0 (2024-11-14) changed null-target row handling ("drop rows with null targets when dropna=False"). Current line is 1.1.0 (2026-07-10), which added `time_agg`/pooled lag transforms, `LookupLag`, `date_features_as_dummies` one-hot, and transfer learning with conformal prediction — additive, no breaks noted.
- hierarchicalforecast 1.0.0 (2024-12-16): major break. It no longer accepts `unique_id` as a DataFrame index (you must `.reset_index()`); added polars support; moved evaluation utilities into the utils module. The current reconcile contract passes the structure as a DataFrame `S_df` and `tags` as keywords. Warn: pre-1.0 hierarchical pipelines that relied on the indexed DataFrame or the older `reconcile(Y_hat_df, Y_df, S, tags)` positional/numpy-S form break. Flag: the current S_df/keyword contract is confirmed from the live docs example, and the v1.0.0 index break from the release note. No release note pins the exact version where S changed from numpy array to DataFrame, so it is attributed to the 1.0.0 dataframe-native migration with medium confidence.
- neuralforecast: v3.1.6 deprecated numpy-based loss functions; v3.2.0 (2026-07-10) removed `cpus`/`gpus` constructor params in favour of `ray_options`. Both can break existing distributed/loss configs. The v2.0.0 and v3.0.0 release bodies were not retrieved directly (the API pages consulted covered the 3.1.x–3.2.0 window), so pre-3.1 major-version break details are unverified here.
- Cross-cutting: the whole stack moved its Python floor to 3.10 (statsforecast excepted, still 3.9), and adopted pandas 2.2+ offset aliases (`'ME'`, `'QE'`, `'h'`), so old `freq='M'`/`'H'` strings now emit pandas deprecation warnings or errors.

## Items flagged as unverified
- coreforecast 0.0.18 exact release date (version and Python support confirmed).
- utilsforecast classifier/Requires-Python mismatch (3.9 classifier vs >=3.10 requirement); real floor is 3.10.
- hierarchicalforecast: exact release where S became a DataFrame (attributed to 1.0.0 with medium confidence).
- neuralforecast v2.0.0/v3.0.0 breaking-change bodies not fetched directly.
- Prophet Meta "in 2023 and beyond" maintenance statement inferred from README link plus release nature, not read in full.
- AutoGluon and Chronos accuracy numbers are AWS-published vendor benchmarks, not independent evaluations.
