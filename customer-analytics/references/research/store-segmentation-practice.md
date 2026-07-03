<!-- Compiled 2026-07-12. -->

Access date for all sources: 2026-07-12.

---

# Fact sheet: store clustering & customer segmentation for assortment localization

Access date for every source below: **2026-07-12**.

## A. Store clustering for assortment — features, cluster counts, mechanics

**1. Two clustering paradigms: top-down (structural) vs bottom-up (behavioural).** Retailers cluster either on structural attributes (store size, location, format) or on actual sales/customer-behaviour data; practitioners recommend clustering at the *category* level rather than one store-wide grouping, because a small store can share a category's demand pattern with a large one.
Source: https://www.relexsolutions.com/resources/store-clustering-pitfalls-and-how-to-avoid-them/

**2. Feature set that goes into clusters.** Documented inputs: sales by category, total/weekly sales volume and velocity, store size and format, customer demographics and local shopper profiles, regional location and climate, foot traffic, and sell-through/performance trends. ML clustering is used specifically to handle "dozens of variables at once" rather than a single attribute.
Source: https://www.toolio.com/post/store-localization-and-clustering-best-practices-for-retail-planners

**3. Typical cluster count in practice: single digits (~5–10), not per-store.** A planner managing ~100 stores is described as building "5–10 cluster-level plans" rather than 100 individual plans — the practical range cited for assortment/planogram clustering.
Source: https://www.toolio.com/post/store-localization-and-clustering-best-practices-for-retail-planners

**4. How clusters feed assortment and planograms.** Clusters drive localized product mix (e.g., winter coats weighted to cold-weather clusters), category-depth variation (edgy styles only to fashion-forward clusters), and space-aware planograms. Vendor tooling (dunnhumby Assortment, 2024 AI release) generates store-specific recommendations then clusters *back up* from store level, and pairs assortment with an integrated planogram tool that enforces merchandising rules, physical constraints, and local health/safety limits.
Sources: https://www.toolio.com/post/store-localization-and-clustering-best-practices-for-retail-planners ; https://www.dunnhumby.com/news/dunnhumby-unveils-ai-powered-assortment-solution-for-localised-ranging/

**5. Which big-box/grocery names are on record localizing.** Walmart, Macy's, Best Buy, and Home Depot are cited (in the Fisher & Vaidyanathan literature) as having run efforts to vary assortment by store for local tastes — e.g., more large sizes in Iowa than Florida, more black apparel in Manhattan than Madison WI, pricier products in wealthier trade areas.
Source: https://web-docs.stern.nyu.edu/old_web/emplibrary/Fisher%20&%20Vaidyanathan%20Demand%20estimation%20and%20assortment%20optimization.pdf

## B. Named results with numbers (lift, cluster counts)

**6. Fisher & Vaidyanathan localization lift: +12.8% (calibration) / +7.6% (validation).** Their demand-estimation + assortment-optimization method, tested on snack cakes, tires, and automotive appearance chemicals in US chains, reports an incremental revenue gain of 12.8% in the calibration period and a 7.6% localization lift in the out-of-sample validation period. (Numbers as reported in search-indexed summaries of the paper; the source PDF did not render cleanly for direct page verification, so treat the exact figures as attributable to the paper but not line-verified by me.)
Sources: https://web-docs.stern.nyu.edu/old_web/emplibrary/Fisher%20&%20Vaidyanathan%20Demand%20estimation%20and%20assortment%20optimization.pdf ; paper landing: https://www.semanticscholar.org/paper/An-Algorithm-and-Demand-Estimation-Procedure-for-Fisher-Vaidyanathan/bb461bab33e7b5e14b8a879e85a2e2feabfe15fc

**7. Practitioner rule of thumb: 3%–10% category uplift from well-executed localized assortment.** Cited as a general achievable range for a well-planned/executed localized assortment strategy (vendor/consultancy-level claim, not a single audited case).
Source (search-surfaced): https://www.retailtouchpoints.com/features/executive-viewpoints/5-widespread-myths-about-localized-assortment

**8. Demand transference is the core mechanism behind assortment cuts.** When an item is deleted, a modelled fraction of its demand transfers to remaining substitutes (item i1 selling 100 units redistributes to i2/i3/i4); localized choice models estimate this substitution so assortment changes can be forecast per store/cluster before rollout.
Source: https://web-docs.stern.nyu.edu/old_web/emplibrary/Fisher%20&%20Vaidyanathan%20Demand%20estimation%20and%20assortment%20optimization.pdf

## C. Pitfalls practitioners report

**9. RELEX "5 pitfalls": (i)** clustering only top-down on store size/location instead of category behaviour; **(ii)** ignoring how categories actually perform inside stores; **(iii)** excluding vendor/supplier category expertise; **(iv)** over-analyzing every category when ~20% of categories drive ~80% of revenue (focus on strategic categories); **(v)** naming clusters with letters/numbers, which store managers read as grades and which distorts behaviour.
Source: https://www.relexsolutions.com/resources/store-clustering-pitfalls-and-how-to-avoid-them/

**10. Cluster instability and over-localization cost.** Clusters must be revisited regularly to stay relevant (implying drift/instability year over year); the central tension is balancing localization against scalability and operational/supply-chain efficiency, and multi-factor clustering forces pulling and cleaning data across sales, inventory, and CRM systems. Misattribution of stores is a named risk when clustering is driven by opinion rather than historical data.
Sources: https://www.relexsolutions.com/resources/store-clustering-pitfalls-and-how-to-avoid-them/ ; https://www.toolio.com/post/store-localization-and-clustering-best-practices-for-retail-planners

