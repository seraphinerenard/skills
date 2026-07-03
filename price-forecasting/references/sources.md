# Sources

All accessed 2026-07-12 (research pass for this skill). Primary extracts
and verification flags live in the fact sheets under `research/`.

## Futures curve as forecast, and commodity risk premia

- Fama & French (1987), "Commodity Futures Prices: Some Evidence on
  Forecast Power, Premiums, and the Theory of Storage", Journal of
  Business 60(1). https://ideas.repec.org/a/ucp/jnlbus/v60y1987i1p55-73.html
- Alquist & Kilian (2010), "What Do We Learn from the Price of Crude Oil
  Futures?", Journal of Applied Econometrics 25(4).
  https://onlinelibrary.wiley.com/doi/10.1002/jae.1159
- Chinn & Coibion (2014), "The Predictive Content of Commodity Futures",
  Journal of Futures Markets. Working paper:
  https://users.ssc.wisc.edu/~mchinn/commodityfutures.pdf
- Reichsfeld & Roache (2011), IMF WP/11/254. Abstract:
  https://www.imf.org/en/publications/wp/issues/2016/12/31/do-commodity-futures-help-forecast-spot-prices-25325
  (primary PDF returned 403 during research; exact RMSE tables unverified)
- Baumeister (2014), "The Art and Science of Forecasting the Real Price of
  Oil", Bank of Canada Review, Spring 2014 (Table 1 MSPE ratios).
  https://www.bankofcanada.ca/wp-content/uploads/2014/05/boc-review-spring14-baumeister.pdf
- Ellwanger & Snudden (2023), "Forecasts of the real price of oil
  revisited: Do they beat the random walk?", Journal of Banking & Finance
  154. https://ideas.repec.org/a/eee/jbfina/v154y2023ics0378426623001619.html
- Benyo (2026), "A Reappraisal of Real-Time Forecasts of the Real Price of
  Oil", Economic Inquiry.
  https://onlinelibrary.wiley.com/doi/full/10.1111/ecin.70009
- Gorton & Rouwenhorst (2006), "Facts and Fantasies about Commodity
  Futures", FAJ 62(2). NBER PDF:
  https://www.nber.org/system/files/working_papers/w10595/w10595.pdf
- Erb & Harvey (2006), "The Strategic and Tactical Value of Commodity
  Futures", FAJ 62(2). Working paper:
  https://people.duke.edu/~charvey/Research/Working_Papers/W77_The_tactical_and.pdf
- Gorton, Hayashi & Rouwenhorst (2013), "The Fundamentals of Commodity
  Futures Returns", Review of Finance 17(1).
  https://www.nber.org/system/files/working_papers/w13249/w13249.pdf
- Bhardwaj, Gorton & Rouwenhorst (2015), "Facts and Fantasies about
  Commodity Futures Ten Years Later", NBER WP 21243.
  https://www.nber.org/system/files/working_papers/w21243/w21243.pdf
- Koijen, Moskowitz, Pedersen & Vrugt (2018), "Carry", JFE 127.
  https://w4.stern.nyu.edu/facdir/lpederse/papers/Carry.pdf

## Electricity price forecasting

- Lago, Marcjasz, De Schutter & Weron (2021), "Forecasting day-ahead
  electricity prices: A review of the state of the art", Applied Energy.
  epftoolbox: https://github.com/jeslago/epftoolbox
- Nowotarski & Weron (2015), QRA origin, Computational Statistics 30(4).
  https://link.springer.com/article/10.1007/s00180-014-0523-0
- Nowotarski & Weron (2018), probabilistic EPF review, RSER 81.
  https://ideas.repec.org/a/eee/rensus/v81y2018ip1p1548-1568.html
- Marcjasz, Narajewski, Weron & Ziel (2023), "Distributional neural
  networks for electricity price forecasting", Energy Economics 125.
  https://arxiv.org/abs/2207.02832
- Lipiecki, Uniejewski & Weron (2024), IDR post-processing, Energy
  Economics 139. https://arxiv.org/abs/2404.02270
- Lipiecki & Uniejewski (2025), isotonic QRA. https://arxiv.org/abs/2507.15079
- Dutot, Zaffran et al. (EDF, 2024), adaptive conformal EPF for France.
  https://arxiv.org/abs/2405.15359
- Olivares et al. (2023), NBEATSx, IJF 39(2).
- Data-driven merit order / residual load features:
  https://arxiv.org/abs/2501.02963
- EWI merit-order tool and 2022 crisis numbers:
  https://www.ewi.uni-koeln.de/en/news/mo-tool-2022-update/
- SDAC / EUPHEMIA and the 15-minute MTU change:
  https://www.entsoe.eu/network_codes/cacm/implementation/sdac/
- ISO-NE LMP FAQ: https://www.iso-ne.com/participate/support/faq/lmp

## Negative prices, curtailment, capture rates

