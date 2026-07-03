# Time-series foundation models, mid-2026 state

Zero-shot pretrained forecasters changed the default starting point of an
engagement: a competent probabilistic baseline now costs one function call
and no feature work. This file records what the 2026 evidence supports, where
the models earn a permanent place in the stack, and where tuned task models
still win. All access dates 2026-07-12; URLs in sources.md.

## The roster

| model | maker | shape | covariates | access |
|---|---|---|---|---|
| Chronos-2 | Amazon | tokenized LM lineage, universal (univariate, multivariate, covariates) | yes, zero-shot | AutoGluon-TimeSeries >= 1.5 default; HuggingFace |
| Chronos-Bolt | Amazon | encoder-decoder rework of Chronos | no | AutoGluon; HuggingFace; runs on CPU |
| TimesFM 2.5 | Google | decoder-only | limited; check current docs | HuggingFace; skforecast wrapper |
| Moirai-2 | Salesforce | encoder-decoder, any-variate | yes | HuggingFace; skforecast wrapper |
| TiRex | NX-AI | xLSTM-based | no | HuggingFace |
| TabPFN-TS | Prior Labs | tabular prior-fitted network applied to TS | yes (tabular features) | package; skforecast wrapper |
| TimeGPT | Nixtla | closed API | yes | API only |

skforecast's ForecasterFoundation wraps Chronos-2, TimesFM 2.5, Moirai-2,
TabICL, TabPFN-TS and The Forecasting Company's T0 behind one backtesting
interface, which is the fastest way to run a fair bake-off (skforecast docs,
accessed 2026-07-12).

## Benchmark standing

GIFT-Eval (97 task configurations over 55 datasets, normalized MASE and
CRPS) is the reference leaderboard. As of its 2026 state, Chronos-2 leads on
win rate and skill score under both weighted quantile loss and MASE, ahead of
TiRex and TimesFM-2.5; Moirai-2 ranks high among models with audited
non-leaking pretraining corpora (Chronos-2 paper, arXiv 2510.15821; Moirai
2.0 paper, arXiv 2511.11698; GIFT-Eval summary at emergentmind.com). Two
structural findings replicate across evaluations: encoder-decoder
architectures (Moirai family) hold up better at long horizons because
decoder-only recursion accumulates error, and leaderboard gains concentrate
on low-frequency, strongly seasonal, trended series.

Domain spot checks. On consumer-hardware energy load, zero-shot foundation
models beat seasonal naive by about 47% at sufficient context length, with
Chronos-Bolt, Chronos-2 and Moirai-2 clustered near MASE 0.31-0.33 (arXiv
2602.10848). On M5-style covariate-rich sparse retail, tree ensembles remain
the winning family and foundation models contribute as ensemble members
(arXiv 2507.22053 uses FM ensembling to approach, and in places beat, the
tuned-GBM frontier; the base observation that LightGBM dominates the M5
leaderboard stands). Calibration audits find foundation-model intervals
imperfectly calibrated out of the box, so empirical coverage checks stay
mandatory before quoting their quantiles (arXiv 2510.16060).

Vendor numbers to treat as vendor numbers: AWS reports Chronos-2 winning
90%+ of comparisons against Chronos-Bolt, and Chronos-Bolt running about
250x faster than original Chronos; both are self-published benchmarks
(AutoGluon 1.5 release notes and AWS ML blog).

## Where they win in production

- Day-one baseline and FVA yardstick. A zero-shot Chronos-2 or Moirai-2 run
  costs minutes and sets the bar every engineered model must clear. When a
  tuned global GBM with the client's covariates cannot beat the zero-shot
  baseline, the feature pipeline is broken, and that diagnosis alone justifies
  the run.
- Cold start and short history: new stores, new regions, portfolios where
  most series have under a year of data. Pretraining substitutes for the
  history the client does not have.
- Long-tail breadth: thousands of low-value series that will never justify
  per-domain modelling effort get a competent probabilistic forecast at zero
  marginal engineering cost.
- Speed of iteration: Chronos-Bolt on CPU makes the baseline runnable inside
  a client workshop, no GPU procurement conversation required.

## Where they lose

- Covariate-rich retail: promos, price, SNAP-style calendars carry most of
  the forecastable signal at SKU-store level, and models that ingest those
  covariates natively and are trained on the client's own price response
  (global GBMs, Zalando-style deep models) keep beating zero-shot FMs there.
  Chronos-2's zero-shot covariate support narrows this gap; it has not closed
  it on the retail benchmarks available as of mid-2026.
- Intermittent tails: rate-plus-distribution methods sized to service levels
  (see intermittent-demand.md) answer the actual inventory question; FM
  quantiles on zero-heavy series are exactly where the calibration audits
  find the weakest coverage.
- Institutionalized domains with mature feature stacks: utility STLF with
  operational GAM pipelines already sits near the weather-forecast error
  floor, so the FM adds a baseline, never a replacement.
- Anything where the client needs the mechanism (price elasticity, promo
  decomposition): the FM is a black box over history and covariates; the
  decomposition deliverable still comes from the structured model.

## Playbook

Run the zero-shot FM first, log its rolling-origin scores with
assets/evaluation.py, and let it referee the rest of the engagement. Promote
it to production only for the segments above (cold start, long tail) and
re-check empirical coverage on the client's data before quoting intervals.
Fine-tuning is a second-line move: AutoGluon's fine-tuned Chronos variants
help on stable single-domain corpora, and the gain rarely beats adding the
same effort to the GBM's features on covariate-rich problems.
