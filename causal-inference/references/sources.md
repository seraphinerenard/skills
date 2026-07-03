# Sources for the causal-inference skill

Two verification tiers apply. Tier 1 entries were fetched and checked against
the live page on 2026-07-12 by a research agent; their URLs and version
numbers sit in `research/staggered-did-implementations.md` and are quoted
there with access dates. Tier 2 entries are canonical papers cited from
memory by author, venue, and year; the citations are standard and stable, and
the exact page numbers still deserve a check before appearing in a client
document.

## Tier 1, verified 2026-07-12 (URLs in the research sheet)

- Roth, Sant'Anna, Bilinski, Poe, "What's Trending in Difference-in-Differences," Journal of Econometrics 235(2), 2023. The survey consensus on staggered DiD.
- Roth, "Pretest with Caution," AER: Insights 4(3), 2022. Pre-trend tests lack power; conditioning on them distorts inference.
- Rambachan and Roth, "A More Credible Approach to Parallel Trends," Review of Economic Studies, 2023. Sensitivity analysis replacing pass/fail pre-testing.
- Borusyak, Jaravel, Spiess imputation estimator, Review of Economic Studies 91(6), 2024.
- Package status as of 2026-07-12: pyfixest 0.60.0; csdid 0.4.2; differences 0.3.0; diff-diff 3.7.0; anzonyquispe/honestdid 0.1.1; R `did` 2.5 (2026-06-15).
- pymc-marketing 0.19.4 (PyPI, 2026-05-06) with the MMM module; verified in the pricing skill's research sweep the same day.

## Tier 2, canonical citations to re-check before quoting page-level detail

- Callaway and Sant'Anna, "Difference-in-Differences with Multiple Time Periods," Journal of Econometrics 225(2), 2021. Group-time ATTs.
- Goodman-Bacon, "Difference-in-Differences with Variation in Treatment Timing," Journal of Econometrics 225(2), 2021. The TWFE weight decomposition.
- Sun and Abraham, "Estimating Dynamic Treatment Effects in Event Studies with Heterogeneous Treatment Effects," Journal of Econometrics 225(2), 2021.
- Abadie, Diamond, Hainmueller, "Synthetic Control Methods for Comparative Case Studies," JASA 105(490), 2010. Weights, placebo inference.
- Ben-Michael, Feller, Rothstein, "The Augmented Synthetic Control Method," JASA 116(536), 2021.
<!-- allow:C1 Utilizing appears in the cited paper title -->
- Deng, Xu, Kohavi, Walker, "Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data," WSDM 2013. CUPED; the 1 - rho^2 identity.
<!-- allow:CAN Modeling appears in the cited paper title; allow-note covers the next line too -->
- Jin and Rubin-style adstock/Hill MMM specification: Jin, Wang, Sun, Chan, Koehler, "Bayesian Methods for Media Mix Modeling with Carryover and Shape Effects," Google research paper, 2017.
- Bojinov, Simchi-Levi, Zhao on switchback design and carryover, Management Science, 2023.

## Known gaps

The geo-experimentation tool survey (GeoLift lineage, Meridian, Robyn current
status) and the MMM vendor survey did not complete in this build cycle; the
research agents assigned to them were cut off before returning. The SKILL.md
therefore names no current geo-testing or MMM product beyond pymc-marketing
and instructs a status check before recommending one. Backfill these two
sheets in the next research pass.
