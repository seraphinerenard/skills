# Post-deployment decay, named failures, and folklore provenance

## Named failure cases with numbers

Epic sepsis model, external validation. Wong et al., JAMA Internal Medicine
2021, validated Epic's widely deployed sepsis prediction model on 27,697
patients at Michigan Medicine and found AUC 0.63 against the vendor's
reported 0.76-0.83; at the operating threshold in use it identified 33% of
sepsis cases (missing 67%) while generating alerts on 18% of all
hospitalized patients. The model had spread across hundreds of hospitals on
the vendor's internal numbers, with no local validation and no monitoring
that would have surfaced the gap. This is the strongest single citation for
the local-validation and monitoring clauses in a delivery contract.

Unity Software, 2022. Unity's Q1 2022 shareholder letter and earnings call
attributed a revenue impact it sized near US$110M for the year to two
compounding data problems in its ad-targeting stack, one of them ingesting
bad data from a large customer into the model unchecked. The share price
fell about 37% the next day. This is the strongest single citation for data
contracts sitting upstream of model metrics.

Both citations are stable and public; fetch the primary documents (the JAMA
IM paper, Unity's Q1 2022 letter) before quoting them in client materials,
since this build cycle's research agents could not re-verify pages.

## The decay evidence

Vela et al., Scientific Reports 2022 ("temporal quality degradation in AI
models"), stress-tested model aging across dozens of dataset-model pairs and
found most degrade materially over time, with the onset and shape of decay
varying by domain and unpredictable in advance; the paper's term "AI aging"
covers the pattern. The practical content matches operations experience:
decay is the default and its timing is not forecastable from training-time
information, so the monitoring cadence, the proxy metrics, and the
retraining-policy backtest in this skill exist because no one can promise a
decay-free year. (Verify the exact counts in the paper before citing them
numerically.)

## Folklore-statistic provenance

"87% of data-science models never reach production" traces to a 2019
VentureBeat opinion piece; it cites no underlying study, and no dataset
supporting the number has surfaced since. The related "85% of AI projects
fail" line attributed to Gartner is a press paraphrase of a 2018 prediction
about outcomes through 2022, a forecast at the time it was quoted as a
measurement. Neither number belongs in client materials. When a
failure-rate anchor is genuinely needed, use a named, methodology-disclosed
survey and quote its scope, or use the client's own project history, which
is the only base rate that predicts their next project.

## Handoff practice worth citing

- Breck et al. (the ML Test Score paper, and the TFX data-validation work
  reported at MLSys 2019) for the data-contract layer: schema, null bands,
  volume bands, freshness, caught before scoring.
<!-- allow:A1 the contrast sits inside the cited paper title -->
- Sambasivan et al., CHI 2021 ("Everyone wants to do the model work, not the
  data work"): 92% of 53 surveyed ML practitioners reported data-cascade
  incidents, small upstream issues compounding downstream. The citation for
  why the contract log is read before the drift dashboard.
- Mitchell et al. 2019 for model cards; the SKILL's variant spends the
  effort on limitations written as invalidation events in the client's own
  vocabulary, since that is the section that gets opened during incidents.

## The pattern under the cases

Each named failure is a missing cheap control, and the controls compose into
the delivery checklist this skill's SKILL.md carries: local validation
before trust (Epic), data contracts before model metrics (Unity), decay
monitoring with proxies because labels lag (Vela), and an owner on the
client side because unowned models die quietly.
