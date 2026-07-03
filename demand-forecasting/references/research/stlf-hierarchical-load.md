<!-- Compiled 2026-07-12. -->

---

# DEMAND-FORECASTING RESEARCH FINDINGS (STLF state of practice, 2024-2026)
Access date for every URL below: 2026-07-12.

Note on method: several official ISO PDFs (ERCOT, PJM, MISO) are image-based scans that text extraction could not decode. They were rendered page-by-page as images and the equations and slides read directly, so the ERCOT, PJM, and MISO details below are quoted from the actual documents, not from search snippets.

---

## TOPIC 2 - STANDARD STLF FEATURES AND OPERATIONAL SYSTEMS

### 2.1 Heating and Cooling Degree Days (HDD / CDD)

Definition (US EIA, primary): a degree day measures how far the daily mean temperature departs from a base temperature. HDD = max(0, T_base − T_mean); CDD = max(0, T_mean − T_base), summed over the period. The standard US base temperature is 65 F (about 18.3 C), chosen as the outdoor temperature at which buildings historically needed neither heating nor cooling. Example given by EIA: base 65 F, daily mean 35 F gives 30 HDD; daily mean 90 F gives 25 CDD. The annual sum of HDD or CDD is roughly proportional to seasonal heating or cooling energy.
- https://www.eia.gov/energyexplained/units-and-calculators/degree-days.php
- https://www.epa.gov/sites/default/files/2021-03/documents/heating-cooling_td.pdf (EPA technical documentation)
- Overview / base-temperature 18.33 C statement: https://www.sciencedirect.com/topics/engineering/cooling-degree-day

Use as STLF features: HDD and CDD (and their one-day lags) enter load-regression models directly as weather drivers year-round. PJM, for example, includes CDD and HDD plus one-day lags of both terms as year-round variables (see 2.5 below, PJM Equation III-4).
FLAG: the European convention of a 15.5 C base (UK) is widely used but no primary document for it is sourced here; the 65 F / 18.3 C base is the sourced figure.

### 2.2 GAMs and temperature splines - the EDF / RTE France line of work

The canonical EDF operational model is a semi-parametric Generalized Additive Model (GAM). The exact baseline structure, quoted from Obst, De Vilmarest and Goude (2021), Equation 1, is:

y_t = Σ_i Σ_j α_{i,j} · 1{DayType_t=i} · 1{DLS_t=j} + Σ_i β_i · Load1D_t · 1{DayType_t=i} + γ · Load1W_t + f1(t) + f2(ToY_t) + f3(t, Temp_t) + f4(Temp95_t) + f5(Temp99_t) + f6(TempMin99_t, TempMax99_t) + ε_t

Term meanings: DayType is day-of-week category; DLS is a daylight-saving indicator; Load1D and Load1W are lagged load at 1 day and 1 week (the day-lag interacted with day type); f1(t) is a long-term trend; f2(ToY) is a smooth of position-in-year (time of year, cyclic); f3(t, Temp) is an interaction of instant/time-of-day with temperature; Temp95 and Temp99 are exponentially smoothed temperatures with smoothing coefficients 0.95 and 0.99 that model building thermal inertia; TempMin99 and TempMax99 are smoothed daily min/max. Each nonlinear f_j is expanded on a spline basis. The models are fit in R with the mgcv package (P-IRLS; bam for large data).
- Model equation and mgcv confirmation: https://ar5iv.labs.arxiv.org/html/2009.06527 (Obst, D., De Vilmarest, J., Goude, Y., "Adaptive Methods for Short-Term Electricity Load Forecasting During COVID-19 Lockdown in France," IEEE Transactions on Power Systems, 2021)
- Spline-basis search (basis types "linear", cubic splines "cs", tensor products) and mgcv/P-IRLS: https://arxiv.org/html/2503.24019v1 (Das, Keisler, Bregere, Durand, "AutoML Algorithms for Online Generalized Additive Model Selection: Application to Electricity Demand Forecasting," arXiv 2503.24019, 2025)

