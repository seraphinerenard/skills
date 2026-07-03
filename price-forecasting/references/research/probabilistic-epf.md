<!-- Compiled 2026-07-12. -->

---

# Probabilistic Electricity Price Forecasting (EPF): Findings Report

Date of research: 2026-07-12. Numbers are quoted with their source URL. Items that could not be verified are flagged explicitly.

## 1. Quantile Regression Averaging (QRA) foundations

**Nowotarski & Weron (2015), "Computing electricity spot price prediction intervals using quantile regression and forecast averaging", Computational Statistics 30(4), 791-803. DOI 10.1007/s00180-014-0523-0.**
URL: https://link.springer.com/article/10.1007/s00180-014-0523-0 (working-paper version: https://ideas.repec.org/p/wuu/wpaper/hsc1312.html)
What it says: this is the paper that introduces QRA. QRA runs a quantile regression where the explanatory variables are a pool of point forecasts from several individual models, and the regression estimates each conditional quantile of the spot price directly. The source states the QRA prediction intervals are more accurate than those from the best individual model tested (a smoothed nonparametric autoregressive model). QRA needs only point forecasts as inputs, which is why it became the default probabilistic-EPF baseline.

**Nowotarski & Weron (2018), "Recent advances in electricity price forecasting: A review of probabilistic forecasting", Renewable and Sustainable Energy Reviews 81(1), 1548-1568. DOI 10.1016/j.rser.2017.05.234.**
URL: https://ideas.repec.org/a/eee/rensus/v81y2018ip1p1548-1568.html (open working-paper: https://ideas.repec.org/p/wuu/wpaper/hsc1808.html)
What it says: tutorial review of probabilistic EPF. It sets out the evaluation discipline the whole field now uses: the pinball (quantile) loss, the aggregate pinball score across quantiles as a CRPS proxy, prediction-interval coverage and reliability, and the significance tests (Diebold-Mariano, conditional predictive ability). It positions QRA and Factor-QRA as leading interval-forecast methods at that time.

**GEFCom2014 probabilistic price track.**
URLs: Gaillard, Goude, Nedellec (2016), "Additive models and robust aggregation for GEFCom2014 probabilistic electric load and electricity price forecasting", International Journal of Forecasting 32(3) — https://www.sciencedirect.com/science/article/abs/pii/S0169207015001545 ; manuscript http://pierre.gaillard.me/doc/GaillardGoudeNedellec2015.pdf ; Maciejowska & Nowotarski (2016), "A multiple quantile regression approach to the wind, solar, and price tracks of GEFCom2014" — https://www.researchgate.net/publication/301773887.
What it says: in GEFCom2014 the pinball score was averaged across 99 quantiles and across the 24 hours of the target day. Team Tololo (Gaillard, Goude, Nedellec) won the price track using quantile regression via pinball-loss minimization plus generalized additive models and robust online aggregation of experts. The Wroclaw team (Maciejowska & Nowotarski) applied a multiple-quantile-regression / QRA-style approach and was among the top performers. Correction to a common premise: the outright price-track winner was Team Tololo's quantile-GAM-plus-aggregation, and QRA rose to prominence around this competition as a top method, rather than being the sole winning method. No single headline pinball number for the price track is extractable from these sources; flag.

## 2. Distributional Deep Neural Networks (DDNN)

