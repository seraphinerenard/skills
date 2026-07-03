# Sources

Two tiers. Tier 1 claims were verified against the listed URL on the
access date, by the researcher fact sheets in `research/` or by
direct search on 2026-07-12. Tier 2 claims are canonical citations carried
from training knowledge; the papers are real and load-bearing details are
stated conservatively in the skill, and any consultant quoting an exact
figure from a Tier 2 source should open the paper first.

## Tier 1, fetch-verified (accessed 2026-07-12)

Field experiment lifts:

- Caro and Gallien, "Clearance Pricing Optimization for a Fast-Fashion
  Retailer", Operations Research 60(6), 2012. Zara clearance experiment in
  all Belgian and Irish stores, 2008 fall-winter season; clearance
  revenues up about 6%. https://pubsonline.informs.org/doi/10.1287/opre.1120.1102
  and http://personal.anderson.ucla.edu/felipe.caro/papers/pdf_FC15.pdf
- Ferreira, Lee, Simchi-Levi, "Analytics for an Online Retailer: Demand
  Forecasting and Price Optimization", M&SOM (published online 2015). Rue
  La La field experiment: test-group revenue up about 9.7%, 90% CI 2.3% to
  17.8%. https://dspace.mit.edu/bitstream/handle/1721.1/101783/Analytics%20for%20an%20Online%20Retailer%20-%20Demand%20Forecasting%20and%20Price%20Optimization%20at%20Rue%20La%20La.pdf

Pocket-price waterfall:

- Marn and Rosiello, "Managing Price, Gaining Profit", Harvard Business
  Review, September-October 1992. Waterfall and pocket-price band; cases:
  3% average price gain producing +35% operating profit (industrial
  equipment), 2.5% producing about +30% (consumer durables).
  https://hbr.org/1992/09/managing-price-gaining-profit and
  https://pages.charlotte.edu/wp-content/uploads/sites/868/2014/12/ManagingPrice.pdf

Robinson-Patman revival:

- FTC v. Southern Glazer's Wine and Spirits, filed 2024-12-12; motion to
  dismiss denied April 2025; parties moved to settlement talks and the FTC
  concluded the case in 2026.
  https://www.ftc.gov/legal-library/browse/cases-proceedings/2110155-southern-glazers-wine-spirits-llc-ftc-v
  with status coverage at
  https://www.wiggin.com/publication/federal-judge-allows-ftcs-robinson-patman-act-suit-against-southern-glazers-wine-and-spirits-to-continue-beyond-motion-to-dismiss-stage/
  and https://globalcompetitionreview.com/gcr-usa/article/ftc-concludes-remaining-robinson-patman-case

Tooling status (full detail and URLs in `research/pymc-elasticity-tooling.md`):

- PyMC 6.1.0 (2026-07-07) and the 6.0.0 break (PyTensor 3, numba default,
  nutpie default NUTS when installed, ArviZ 1.0 DataTree).
  https://pypi.org/project/pymc/
- nutpie 0.16.11 (2026-06-30); reported about 2x Stan on posteriordb.
  https://pypi.org/project/nutpie/ and https://pymc-devs.github.io/nutpie/
- GPU/JAX crossover near 50,000 observations, PyMC Labs benchmark.
  https://www.pymc-labs.com/blog-posts/pymc-stan-benchmark
- pymc-marketing 0.19.4 scope: MMM, CLV, choice; no pricing module.
  https://github.com/pymc-labs/pymc-marketing
- Orduz, "Hierarchical Pricing Elasticity Models" (87 SKUs, 33 categories,
  NumPyro SVI). https://juanitorduz.github.io/elasticities/ (the "5,000
  SKU" version of this citation circulating in search summaries is
  fabricated; the fact sheet documents the correction)

Retail pricing vendors (full detail in
`research/pricing-vendors-cluster-a.md`):

