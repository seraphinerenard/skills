# Sources

Every URL below was accessed 2026-07-12. The four fact sheets under
research/ hold the full extraction notes and per-claim verification flags;
this file is the consolidated index.

## M5 and global-model retail forecasting

- M5 accuracy results paper (Makridakis, Spiliotis, Assimakopoulos, IJF 38(4) 2022): https://www.sciencedirect.com/science/article/pii/S0169207021001874
- M5 accuracy preprint full text: https://statmodeling.stat.columbia.edu/wp-content/uploads/2021/10/M5_accuracy_competition.pdf
- M5 background paper (IJF 38(4) 2022): https://www.sciencedirect.com/science/article/pii/S0169207021001187
- M5 uncertainty results paper (IJF 38(4) 2022): https://www.sciencedirect.com/science/article/pii/S0169207021001722
- M5 conclusions paper (IJF 38(4) 2022): https://researchportal.bath.ac.uk/en/publications/the-m5-competition-conclusions
- Locality and globality theory (Montero-Manso and Hyndman): https://arxiv.org/abs/2008.00444
- M5 uncertainty winner paper (Lander and Wolfinger): https://www.sciencedirect.com/science/article/abs/pii/S0169207021002090
- GoodsForecast second-place uncertainty paper: https://ideas.repec.org/a/eee/intfor/v38y2022i4p1434-1441.html
- M5 uncertainty critique (GAMLSS, overdispersion): https://arxiv.org/pdf/2107.06675
<!-- allow:C1 robustness appears in the cited paper title -->
- Global bottom-up robustness check: https://www.sciencedirect.com/science/article/abs/pii/S0169207021001400
- Matthias Anderer second-place repo: https://github.com/matthiasanderer/m5-accuracy-competition
- M5 Kaggle uncertainty evaluation page: https://www.kaggle.com/competitions/m5-forecasting-uncertainty
- Practitioner post-mortem (Tweedie, magic multiplier, shake-up): https://www.christophenicault.com/post/m5_forecasting_accuracy/
- M5 feature-engineering summary: https://medium.com/analytics-vidhya/predicting-the-future-with-learnings-from-the-m5-competition-d54e84ca3d0d
- WSPL gameability discussion: https://michelbaudin.com/2021/07/16/evaluating-sales-forecasts/

## Censored demand and unconstraining