Foundational and related published papers (author, title, venue, year), confirmed on Goude's own publication list at https://www.imo.universite-paris-saclay.fr/~yannig.goude/publications.html :
- Pierrot, A., Goude, Y. "Short-Term Electricity Load Forecasting With Generalized Additive Models." Proceedings of ISAP (Intelligent System Applications to Power Systems), 2011. https://www.researchgate.net/publication/260448958_Short-Term_Electricity_Load_Forecasting_With_Generalized_Additive_Models
- Goude, Y., Nedellec, R., Kong, N. "Local Short and Middle Term Electricity Load Forecasting With Semi-Parametric Additive Models." IEEE Transactions on Smart Grid, 2014 (vol 5, no 1, pp 440-446). Applies one GAM specification to each of 2260 French distribution substations (EDF R&D / ERDF). https://www.researchgate.net/publication/260449195_Local_Short_and_Middle_Term_Electricity_Load_Forecasting_With_Semi-Parametric_Additive_Models
- Wood, S. N., Goude, Y., Shaw, S. "Generalized additive models for large data sets." Journal of the Royal Statistical Society: Series C (Applied Statistics), 2015. (The bam / large-data mgcv method behind operational GAM fitting.)
- Cho, H., Goude, Y., Brossat, X., Yao, Q. "Modeling and Forecasting Daily Electricity Load Curves: A Hybrid Approach." Journal of the American Statistical Association, 2013.

### 2.3 Aggregation of experts (Gaillard / Goude line)

- Devaine, M., Gaillard, P., Goude, Y., Stoltz, G. "Forecasting electricity consumption by aggregating specialized experts." Machine Learning, 2013. Online expert-aggregation: predictions from many models are combined in a time-varying weighted sum. https://arxiv.org/pdf/1207.1965 and https://link.springer.com/article/10.1007/s10994-012-5314-7
- Gaillard, P., Goude, Y., Nedellec, R. "Additive models and robust aggregation for GEFCom2014 probabilistic electric load and electricity price forecasting." International Journal of Forecasting, 2016. This method ranked 1st on both the load and the price tracks of GEFCom2014, using a quantile GAM (quantGAM): fit a quantile additive model, generate temperature scenarios, plug them into the load model, then aggregate. http://pierre.gaillard.me/doc/GaillardGoudeNedellec2015.pdf and https://www.sciencedirect.com/science/article/abs/pii/S0169207015001545
- Goehry, B., Goude, Y., Massart, P., Poggi, J.-M. "Aggregation of Multi-Scale Experts for Bottom-Up Load Forecasting." IEEE Transactions on Smart Grid, 2019. (Bottom-up hierarchical link, see Topic 6.)

### 2.4 Humidity / Temperature-Humidity Index (THI)