- Revionics methods (Bayesian hierarchical demand models, TensorFlow,
  SciPy) from a 2024 technical interview.
<!-- allow:CAN optimisation appears inside the URL -->
  https://retailtechinnovationhub.com/home/2024/5/28/demand-based-optimisation-at-scale-using-ai
- Farmacorp 10% year-over-year revenue growth, vendor case study.
  https://revionics.com/assets/farmacorp_casestudy_revised_9-1_oorqnO6.pdf
- No reinforcement-learning claim in production pricing by Revionics, Blue
  Yonder, or o9 in their own materials; whitepaper lift ranges (5-10%
  gross profit and similar) are vendor marketing, including the figures
  attributed to BCG, Coresight, and Bain inside vendor documents.

Regulation and failures (full detail in
`research/pricing-algorithm-failures-regulation.md`):

- RealPage: DOJ suit 2024-08-23 (M.D.N.C. 1:24-CV-00710), landlord
  defendants added 2025-01-07, DOJ settlement 2025-11-24 (own plus public
  data at runtime, pooled training data at least 12 months old, no finer
  than statewide, monitor with code access), private MDL settlements
  $141.8M. https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and
- Assad, Clark, Ershov, Xu, JPE 132(3) 2024: German retail gasoline,
  margins +9% from adoption, +28% when both duopolists adopt.
  https://www.journals.uchicago.edu/doi/10.1086/726906
- Calvano, Calzolari, Denicolo, Pastorello, AER 110(10) 2020: Q-learning
  pricers sustain supracompetitive prices without communication.
  https://www.aeaweb.org/articles?id=10.1257%2Faer.20190623
- FTC surveillance-pricing 6(b) study (orders 2024-07-23; staff findings
  2025-01-17).
  https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-surveillance-pricing-study-indicates-wide-range-personal-data-used-set-individualized-consumer
- Amazon "Project Nessie" allegations, FTC v. Amazon (W.D. Wash.), bench
  trial set 2026-10-13.
  https://techcrunch.com/2023/11/02/unredacted-ftc-suit-shows-project-nessie-price-raising-algorithm-made-amazon-1-4b/
- 2011 Amazon book repricing spiral to $23,698,655.93.
  https://www.michaeleisen.org/blog/?p=358
- Wendy's dynamic-pricing backlash, February 2024.
  https://www.axios.com/2024/02/29/wendys-surge-pricing-ai-backlash-internet

## Tier 2, canonical citations from training knowledge (not re-fetched)

- Kalyanaram and Winer, "Empirical Generalizations from Reference Price
  Research", Marketing Science 14(3), 1995. Reference-price effects and
  loss asymmetry as empirical generalizations.
- Putler, "Incorporating Reference Price Effects into a Theory of Consumer
  Choice", Marketing Science 11(3), 1992. Egg demand; loss response about
  twice gain response.
<!-- allow:CAN Modeling appears in the cited US paper title -->
- Hardie, Johnson, Fader, "Modeling Loss Aversion and Reference Dependence
  Effects on Brand Choice", Marketing Science 12(4), 1993.
- Anderson and Simester, "Effects of $9 Price Endings on Retail Sales:
  Evidence from Field Experiments", Quantitative Marketing and Economics
  1(1), 2003. Catalogue experiments; 9-endings raised demand.
- Hausman, "Valuation of New Goods under Perfect and Imperfect
  Competition", 1996 (the other-market price instrument), with the
  standard exclusion critique (common demand shocks across markets).
- Agrawal and Ferguson, "Bid-Response Models for Customised Pricing",
  Journal of Revenue and Pricing Management, 2007. Logistic bid-response
  for quote pricing.
- Phillips, "Pricing and Revenue Optimization", 2nd ed., Stanford
  University Press, 2021, and Talluri and van Ryzin, "The Theory and
  Practice of Revenue Management", 2004. Textbook grounding for the
  markdown DP and capacity shadow-price treatments.