**Marcjasz, Narajewski, Weron, Ziel (2023), "Distributional neural networks for electricity price forecasting", Energy Economics 125, article 106843. DOI 10.1016/j.eneco.2023.106843. arXiv 2207.02832.**
URLs: https://ideas.repec.org/a/eee/eneeco/v125y2023ics0140988323003419.html ; https://arxiv.org/abs/2207.02832
Method (confirmed): a deep neural network with a final "probability layer" whose outputs are the parameters of a parametric distribution. Two variants: the Normal distribution (2 parameters, location and scale) and Johnson's SU distribution (4 parameters: location, scale, and two shape parameters for skewness and tail weight). The JSU variant is the point of the paper because electricity prices are skewed and heavy-tailed. One network produces both the point forecast and the full predictive distribution, so no separate QRA post-processing step is needed.
Dataset: German EPEX day-ahead prices. The full sample runs 1 January 2015 to 31 December 2020, with the out-of-sample test beginning 27 June 2019 (the same split is described in the Brusaferri et al. conformal paper below, which reuses this benchmark), giving roughly 553 test days over the calm 2019-2020 regime.
Headline results (confirmed exact wording from the abstract): the JSU-parameterized DDNN "outperforms state-of-the-art benchmarks by over 7% in terms of the continuous ranked probability score and by 8% in terms of the per-transaction profits." The benchmarks it beats are LASSO-estimated regressions (LEAR) with QRA and standard DNNs combined with QRA. Python code is on GitHub.
Flag: the paper's own absolute mean CRPS in EUR/MWh could not be confirmed from a primary extract (the arXiv PDF is Flate-compressed and no arXiv HTML render exists for this ID). The >7% CRPS and 8% profit figures are confirmed. For an absolute anchor of DDNN-JSU performance, use the downstream re-evaluations below.
Downstream absolute DDNN-JSU CRPS (EUR/MWh), from papers that re-ran it:
- German market (from the IDR paper, section 3): 1.342 (2020), 5.395 (2021), 13.375 (2022), 5.265 (2023).
- German market (from the Quantile Neural Basis Models paper, arXiv 2509.14113, test window Oct 2023-Sep 2024): the JSU-DNN "J-DNN" scored CRPS 3.809, versus the proposed QNBM at 3.789.

## 3. Isotonic Distributional Regression (IDR) for EPF