- Trapero, de Frutos, Pedregal, Tobit Kalman filter for lost sales (IJF 40(3) 2024): https://www.sciencedirect.com/science/article/abs/pii/S0169207023000961
- Spiral-down effect (Cooper, Homem-de-Mello, Kleywegt, OR 2006): https://ideas.repec.org/a/inm/oropre/v54y2006i5p968-987.html
- Unconstraining methods survey (Guo, Xiao, Li 2012): https://onlinelibrary.wiley.com/doi/10.1155/2012/270910
- Taxonomy of uncensoring methods (Azadeh, Marcotte, Savard 2014): https://link.springer.com/article/10.1057/rpm.2014.8
- FreshRetailNet-50K (Dingdong stockout-annotated benchmark): https://arxiv.org/abs/2505.16319
- Weatherford and Poelt, airline unconstraining gains: https://link.springer.com/article/10.1057/palgrave.rpm.5170027
- Queenan et al., unconstraining comparison (POM 2007): https://journals.sagepub.com/doi/10.1111/j.1937-5956.2007.tb00292.x
- Kourentzes, Li, Strauss, small-demand unconstraining: https://link.springer.com/article/10.1057/s41272-017-0117-x
- Gaussian processes for unconstraining: https://arxiv.org/abs/1711.10910
- Nahmias, lost-sales demand estimation (NRL 1994): https://onlinelibrary.wiley.com/doi/abs/10.1002/1520-6750(199410)41:6%3C739::AID-NAV3220410605%3E3.0.CO;2-A
- Agrawal and Smith, negative binomial retail demand (NRL 1996): https://onlinelibrary.wiley.com/doi/10.1002/(SICI)1520-6750(199609)43:6%3C839::AID-NAV4%3E3.0.CO;2-5
- Tobit exponential smoothing: https://arxiv.org/abs/2407.17920
- Tobit ES with time aggregation: https://arxiv.org/html/2409.05412
- Jain, Rudi, Wang, stockout timing (OR 2015): https://pubsonline.informs.org/doi/10.1287/opre.2014.1326
- Sachs and Minner, data-driven newsvendor with censoring (IJPE 2014): https://www.sciencedirect.com/science/article/abs/pii/S092552731300203X
- Kaplan-Meier adaptive inventory control (Huh et al., OR 2011): https://ideas.repec.org/a/inm/oropre/v59y2011i4p929-941.html
- Besbes and Muharremoglu, censoring in the newsvendor (MS 2013): https://ideas.repec.org/a/inm/ormnsc/v59y2013i6p1407-1424.html
- Data-driven censored newsvendor: https://arxiv.org/abs/2412.01763
- Vulcano, van Ryzin, Ratliff, primary demand EM (OR 2012): https://pubsonline.informs.org/doi/10.1287/opre.1110.1012
- Anupindi, Dada, Gupta, stockout substitution (MkSc 1998): https://pubsonline.informs.org/doi/10.1287/mksc.17.4.406
- Conlon and Mortimer, incomplete availability (AEJ Micro 2013): https://www.nber.org/papers/w14315
- Ban and Rudin, big-data newsvendor (OR 2019): https://pubsonline.informs.org/doi/10.1287/opre.2018.1757
- Amazon Deep Inventory Management (glance-view correction): https://arxiv.org/abs/2210.03137
- Lokad review of Deep Inventory Management: https://www.lokad.com/blog/2023/12/19/deep-inventory-management-opinionated-review/
- Amazon forecasting-algorithm history (MQ lineage): https://www.amazon.science/latest-news/the-history-of-amazons-forecasting-algorithm
- MQ-RNN/CNN multi-horizon quantile forecaster: https://arxiv.org/pdf/1711.11053
- Zalando production demand forecasting (masking and size imputation): https://arxiv.org/abs/2305.14406
- AWS Forecast missing-value guidance (NaN for out-of-stock): https://aws.amazon.com/blogs/machine-learning/managing-missing-values-in-your-target-and-related-datasets-with-automated-imputation-support-in-amazon-forecast/
- Blue Yonder unconstrained-demand FAQ: https://info.blueyonder.com/retail-planning-category-management/what-is-retail-demand-forecasting
- RELEX demand planning RFP documentation: https://www.relexsolutions.com/relex-demand-planning-and-sensing-rfp/
- DeHoratius and Raman, inventory record inaccuracy (MS 2008): https://pubsonline.informs.org/doi/10.1287/mnsc.1070.0789

## Intermittent demand

- Croston 1972, Syntetos-Boylan 2005, SBC categorization 2005, TSB 2011,
  ADIDA 2011: canonical journal citations are given in full in
  intermittent-demand.md; online copies via the publishers above and
  https://ideas.repec.org/ mirrors.

## Utility load forecasting