THI folds relative humidity into an effective summer temperature so that muggy days read hotter for cooling load. PJM's operational THI is the cleanest primary definition (see 2.5). A study specific to ERCOT quantifies the THI-load link: "Statistical Correlation Study of Temperature Humidity Index (THI) and Load in the ERCOT System," IEEE, 2023. https://ieeexplore.ieee.org/document/10116969/
Research showing relative humidity as a warm-season driver (North Carolina utility case, June-September): https://blog.drhongtao.com/2016/03/relative-humidity-for-load-forecasting-models.html
FLAG: the "correlation rises from 0.91 to 0.96" figure comes from one research paper (Fisher-information feature selection study, https://pmc.ncbi.nlm.nih.gov/articles/PMC7512701/ ), not from an operator's methodology.

### 2.5 PJM (fully documented from the primary whitepaper)

Source: "PJM Load Forecasting Model Whitepaper," Resource Adequacy Planning Department, last updated April 27, 2016. https://www.pjm.com/-/media/DotCom/library/reports-notices/load-forecast/2016-load-forecast-whitepaper.pdf . Governing manual: PJM Manual 19 (Load Forecasting and Analysis), https://www.pjm.com/-/media/DotCom/documents/manuals/m19.pdf .

Model type and structure: a regression model with daily load as the dependent variable and independent variables covering calendar effects, weather, economics, and end-use characteristics. Estimated on history back to 1998; produces a 15-year forecast for PJM zones, Locational Deliverability Areas (LDAs), and the RTO. LDA/RTO forecasts are built bottom-up by forecasting zonal contributions and aggregating. The dependent variable is hourly metered load adjusted for "load drops" and distributed solar to yield hourly unrestricted loads.

Calendar variables: binary and "fuzzy binary" (0-to-1) indicators for day of week and month, plus fractional holiday variables whose values vary by observed day of week (worked tables for MLK, Presidents, Memorial, Labor, Good Friday, Thanksgiving, July 4th, Christmas week, New Year), a graduated "Christmas Lights" variable that ramps from the Friday after Thanksgiving to Dec 23, and a daylight-saving indicator.

Economics: sector economic indexes for Residential, Commercial, Industrial (data from Moody's Analytics), each a Cobb-Douglas-style product of normalized drivers. Quoted Equation III-1, e.g. Residential index = (Households ratio)^0.47 × (Population ratio)^0.26 × (Real Personal Income ratio)^0.27; combined into one economic index weighted by each sector's share of zonal sales (Equation III-2). Sector weights originate from a 2010 Itron forecasters survey.

Weather (quoted Equation III-3, the load-bearing definitions):
- Wind-Adjusted Temperature, also called Winter Weather Parameter (WWP): WWP = Temp − (0.5 × (Wind − 10)) if Wind > 10; WWP = Temp if Wind <= 10. Wind in MPH, Temp = dry-bulb.
- Temperature-Humidity Index (THI): THI = Temp − 0.55 × (1 − Hum) × (Temp − 58) if Temp >= 58; THI = Temp if Temp < 58. Hum = relative humidity as a fraction (100% = 1). Base is 58 F.
- These feed four-section splines for summer (May-September) and winter (January, February, December); shoulder months blend WWP and THI. In addition, CDD, HDD, and one-day lags of both are used year-round (Equation III-4).
End-use: equipment saturation and efficiency indexes for Heating, Cooling, Other, including a SEER-to-EER air-conditioner efficiency conversion. 2015 changes added granular THI/WWP treatment, an autoregressive error term, a defined weather-simulation period, and distributed-solar modelling.

### 2.6 ERCOT (long-term methodology fully documented; 2025 update)

Sources read directly: "Item 8.1: Long-Term Load Forecast Update (2025-2031) and Methodology Changes," ERCOT Board of Directors, April 7-8, 2025, https://www.ercot.com/files/docs/2025/04/07/8.1-Long-Term-Load-Forecast-Update-2025-2031-and-Methodology-Changes.pdf ; and "2025 ERCOT System Planning Long-Term Hourly Peak Demand and Energy Forecast," https://www.ercot.com/files/docs/2025/04/08/2025-LTLF-Report.pdf . Load forecast landing page: https://www.ercot.com/gridinfo/load/forecast .

Model type: an econometric model of hourly load as a function of the number of premises by customer class (residential, business, industrial) and weather variables, with historical weather drawn from 2008-2022; horizon is hourly for the next 10 years. The CDR firm-load forecast formula is defined in ERCOT Protocol Section 3.2.6.3(1); ERCOT states it "has flexibility to determine the appropriate variables to include in its econometric load forecast."

2025 waterfall / component structure (quoted): Existing Load builds up as Base Economic Forecast + Electric Vehicle Forecast + existing crypto-site load growth − rooftop photovoltaic, then adds TSP-provided large loads (executed contracts, credible third-party forecasts, and TSP officer-attested letters, the last enabled by NPRR1180 and PGRR107, PUCT-approved January 21, 2025, tracking House Bill 5066). The 2025 TSP-provided forecast reaches 218 GW by 2031, driven mainly by data centres (data-centre load for 2030 rose from 29,614 MW in the 2024 forecast to 77,965 MW in 2025).

New "ERCOT Adjusted Load Forecast" method (quoted): starting May 2025 CDR, ERCOT delays every new large load's in-service date by 180 days (actual 2022-2024 experience showed ~220-day average delay), reduces new data-centre demand to 49.8% of requested amount, and reduces officer-letter loads to 55.4%. Incorporating the higher values produced a −6.2% planning reserve margin for summer 2026 in the net peak-load hour and 5.2% in the peak-load hour.
FLAG: ERCOT's operational short-term (day-ahead / real-time) load-forecast feature set is not separately documented in these long-term planning materials; the econometric-with-premises-and-weather description above is the long-term LTLF methodology.

### 2.7 MISO (documented from the primary presentation)

Source read directly (as slide images): "Load Forecast Development and Use at MISO," IRP Conference IURC, June 6, 2024. https://www.in.gov/iurc/files/Load-Forecast-Development-and-Use-at-MISO.pdf

Operational forecasts: MISO operations use a Neural Network + Linear Regression model to forecast from one week ahead down to the next five minutes. Inputs feeding the model (quoted from the "How do we build load forecasts?" slide): live load and weather data, historic load data, Market-Participant-submitted data, day type, and a seasonal model. Output is produced, staff may manually adjust it, then it is sent to customers. The forecasting function supplies near-real-time and hourly granularity for the next 7 days, split into a "Medium Term Hourly Load and Renewable forecast" and a "Short Term 5-minute Load and Renewable forecast" that back the Forward Commitment (>16 h), Intra-day (4-16 h), Look-Ahead (<3 h), and 5-minute-market processes.

Planning-year (resource-adequacy) forecasts: originate from Load Serving Entities, not from MISO's own model; MISO reviews a sample of submitted methodologies (Tariff Module E-1, section 69A.1.1). All demand forecasts must reflect a 50% probability that demand will not exceed the forecast (P50).

### 2.8 CAISO

CAISO does not publish a load-forecast model whitepaper comparable to PJM's. Operational structure is set in the CAISO Business Practice Manual for Market Operations ( https://bpmcm.caiso.com/BPM%20Document%20Library/Market%20Operations/ ): the Day-Ahead Market needs hourly day-ahead and two-day-ahead demand forecasts; RTUC runs every 15 minutes over the current and next trading hour; STUC looks at least 3 hours ahead at 15-minute intervals; the real-time market clears at 5-minute granularity; scheduling coordinators must submit at minimum a 3-hour rolling forecast at 15-minute (or optionally 5-minute) granularity.

Weather sensitivity documented for CAISO: temperature is the dominant summer driver, with a V-shaped load-temperature curve inflecting around 60 F (load rises with temperature above ~60 F from air-conditioning, and rises more slowly below ~60 F from electric heating). During the July 2024 heat wave, CAISO's day-ahead forecast recorded 4.55% MAPE and a peak error of 3,211 MW, and commercial vendors reported materially lower error.
- CAISO 2025 Summer Loads and Resources Assessment: https://www.caiso.com/content/summer-loads-resources-assessment/2025/index.html
- Load-temperature inflection and net-load-ramp modelling: https://arxiv.org/pdf/2012.07117
- July 2024 heat-wave MAPE figures: https://www.yesenergy.com/blog/caiso-load-forecasts
FLAG: CAISO's internal short-term system-load model (algorithm and full feature list) is not published; the above is the sourced operational and weather-sensitivity picture.

### 2.9 National Grid ESO / NESO (Great Britain)

NESO (National Energy System Operator, the renamed National Grid ESO) publishes operational demand forecasts at horizons of 1 day, 2 days, 7 days, and 2-14 days, updated intraday, via its data portal.
- Data portal (day-ahead national demand forecast, published twice daily): https://www.neso.energy/data-portal/1-day-ahead-demand-forecast
- Day-ahead half-hourly forecast performance (APE, TRIAD-avoidance adjustments from April 2021): https://www.neso.energy/data-portal/day-ahead-half-hourly-demand-forecast-performance
- Peak-demand forecasting programme + literature review (WP1): https://www.neso.energy/publications and https://www.neso.energy/document/354451/download

Weather variables in the GB demand model: the temperature driver is an "effective temperature" that smooths and lags raw temperature to capture thermal inertia. A published description of the NESO model gives the recursive form TE_{i,h} = 0.5 × (TE_{i,h−24} + TO_{i,h}), where TE_{i,h−24} is the effective temperature 24 hours earlier and TO_{i,h} is the mean of the last four hours of temperature; population-weighted 10 m wind speed models the wind-chill effect on heat demand. Historical demand-data field descriptions and embedded-wind definitions are published by National Grid.
- Effective-temperature and wind description: https://arxiv.org/pdf/2604.20445 (Bhattacharya et al., "Assessing the Shortfall Risk of GB Electricity Grid using Shifts in Winter Weather Conditions") and https://arxiv.org/html/2506.04294v1
- Historic demand data field descriptions: https://www.nationalgrid.com/sites/default/files/documents/DemandData%20Field%20Descriptions_0.doc

Peak-demand / capacity-adequacy definition: the Average Cold Spell (ACS) methodology defines the 1-in-20 peak day (the daily demand level exceeded in one winter out of twenty), with ACS peak demand set as the median winter peak across the Monte Carlo simulations (about 20,000).
- ACS methodology (EMR Delivery Body): https://www.emrdeliverybody.com/Lists/Latest%20News/Attachments/189/SC4L12%20ACS%20Methodology.pdf
FLAG: no single consolidated NESO operational-STLF methodology whitepaper was located or quoted; the effective-temperature formula is sourced from academic descriptions of the NESO model plus NESO's own data-field documentation, and the 1-in-20/ACS definition from the EMR Delivery Body document.

### 2.10 Lagged load, calendar, holiday handling (cross-cutting)

Lagged load: standard practice uses previous-day and previous-week load (see the EDF GAM Load1D and Load1W terms, 2.2). Calendar: hour/time-of-day, day-of-week, month, and time-of-year (often cyclic splines), with daylight-saving indicators (EDF DLS term; PJM DLSav). Holiday handling: PJM's fractional/fuzzy holiday variables that differ by observed weekday (2.5) are a fully worked example; the French GAM literature treats public holidays and "bridge" days (jours feries / ponts) as special day types. Bridge-day and holiday handling in the French adaptive setting: https://ar5iv.labs.arxiv.org/html/2009.06527

---

## TOPIC 6 - HIERARCHICAL / SPATIAL LOAD FORECASTING

### 6.1 Forecast reconciliation theory (Hyndman line)

Primary textbook reference (Hyndman & Athanasopoulos, Forecasting: Principles and Practice, 3rd ed, chapter on reconciliation): https://otexts.com/fpp3/reconciliation.html
Structure: coherent forecasts are ỹ_h = S G ŷ_h, where S is the summing matrix encoding the hierarchy, ŷ_h are independent base forecasts, and G maps base forecasts to the bottom level. Traditional G choices give bottom-up (G selects the bottom level), top-down (disaggregate the top by proportions, which is biased), and middle-out.
Optimal reconciliation (MinT): G = (S' W_h^{-1} S)^{-1} S' W_h^{-1}, so ỹ_h = S (S' W_h^{-1} S)^{-1} S' W_h^{-1} ŷ_h, minimizing the trace of the coherent-forecast error covariance under unbiasedness. Covariance-estimator options: OLS (W = kI), WLS-variance (diagonal of residual variances), WLS-structural (diagonal from S·1, for judgmental forecasts), MinT-sample (full sample covariance), MinT-shrinkage (shrink sample covariance toward its diagonal when series outnumber observations).
Primary paper: Wickramasuriya, S. L., Athanasopoulos, G., Hyndman, R. J. "Optimal forecast reconciliation for hierarchical and grouped time series through trace minimization." Journal of the American Statistical Association, vol 114, no 526, pp 804-819, 2019. https://robjhyndman.com/publications/mint/ and PDF https://robjhyndman.com/papers/mint.pdf
Review: Athanasopoulos, Hyndman et al., "Forecast reconciliation: A review." https://robjhyndman.com/papers/hf_review.pdf

### 6.2 Feeder- and substation-level (distribution) load forecasting

- Goude, Nedellec, Kong (2014, IEEE Transactions on Smart Grid) fit one GAM specification locally to each of 2260 French distribution substations, the reference example of substation-level GAM forecasting (see 2.2).
- Mogos et al., "Hierarchical Load Forecast Aggregation for Distribution Transformers Using Minimum Trace Optimal Reconciliation and AMI Data," IEEE (Access/journal, 2023). Hong Kong Polytechnic University. Hierarchy per distribution transformer: individual single-phase customers (bottom), per-phase load (middle), three-phase total (top). Base forecasts by ARIMA; reconciled with MinT-sample (MinTSa) for small networks and MinT-shrinkage (MinTSh) for large networks using AMI smart-meter data; MinT-shrink generally improves accuracy at all levels and horizons. https://ieeexplore.ieee.org/document/10233865/ and PDF https://ira.lib.polyu.edu.hk/bitstream/10397/109652/1/Mogos_Hierarchical_Load_Forecast.pdf

### 6.3 Spatial load forecasting for distribution planning (Willis)

- Willis, H. Lee. "Spatial Electric Load Forecasting." Book, 2nd edition, CRC Press / Marcel Dekker, 2002 (1st edition 1996). Surveys small-area forecasting methods for T&D planning: trending, simulation, and land-use / multivariate approaches, weather normalization, and the effect of small-area forecast error on distribution planning. https://books.google.com/books/about/Spatial_Electric_Load_Forecasting.html?id=_2HL-vs8HPgC and https://www.amazon.com/Spatial-Electric-Forecasting-Engineering-Willis/dp/0824708407 (ISBN 9780824708405)
- Foundational tutorial: Willis, H. L., Northcote-Green, J. E. D. "Spatial electric load forecasting: A tutorial review." Proceedings of the IEEE, vol 71, no 2, pp 232-253, 1983. Introduces two-dimensional signal theory as a common framework for small-area load, growth, and forecast error. https://ieeexplore.ieee.org/document/1456830/
FLAG: the 2nd-edition ISBN and publisher are confirmed; the exact 2nd-edition year (2002) is from retailer/library metadata rather than a primary Library-of-Congress record.

### 6.4 Hierarchical / probabilistic load reconciliation papers

Established:
- Ben Taieb, S., Taylor, J. W., Hyndman, R. J. "Hierarchical Probabilistic Forecasting of Electricity Demand With Smart Meter Data." Journal of the American Statistical Association, vol 116, no 533, pp 27-43, 2021. Produces coherent probability-density forecasts across a smart-meter -> substation -> city -> region hierarchy (aggregate distribution equals the convolution of disaggregate distributions). https://robjhyndman.com/publications/hpf-electricity/ ; code https://github.com/bsouhaib/prob-hts
- Bregere, M., Huard, M. "Online hierarchical forecasting for power consumption data." International Journal of Forecasting, vol 38, no 1, pp 339-351, 2022. Three steps: GAM benchmark forecasts, online expert-aggregation of benchmarks per series, then projection onto the coherent subspace. https://hal.science/hal-03884826/document and https://arxiv.org/abs/2003.00585

2024-2026 papers:
- Antoniadis, A., Gaucher, S., Goude, Y. "Hierarchical transfer learning with applications to electricity load forecasting." International Journal of Forecasting, vol 40, no 2, pp 641-660, 2024. Two hierarchical transfer-learning methods stacking GAMs and random forests (GAM-RF), plus hierarchical adaptations of online expert-aggregation with quantile GAM-RF experts. https://ideas.repec.org/a/eee/intfor/v40y2024i2p641-660.html
- "An Evaluation of Direct and Indirect Strategies for Hierarchical Net-Load Forecasting." ITEGAM-JETIA, published 2026. Feeder-level hourly load 2022-2024 with solar PV; compares direct net-load forecasting against indirect (gross load and generation separately); direct is statistically more accurate across the hierarchy but carries over-forecasting bias. https://itegam-jetia.org/journal/index.php/jetia/article/view/3015
- "Scalable forecast reconciliation through (un)guided Sub-hierarchies." Journal of the Operational Research Society, online December 12, 2025. Breaks a large hierarchy into sub-hierarchies so any point or probabilistic reconciliation method applies efficiently at scale. https://www.tandfonline.com/doi/full/10.1080/01605682.2025.2599394
- "Conformal Prediction for Hierarchical Data." arXiv 2411.13479, 2024 (distribution-free coherent prediction intervals over a hierarchy). https://arxiv.org/pdf/2411.13479
- "Extending Load Forecasting from Zonal Aggregates to Individual Nodes for Transmission System Operators." arXiv 2510.14983, 2025 (node-level TSO forecasting with hierarchical structure). https://arxiv.org/html/2510.14983v1
FLAG: author names for the ITEGAM-JETIA net-load paper were not shown in the search excerpts, and the full article was not opened to confirm them.

---

## KEY UNVERIFIED ITEMS (consolidated)
1. European HDD/CDD base of 15.5 C (UK): commonly cited, not sourced here; the 65 F / 18.3 C base is sourced (EIA/EPA).
2. NESO: no single consolidated operational-STLF methodology whitepaper was located; effective-temperature formula is from academic descriptions of the NESO model plus NESO data-field docs; ACS 1-in-20 from the EMR Delivery Body doc.
3. ERCOT operational (day-ahead/real-time) STLF feature set is not documented in the long-term planning materials consulted; the econometric-premises-and-weather description is the long-term LTLF methodology.
4. CAISO internal short-term system-load model algorithm and full feature list are not published; only operational cadence and weather sensitivity are sourced.
5. Willis 2nd-edition year (2002) is from retailer/library metadata, not a primary record.
6. THI improvement statistics (correlation 0.91 to 0.96) come from one research paper, not an operator methodology.