**Lipiecki, Uniejewski, Weron (2024), "Postprocessing of point predictions for probabilistic forecasting of day-ahead electricity prices: The benefits of using isotonic distributional regression", Energy Economics 139(C). arXiv 2404.02270.**
URLs: https://www.sciencedirect.com/science/article/pii/S014098832400642X ; https://arxiv.org/abs/2404.02270
Method: IDR (from Henzi, Ziegel & Gneiting, JRSS-B 2021, "Isotonic distributional regression", https://ideas.repec.org/a/bla/jorssb/v83y2021i5p963-993.html) is a nonparametric method that learns the conditional predictive distribution under a stochastic-order (isotonicity) constraint, with no distributional-family assumption and no hyperparameters to tune. The paper post-processes LEAR point forecasts three ways: QRA (called QRM here), Conformal Prediction (CP), and IDR, then averages the three into an ensemble (LEAR-Ave).
Datasets: German (BZN|DE-LU) and Spanish (BZN|ES) day-ahead markets. Full data 1 Jan 2015 to 31 Dec 2023; test period 27 June 2019 to 31 Dec 2023 (4.5 years); sub-periods 2020 (554 days) and 2021, 2022, 2023 (365 days each).
CRPS (EUR/MWh), Germany, by year (2020 / 2021 / 2022 / 2023):
- LEAR-QRM (QRA): 1.350 / 4.189 / 10.651 / 4.422
- LEAR-CP: 1.369 / 4.399 / 10.864 / 4.582
- LEAR-IDR: 1.422 / 4.389 / 10.926 / 4.336
- LEAR-Ave (three-method ensemble): 1.310 / 3.970 / 10.199 / 4.215 (best)
- DDNN-JSU (neural benchmark): 1.342 / 5.395 / 13.375 / 5.265
CRPS (EUR/MWh), Spain, by year:
- LEAR-Ave: 0.938 / 3.832 / 6.983 / 4.369
- DDNN-JSU: 0.989 / 4.627 / 8.299 / 4.379
Key findings: IDR contributes the most to the ensemble by Shapley value (over 75% in 2023 in both markets); CP contributes the least. The LEAR-Ave ensemble significantly beats the DDNN-JSU neural network on the conditional predictive ability test, especially across 2021-2023 when the neural model degraded during the energy-crisis and war period.

## 4. Conformal prediction for EPF

**Dutot, Zaffran et al. (EDF R&D), "Adaptive probabilistic forecasting of French electricity spot prices", arXiv 2405.15359 (2024).**
URL: https://arxiv.org/abs/2405.15359 (html: https://arxiv.org/html/2405.15359v1)
Methods: OSSCP (online sequential split conformal), a novel OSSCP-horizon variant, Conformalized Quantile Regression (CQR), Adaptive Conformal Inference (ACI), and AgACI (parameter-free online aggregation of ACI experts). Base quantile models include linear QR, Lasso QR, quantile random forest (QRF), and quantile GAM (QGAM). French EPEX day-ahead hourly prices; train 11 Jan 2016 to 31 Dec 2018, validation 2019, test 2020-2021; nuclear-plant availability added as a predictor.
Findings: before September 2021, QRF and QGAM reached nominal coverage while linear-QR and Lasso-QR did not. After September 2021 (the price spike), every base model became invalid and intervals widened sharply. OSSCP-horizon recovers coverage toward nominal and improves interval length; AgACI online aggregation improves validity further, especially after September 2021, though it does not perfectly hit the target. The paper's conclusion is that conformalizing the base experts and then aggregating them online is the preferred pipeline.
Flag: the exact numerical coverage percentages and interval widths are presented in figures (Figures 4, 6, 7), so specific numeric coverage/width/CRPS values are not extractable from the text. The CRPS table is stated to be in Appendix A but was not extractable.

**Zaffran, Feron, Goude, Josse, Dieuleveut (2022), "Adaptive Conformal Predictions for Time Series", ICML 2022 / PMLR 162.** This is the ACI/AgACI source, demonstrated on French electricity spot prices. Referenced across the EPF conformal literature above; its exact numbers were not retrieved, flag.

**Brusaferri, Ballarino, Grossi, Laurini (2024), "On-line conformalized neural networks ensembles for probabilistic forecasting of day-ahead electricity prices", arXiv 2404.02722.**
URL: https://arxiv.org/abs/2404.02722
Method: combines DNN ensembles with online Conformalized Quantile Regression (asymmetric CP), using quantile-tracking and coverage-error integration to handle the non-exchangeable, non-stationary electricity setting. Datasets: German market (1 Jan 2015 to 31 Dec 2020, test from 27 June 2019) and six Italian bidding zones (test from 31 Aug 2018).
Flag: the provided extract did not expose a consolidated CRPS (EUR/MWh) table or exact nominal-versus-achieved coverage numbers.

**Kath & Ziel** conformal-prediction EPF work (widely cited, e.g. "Conformal prediction interval estimation and applications to day-ahead and intraday power markets", IJF 2021) is referenced by the field, but its exact coverage/width numbers were not retrieved; flag.

## 5. Typical CRPS levels on EU day-ahead markets

CRPS depends strongly on price regime, so a single "good" number is misleading without a year attached. Concrete values from the sources above (all EUR/MWh, aggregate mean CRPS):

German day-ahead (BZN|DE-LU), best-in-class models:
- Calm 2020: about 1.31 to 1.35 (LEAR-Ave 1.310; LEAR-QRM 1.350). A CRPS near 1.3-1.4 is "good" for a calm German year.
- 2021: about 3.97 to 4.19.
- Crisis 2022: about 10.2 to 10.7 (LEAR-Ave 10.199).
- 2023: about 4.2 to 4.4 (LEAR-Ave 4.215).
- 2024: about 7.48 (iQRA), reflecting elevated volatility.
Source: IDR paper and iQRA paper (below).

Spanish day-ahead (BZN|ES): 2020 about 0.94; 2022 about 6.98 to 8.30; 2023 about 4.37. Source: IDR paper.

Reference point on a whole multi-year window: the Smoothing-QRA paper (arXiv 2302.00411) reports the Aggregate Pinball Score across 99 quantiles (its CRPS proxy) averaged over 29 June 2017 to 31 Dec 2023 as roughly 5.78 to 5.87 on EPEX (best method SQRF at 5.782) and 3.68 to 3.73 on the Spanish OMIE market (SQRF 3.679). URL: https://arxiv.org/html/2302.00411v3. Note this window blends the calm and crisis regimes, so the average sits well above a calm-year number.

Bottom line for "good German day-ahead CRPS now": in a normal-volatility year expect leading models around 4 to 5 (as in 2023), and around 1.3 to 1.6 in a genuinely calm year like 2020. In a high-volatility year (2022 crisis, 2024) CRPS runs from roughly 7 up to 10 or more. French numeric CRPS: not confirmed from the fetched source; flag.

## 6. Wroclaw group (Weron / Marcjasz / Ziel / Uniejewski / Lipiecki / Serafin) EPF output, 2023-2026

Compiled from Weron's RePEc author listing (https://ideas.repec.org/e/pwe42.html); the group page https://p.wz.pwr.edu.pl/~weron.rafal/Publ failed on a TLS certificate error, flag.

2023
- Marcjasz, Narajewski, Weron, Ziel, "Distributional neural networks for electricity price forecasting", Energy Economics 125, 106843. DDNN with Normal/JSU probability layer; >7% CRPS, 8% profit over LEAR-QRA and DNN-QRA. (Section 2.)
- Nitka & Weron, "Combining predictive distributions of electricity prices. Does minimizing the CRPS lead to optimal decisions in day-ahead bidding?", Operations Research and Decisions 33(3). arXiv 2308.15443. Finding: minimizing CRPS is not always aligned with optimal trading decisions; the loss you optimize should match the downstream decision.
- Olivares, Challu, Marcjasz, Dubrawski et al., "Neural basis expansion analysis with exogenous variables: Forecasting electricity prices with NBEATSx", International Journal of Forecasting 39(2), 884-900.

2024
- Lipiecki, Uniejewski, Weron, "Postprocessing of point predictions ... isotonic distributional regression", Energy Economics 139. IDR beats QRA and CP; three-method ensemble beats DDNN-JSU. (Section 3.)

2025
- Lipiecki & Uniejewski, "Isotonic Quantile Regression Averaging for uncertainty quantification of electricity price forecasts", arXiv 2507.15079 (20 Jul 2025). iQRA enforces stochastic-order constraints on QRA by keeping regression coefficients nonnegative, dropping the Lasso tuning step. German data 8 Jan 2015 to 31 Dec 2024, test 2020-2024. CRPS (2020/2021/2022/2023/2024): iQRA 1.521 / 4.225 / 11.014 / 5.134 / 7.482; QRA 1.633 / 4.705 / 11.763 / 5.396 / 7.782; IDR 1.582 / 4.681 / 11.428 / 5.023 / 7.779; LQRA 1.521 / 4.219 / 11.003 / 5.103 / 7.492. iQRA is statistically tied with tuned LQRA and significantly beats plain QRA, IDR, CP and QRM, at lower computational cost. URL: https://arxiv.org/abs/2507.15079.
- Serafin & Weron, "Loss functions in regression models: Impact on profits and risk in day-ahead electricity trading", Energy Economics 148(C).
- Chec, Uniejewski, Weron, "Extrapolating the long-term seasonal component of electricity prices for forecasting in the day-ahead market", Journal of Commodity Markets 37(C).
- Chen, Lerch, Schienle, Serafin (with Weron group), "Probabilistic intraday electricity price forecasting using generative machine learning", WORMS 25/05.
- Lipiecki, Bilinska, Kourentzes, Weron, "Stealing accuracy: Predicting day-ahead electricity prices with Temporal Hierarchy Forecasting (THieF)", arXiv 2508.11372 / WORMS 25/06.
- Lipiecki & Weron, "PostForecasts.jl: A Julia package for probabilistic forecasting by postprocessing point predictions", WORMS 25/02. Software implementing QRA, CP, IDR post-processing.

2026
- Chec, Uniejewski, Weron, "From biased point forecasts of electricity demand to accurate predictive distributions: Using LASSO and GAMLSS", WORMS 26/01.

Group trajectory in one line: they moved from QRA and Factor-QRA (2015-2018), to distributional neural networks with the JSU parameterization (2023), then found that simple LEAR point forecasts post-processed by IDR and averaged beat the neural model through the crisis (2024), and are now refining the averaging itself (isotonic QRA, temporal-hierarchy reconciliation, GAMLSS) and moving into intraday and generative methods (2025-2026).

## Verification flags summary
- Original DDNN paper's own absolute CRPS in EUR/MWh: not confirmed (relative >7% and 8% confirmed). Absolute DDNN-JSU anchors taken from downstream re-runs.
- French conformal paper (2405.15359): exact coverage %, interval widths, and CRPS are in figures, not extracted.
- Brusaferri et al. conformalized-ensembles (2404.02722): no consolidated CRPS/coverage table extracted.
- Zaffran et al. ICML 2022 and Kath & Ziel: exact numbers not fetched.
- GEFCom2014 price-track headline pinball value: not extracted; note the winner was Team Tololo's quantile-GAM-plus-aggregation, with QRA a top performer rather than the sole winner.
- Group publication list drawn from RePEc because the Wroclaw group page returned a TLS certificate error.