- Bundesnetzagentur/SMARD German negative-hour series and 2025 figures:
  https://www.smard.de/page/en/topic-article/5892/15618 and
  https://www.bundesnetzagentur.de/SharedDocs/Pressemitteilungen/EN/2026/20260104_SMARD.html
- FfE EPEX reviews 2024/2025:
  https://www.ffe.de/en/publications/german-electricity-prices-on-epex-spot-2024/
- pv-magazine trackers (2024: 457 h; H1 2025: 389 h):
  https://www.pv-magazine.com/2025/01/06/germany-records-457-hours-of-negative-electricity-prices-in-2024/
- REsurety on CAISO negative prices (SP15 ~1,180 h in 2024):
  https://resurety.com/article-negative-prices-in-caiso/
- EIA on CAISO 2024 curtailment (3.4 TWh, 93% solar):
  https://www.eia.gov/todayinenergy/detail.php?id=65364
- Modo Energy on ERCOT 2024 prices and >8 TWh curtailment:
  https://modoenergy.com/research/en/ercot-curtailment-crisis-solar-wind-data-battery-colocated-trends-maps-texas
- Potomac Economics, 2024 ERCOT State of the Market:
  https://www.potomaceconomics.com/wp-content/uploads/2025/06/2024-State-of-the-Market-Report.pdf
- Hirth (2013), "The Market Value of Variable Renewables":
  https://neon.energy/Hirth-2013-Market-Value-Renewables-Solar-Wind-Power-Variability-Price.pdf
- S&P Global 2024 capture prices (DE solar EUR 54.64, ES EUR 45.56):
  https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/013125-deflating-capture-prices-pull-solar-wind-market-values-down-across-europe-in-2024
- Pexapark capture-factor trackers:
  https://pexapark.com/blog/european-solar-capture-factors-collapse-as-april-oversupply-triggers-wave-of-negative-prices/
- LBNL Utility-Scale Solar (CAISO $27/MWh 2023):
  https://emp.lbl.gov/publications/utility-scale-solar-2024-edition
- Bessembinder & Lemmon (2002), "Equilibrium Pricing and Optimal Hedging in
  Electricity Forward Markets", Journal of Finance 57(3).

## Lumber

- NAHB duty-timeline posts (14.54% Aug 2024; ~35% + Section 232 in 2025;
  ~24.8% signalled 2026):
  https://www.nahb.org/blog/2024/08/canadian-lumber-tariffs ,
  https://www.nahb.org/blog/2025/08/canadian-lumber-cvd-rates ,
  https://www.nahb.org/blog/2025/09/section-232-tariffs ,
  https://www.nahb.org/blog/2026/04/canadian-lumbers-duties-to-drop
- Commerce final results release:
  https://www.trade.gov/press-release/commerce-department-announces-final-results-softwood-lumber-canada-countervailing
- ResourceWise tariff explainer:
  https://www.resourcewise.com/blog/u.s.-tariffs-on-canadian-lumber-whats-happening-now-and-whats-next-april-2025-update
- CME Lumber Futures (LBR) contract specs:
  https://www.cmegroup.com/markets/agriculture/lumber-and-softs/lumber.html

## Aggregates

- Vulcan Materials Q4/FY2024 results ($21.08/ton freight-adjusted, +5-7%):
  https://ir.vulcanmaterials.com/news/news-details/2025/VULCAN-REPORTS-FOURTH-QUARTER-AND-FULL-YEAR-2024-RESULTS/default.aspx
- Martin Marietta Q1 2025 ($23.77/ton, +6.8%):
  https://www.pitandquarry.com/martin-marietta-off-to-a-strong-start-to-2025/
- Rock Products, "The 2024 Regional Pricing Puzzle" (rural delivered
  +30-40%, haul economics):
  https://rockproducts.com/2025/01/03/the-2024-regional-pricing-puzzle/

## Natural gas

- EIA 2024 hub review (Waha negative ~42% of trading days):
  https://www.eia.gov/todayinenergy/detail.php?id=64445
- NGI Waha negative-day counts and 2026 records:
  https://naturalgasintel.com/news/is-waha-natural-gas-on-pace-to-shatter-annual-record-for-negative-prices/
- RBN on Permian takeaway and Matterhorn:
  https://rbnenergy.com/daily-posts/analyst-insight/new-low-reached-permian-natural-gas-prices

## FX pass-through

- Campa & Goldberg (2005), "Exchange Rate Pass-Through into Import
  Prices", Review of Economics and Statistics 87(4) (OECD averages ~0.46
  short run, ~0.64 long run).
- Gopinath et al., dominant currency pricing literature (low short-run
  pass-through for dollar-invoiced trade).

## Tooling (verified by running, 2026-07-12)

- statsmodels 0.14.6, arch 8.0.0, numpy 2.5.1, pandas 3.0.3 on Python
  3.14.3: all six asset modules compile and their demos run; coint_johansen
  emits a benign ComplexWarning under numpy 2.x; the arch simulation
  forecast API returns paths at forecast.simulations.values with shape
  (n_origins, n_sims, horizon).