- EIA degree-day definitions: https://www.eia.gov/energyexplained/units-and-calculators/degree-days.php
- EDF adaptive GAM under lockdown (Obst, de Vilmarest, Goude, IEEE TPS 2021): https://ar5iv.labs.arxiv.org/html/2009.06527
- Online GAM selection for load (Das et al. 2025): https://arxiv.org/html/2503.24019v1
- Goude, Nedellec, Kong, 2,260-substation GAMs (IEEE TSG 2014): https://www.researchgate.net/publication/260449195_Local_Short_and_Middle_Term_Electricity_Load_Forecasting_With_Semi-Parametric_Additive_Models
- GEFCom2014 winning quantile-GAM method (Gaillard, Goude, Nedellec, IJF 2016): https://www.sciencedirect.com/science/article/abs/pii/S0169207015001545
- Expert aggregation for consumption (Devaine et al. 2013): https://arxiv.org/pdf/1207.1965
- PJM load forecasting whitepaper (2016, WWP and THI formulas): https://www.pjm.com/-/media/DotCom/library/reports-notices/load-forecast/2016-load-forecast-whitepaper.pdf
- PJM Manual 19: https://www.pjm.com/-/media/DotCom/documents/manuals/m19.pdf
- ERCOT 2025 long-term load forecast methodology and data-centre revisions: https://www.ercot.com/files/docs/2025/04/07/8.1-Long-Term-Load-Forecast-Update-2025-2031-and-Methodology-Changes.pdf
- ERCOT 2025 LTLF report: https://www.ercot.com/files/docs/2025/04/08/2025-LTLF-Report.pdf
- MISO load-forecast development presentation (2024): https://www.in.gov/iurc/files/Load-Forecast-Development-and-Use-at-MISO.pdf
- CAISO 2025 summer assessment: https://www.caiso.com/content/summer-loads-resources-assessment/2025/index.html
- CAISO July 2024 heat-wave forecast performance: https://www.yesenergy.com/blog/caiso-load-forecasts
- NESO day-ahead demand forecast portal: https://www.neso.energy/data-portal/1-day-ahead-demand-forecast
- GB effective-temperature description: https://arxiv.org/pdf/2604.20445
- ACS 1-in-20 methodology: https://www.emrdeliverybody.com/Lists/Latest%20News/Attachments/189/SC4L12%20ACS%20Methodology.pdf
- MinT (Wickramasuriya, Athanasopoulos, Hyndman, JASA 2019): https://robjhyndman.com/publications/mint/
- fpp3 reconciliation chapter: https://otexts.com/fpp3/reconciliation.html
<!-- allow:CAN smart-meter appears in the cited paper title -->
- Coherent probabilistic smart-meter forecasts (Ben Taieb, Taylor, Hyndman, JASA 2021): https://robjhyndman.com/publications/hpf-electricity/
- MinT for distribution transformers with AMI data: https://ieeexplore.ieee.org/document/10233865/
- Direct vs indirect hierarchical net-load forecasting (ITEGAM-JETIA 2026): https://itegam-jetia.org/journal/index.php/jetia/article/view/3015
- Hierarchical transfer learning for load (Antoniadis, Gaucher, Goude, IJF 2024): https://ideas.repec.org/a/eee/intfor/v40y2024i2p641-660.html
- Conformal prediction for hierarchical data: https://arxiv.org/pdf/2411.13479

## Libraries

- statsforecast: https://pypi.org/project/statsforecast/ and https://raw.githubusercontent.com/Nixtla/statsforecast/main/README.md
- mlforecast: https://pypi.org/project/mlforecast/ and https://nixtlaverse.nixtla.io/mlforecast/forecast.html
- neuralforecast: https://pypi.org/project/neuralforecast/
- hierarchicalforecast: https://pypi.org/project/hierarchicalforecast/ and https://raw.githubusercontent.com/Nixtla/hierarchicalforecast/main/hierarchicalforecast/methods.py
- utilsforecast: https://pypi.org/project/utilsforecast/
- Darts: https://pypi.org/project/darts/
- GluonTS (MXNet end-of-life discussion): https://github.com/awslabs/gluonts/discussions/3088
- sktime: https://pypi.org/project/sktime/
- skforecast foundation-model wrappers: https://skforecast.org/latest/user_guides/foundation-forecasting-models.html
- AutoGluon-TimeSeries 1.5 release notes: https://auto.gluon.ai/stable/whats_new/v1.5.0.html
- AutoGluon Chronos tutorial: https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-chronos.html
- AWS Chronos-Bolt blog: https://aws.amazon.com/blogs/machine-learning/fast-and-accurate-zero-shot-forecasting-with-chronos-bolt-and-autogluon/
- Prophet status: https://github.com/facebook/prophet and https://pypi.org/pypi/prophet/json

## Foundation models

- Chronos-2 paper: https://arxiv.org/pdf/2510.15821
- Moirai 2.0 paper: https://arxiv.org/html/2511.11698v3
- GIFT-Eval benchmark summary: https://www.emergentmind.com/topics/gift-eval
- Foundation-model calibration audit: https://arxiv.org/pdf/2510.16060
- Zero-shot energy load benchmark on consumer hardware: https://arxiv.org/html/2602.10848
- Foundation-model ensembling for demand forecasting: https://arxiv.org/html/2507.22053v1
- Intermittent local vs global models: https://arxiv.org/pdf/2601.14031
- TSFM demand-forecasting comparison (Grid Dynamics): https://www.griddynamics.com/blog/ai-models-demand-forecasting-tsfm-comparison
