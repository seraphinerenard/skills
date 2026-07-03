# Sources for the model-operations skill

The build cycle's dedicated research agents (drift tooling, FVA and override
evidence, handoff practice) were cut off by an API outage before returning
sourced fact sheets, so this skill cites by author, venue, and year, with
one live check noted below. Every citation is canonical and findable from
its name; fetch the primary document before quoting page-level numbers in a
client deliverable. Backfill a URL-verified sheet in the next research pass.

## Cited in SKILL.md and the references

- Siddiqi, N., Credit Risk Scorecards, 2006. Provenance of the 0.10/0.25 PSI rules of thumb.
- Yurdakul, B., "Statistical Properties of the Population Stability Index," PhD thesis, Western Michigan University, 2018. The PSI null distribution.
- Evidently documentation, defaults for per-column drift tests. Accessed 2026-07-12 during the build (KS with p < 0.05 up to 1,000 reference rows, scaled Wasserstein with threshold 0.1 above).
- Fildes, Goodwin, Lawrence, Nikolopoulos, "Effective forecasting and judgmental adjustments," International Journal of Forecasting 25(1), 2009.
- Franses and Legerstee, papers on expert adjustment of pharmaceutical SKU forecasts, 2009-2013.
- Davydenko and Fildes, "Measuring forecasting accuracy: The case of judgmental adjustments to SKU-level demand forecasts," IJF 29(3), 2013.
- Gilliland, M., The Business Forecasting Deal, 2010, and the SAS FVA white papers.
- Makridakis, Spiliotis, Assimakopoulos, "The M5 accuracy competition," IJF 38(4), 2022. Verified 2026-07-12 via the demand-forecasting skill's research sheets.
- Breck, Cai, Nielsen, Salib, Sculley, "The ML Test Score," and the TFX data-validation system paper (MLSys 2019).
<!-- allow:A1 the contrast sits inside the cited paper title -->
- Sambasivan et al., "Everyone wants to do the model work, not the data work," CHI 2021.
- Mitchell et al., "Model Cards for Model Reporting," FAT* 2019.
- Wong et al., "External Validation of a Widely Implemented Proprietary Sepsis Prediction Model," JAMA Internal Medicine 181(8), 2021.
- Unity Software Q1 2022 shareholder letter and earnings call (the ~US$110M data-quality impact).
- Vela et al., "Temporal quality degradation in AI models," Scientific Reports 12, 2022.
- VentureBeat, 2019 opinion piece, origin of the unsupported "87%" statistic (cited here only as provenance for why the number is banned from client materials).

## Repo-internal

- `assets/drift.py`, `assets/fva.py`, `assets/retraining_policy.py`,
  `assets/override_scoring.py`: every table in SKILL.md marked as a demo
  reproduces from these on synthetic data.
- The alert doctrine cross-referenced from the daemon-ops skill.