## D. Customer segmentation practice

**11. RFM remains the default baseline; unsupervised clustering is used to validate, not replace it.** Current practitioner framing: rule-based RFM establishes a trustworthy baseline, then k-means/unsupervised clustering is run to confirm (or refine) it; the two together are described as more defensible than either alone. RFM + k-means is still the dominant published pattern in 2020s retail/e-commerce CRM work.
Sources: https://www.researchgate.net/publication/394047969_Customer_Segmentation_Using_RFM_and_K-Means_Clustering_to_Support_CRM_in_Retail_Industry ; https://www.digitalapplied.com/blog/rfm-segmentation-2026-ecommerce-customer-framework

**12. Transition/migration matrices between RFM segments are a standard monitoring tool.** Practice tracks customer movement across segments between consecutive periods (New → Potential Loyalist → Loyal → Champion, or downward to At-Risk/Lost) as the key health signal; some CRM/CDP stacks store current group, previous group, and last-change timestamp per customer to fire flows on the transition itself (e.g., CareCloud visualizes RFM segment transitions). Refresh cadence is matched to purchase frequency (e-commerce weekly/bi-weekly, B2B monthly).
Sources: https://www.digitalapplied.com/blog/rfm-segmentation-2026-ecommerce-customer-framework ; https://www.crmcarecloud.com/rfm-segmentation/ ; classic reference: https://www.dbmarketing.com/articles/Art123.htm

**13. Hennig (2007), cluster-wise stability via bootstrap Jaccard.** For each cluster, resample (bootstrap/subset/jitter/noise-replacement), match to the most similar cluster in each replicate via the Jaccard coefficient, and average. Interpretation thresholds: mean Jaccard **< 0.6 = dissolved/unstable**, **0.6–0.75 = doubtful membership** (pattern may exist but point assignment unreliable), **≥ 0.75 = valid/stable**, **≥ 0.85 = highly stable**. Implemented as `clusterboot` in R package `fpc`. Published in Computational Statistics & Data Analysis 52(1): 258–271.
Sources: https://www.homepages.ucl.ac.uk/~ucakche/papers/clusta.pdf ; https://ideas.repec.org/a/eee/csdana/v52y2007i1p258-271.html ; https://search.r-project.org/CRAN/refmans/fpc/html/clusterboot.html

**14. von Luxburg (2010), "Clustering Stability: An Overview" — stability to pick k, with a caveat.** Choosing k so that clustering results are "most stable" is a popular model-selection method; the survey's key limitation is that stability can be driven by symmetry/structure of the underlying distribution rather than by the true number of clusters, so high stability does not guarantee correct k. Foundations and Trends in ML 2(3).
Sources: https://arxiv.org/abs/1007.1075 ; https://www.nowpublishers.com/article/Details/MAL-008

**15. Silhouette-based k-selection is common but limited.** Silhouette (Rousseeuw 1987) is the standard internal index for choosing k, but is a within-vs-between distance heuristic that biases toward convex/spherical, well-separated clusters and is not a stability guarantee; recent work proposes explicit stability-tradeoff internal criteria as an alternative to it.
Source: https://link.springer.com/chapter/10.1007/978-3-031-33374-3_17

## E. Basket-embedding segmentation (SVD / word2vec-style)

**16. P2V-MAP (Gabel, Guhl & Klapper, 2019, *Journal of Marketing Research*).** A word2vec-style neural language model over shopping baskets learns latent product embeddings from product co-occurrence, then t-SNE reduces them to a 2-D market-structure map that separates substitutes vs complements across large assortments; uses only checkout data, no manual attributes. Example finding: wines cluster by price tier. Code is public.
Sources: https://journals.sagepub.com/doi/abs/10.1177/0022243719833631 ; https://github.com/sbstn-gbl/p2v-map ; vendor overview: https://product2vec.com/

**17. customer2vec / doc2vec customer embeddings for segmentation (Grid Dynamics, Instacart data).** Concatenate each customer's products chronologically into a "document," run doc2vec to get **200-dimensional customer vectors**. On Instacart data, a hand-crafted baseline (155 department/aisle-frequency features) separated only 2–3 clusters under t-SNE; the doc2vec embedding produced cleaner separation with **12 clusters** chosen by silhouette. Caveat reported: aggregate department statistics across those 12 clusters were "almost identical," with differences visible only at the individual-customer level (e.g., low-calorie vs high-calorie skew) — a warning that embedding clusters can look crisp yet be hard to interpret.
Source: https://www.griddynamics.com/blog/customer2vec-representation-learning-and-automl-for-customer-analytics-and-personalization

**18. Instacart production use of word2vec basket/search embeddings.** Instacart reports word2vec features ranking among the top features for query-product and user-product matching in search and discovery, alongside LDA — evidence that basket/word2vec embeddings are used in production retail, not only in academia.
Source: https://www.slideshare.net/SharathRao6/learned-embeddings-for-search-and-discovery-at-instacart

---

### Sourcing caveats to carry into the reference doc
- The **12.8% / 7.6%** Fisher & Vaidyanathan figures (Finding 6) come from search-indexed summaries of the paper; the source PDF did not render for direct page-level verification. Treat as attributable-to-paper, not line-verified.
- The **3%–10%** category-uplift range (Finding 7) is a practitioner/consultancy claim, not a single audited case study.
- No published, named exact store-cluster count for a specific retailer turned up (e.g., "Walmart uses N clusters"); those counts appear to be proprietary. The **5–10 cluster** figure is the practical planning range from vendor guidance, not a named-retailer disclosure.
