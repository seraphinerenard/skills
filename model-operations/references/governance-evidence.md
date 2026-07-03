# The override and FVA evidence

Citations here are named from the literature; the build cycle's research
agents were cut off before fetching pages, so page-level details carry a
verify-before-quoting flag while the findings themselves are the stable,
widely replicated ones.

## Judgmental adjustments, the published record

Fildes, Goodwin, Lawrence and Nikolopoulos (2009, International Journal of
Forecasting): over 60,000 forecasts across four supply-chain companies, the
largest published study of practitioner overrides. Findings that survived
replication: adjustments helped on average in three of the four firms; large
adjustments improved accuracy on average while small ones damaged it;
downward adjustments outperformed upward ones by a wide margin, consistent
with optimism riding on upward touches; and adjustment was pervasive (one
firm adjusted 91% of all forecasts). Franses and Legerstee (2009-2013, a
series of papers on pharmaceutical SKU forecasts) found comparably high
adjustment rates and, on accuracy, that expert-adjusted forecasts were
usually no better than the model baseline.

Davydenko and Fildes (2013, IJF) is the measurement warning: evaluating the
same adjustments in MAPE and in an average relative MAE flipped the
conclusion, because MAPE rewards under-forecasting. The FVA stairstep in the
SKILL therefore runs on WAPE with bias printed beside it, and a client's
existing MAPE-based override review deserves recomputation before its
conclusions are repeated.

The operational reading, encoded in `assets/override_scoring.py`: overrides
earn their keep only when logged and scored; small habitual touches are
process cost with negative expected return; a recurring, explainable
override is a feature request for the model.

## FVA methodology

The stairstep follows Gilliland's forecast value added methodology (the SAS
white papers and the 2013 book The Business Forecasting Deal): score every
process step against the step upstream and against a naive baseline, on
identical rows. The two integrity rules from the SKILL bear repeating
because both failures are common in client FVA decks: a step scored on the
subset of series it touched flatters itself, and FVA against plain naive
overstates everyone when the demand is seasonal, so the baseline is seasonal
naive.

A related anchor from competition evidence: in the M5 accuracy competition,
48.4% of 5,507 teams beat the plain naive benchmark and 7.5% beat the
strongest statistical benchmark (the organizers' results paper, IJF 38(4),
2022; URLs in the demand-forecasting skill's research sheets). Teams trying
hard fail to add value over good baselines about half the time; planning
organizations that never measure it should expect no better.

## Plan stability

Accuracy improvements that arrive with forecast whipsaw get rejected by
planners because every revision propagates through supply plans with a real
changeover cost. `assets/fva.py` computes period-over-period plan churn
(mean absolute revision of the locked plan, in units and in percent)
alongside FVA so the two trade off explicitly in the same table. Present
stability beside accuracy in every review; a 1-point WAPE gain bought with a
doubling of revision volume is usually a net loss inside the S&OP cycle, and
the churn number is what makes that conversation concrete.

## Verification status

- Fildes et al. 2009, Franses and Legerstee, Davydenko and Fildes 2013:
  canonical citations, stable findings; fetch DOIs before quoting page
  numbers in a client document.
- M5 figures: verified against the organizers' results paper on 2026-07-12
  (see the demand-forecasting skill's research sheets for URLs).
- Gilliland FVA: methodology description, uncontroversial; the specific
  stairstep numbers in the SKILL come from this repo's own demo, marked as
  synthetic.
