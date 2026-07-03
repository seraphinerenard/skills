# Sources

All URLs accessed 2026-07-12. Package versions were additionally verified
by installing into a fresh Python 3.14 venv on that date (numpy 2.5.1,
scipy 1.18.0, pandas 2.3.3, lifelines 0.30.3) and by the PyPI JSON API.

## Tooling

- S1. lifelines on PyPI. 0.30.3, released 2026-03-05, requires Python
  >= 3.11; deps numpy >= 1.14, scipy >= 1.7, pandas >= 2.1 and < 3.0.
  https://pypi.org/project/lifelines/
- S2. scikit-survival on PyPI. 0.28.0, released 2026-07-05, requires
  Python >= 3.11; pins scikit-learn >= 1.9.0 and < 1.10, numpy >= 2.0.
  https://pypi.org/project/scikit-survival/
- S3. reliability on PyPI. 0.9.0, released 2025-03-07; no release in the
  16 months to 2026-07, so treat as maintenance mode.
  https://pypi.org/project/reliability/
- S6. lifelines documentation, time-varying survival regression;
  CoxTimeVaryingFitter and its prediction limitations.
  https://lifelines.readthedocs.io/en/latest/Time%20varying%20survival%20regression.html
- S16. scikit-survival documentation, evaluation metrics
  (concordance_index_ipcw, integrated_brier_score, cumulative_dynamic_auc).
  https://scikit-survival.readthedocs.io/en/stable/user_guide/evaluating-survival-models.html

## RUL benchmarks and foundation models

- S4. Vollert and Theissler, "Challenges of machine learning-based RUL
  prognosis: A review on NASA's C-MAPSS data set" (IEEE ETFA 2021).
  https://www.researchgate.net/publication/353119926_Challenges_of_machine_learning-based_RUL_prognosis_A_review_on_NASA's_C-MAPSS_data_set
- S5. Basora et al., "A Benchmark on Uncertainty Quantification for Deep
  Learning Prognostics" (arXiv 2302.04730); documents the truncated,
  right-censored test trajectories and the piecewise-linear capped target.
  https://arxiv.org/pdf/2302.04730
- S11. "Time-Series Foundation Model Embeddings for Remaining Useful Life
  Estimation" (arXiv 2606.11990, June 2026); frozen Chronos-2 embeddings
  plus a regression head against conventional baselines.
  https://arxiv.org/pdf/2606.11990
- S12. Vendor and trade coverage of time-series foundation models in
  industry, 2026; TimesFM in BigQuery ML, ROI claims without denominators
  (marketing, cited as evidence of claims only).
  https://blog.pebblous.ai/report/timesfm-industrial-forecasting/en/ and
  https://machinelearningmastery.com/the-2026-time-series-toolkit-5-foundation-models-for-autonomous-forecasting/

## Maintenance data quality and mining practice

- S7. Trade-press figures for haul-truck economics: unplanned downtime
  $5,000 to $20,000 per hour, in-service final-drive failure around
  $200,000, ultra-class truck price $5M to $8M, mining duty 5,000 to 7,000
  operating hours per year. Trade sources, so quote as ranges with this
  provenance stated.
  https://heavyvehicleinspection.com/blog/post/mining-haul-truck-preventive-maintenance and
  https://honestdig.io/blog/reduce-unplanned-equipment-downtime-mine
- S8. Hodkiewicz and Ho, "Cleaning historical maintenance work order data
  for reliability analysis" (Journal of Quality in Maintenance
  Engineering, 2016).
  https://www.researchgate.net/publication/301596725_Cleaning_historical_maintenance_work_order_data_for_reliability_analysis
- S9. ReliaMag, "How to improve CMMS data quality"; petrochemical case
  where trimming the failure-code list from 87 to 22 options raised coding
  accuracy from 41% to 89% in three months (trade press).
  https://reliamag.com/cartoons/improve-cmms-data-quality/
- S10. Stewart et al., "Large Language Models for Failure Mode
  Classification: An Investigation" (arXiv 2309.08181); LLM annotation of
  maintenance work-order text against expert labels.
  https://arxiv.org/pdf/2309.08181

## Books and standards

- S13. Montgomery, Introduction to Statistical Quality Control, 7th ed.,
  Wiley; ch. 9 for EWMA and CUSUM ARL design tables. The constants used in
  `control_charts.py` were re-verified by Monte Carlo in that module.
- S14. Uno, Cai, Pencina, D'Agostino, Wei, "On the C-statistics for
  evaluating overall adequacy of risk prediction procedures with censored
  survival data", Statistics in Medicine 30(10), 2011.
  https://pubmed.ncbi.nlm.nih.gov/21484848/
- S15. ISO 14224 (reliability and maintenance data collection for
  equipment: taxonomy, equipment boundaries, failure modes) and ISO 20816
  (mechanical vibration severity evaluation; successor to ISO 10816).
  https://www.iso.org/standard/64076.html and
  https://www.iso.org/standard/63180.html
