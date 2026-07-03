# Sources

Access date for every URL: 2026-07-12, except the uplift-practice block dated
inline. Raw researcher fact sheets sit in `research/`.

## BTYD and CLV, primary papers

- Schmittlein, Morrison and Colombo (1987), "Counting Your Customers: Who Are
  They and What Will They Do Next?", Management Science 33(1) 1-24.
  https://pubsonline.informs.org/doi/10.1287/mnsc.33.1.1
- Fader, Hardie and Lee (2005), "'Counting Your Customers' the Easy Way: An
  Alternative to the Pareto/NBD Model", Marketing Science 24(2) 275-284.
  http://brucehardie.com/papers/018/fader_et_al_mksc_05.pdf
- Fader and Hardie (2013), "The Gamma-Gamma Model of Monetary Value",
  technical note 025. http://www.brucehardie.com/notes/025/
- Hardie technical notes used for derivations and quirks: note 004 (BG/NBD
  in Excel) http://www.brucehardie.com/notes/004/, note 009 (deriving the
  Pareto/NBD) http://www.brucehardie.com/notes/009/, note 021 (computing
  P(alive) under BG/NBD) http://www.brucehardie.com/notes/021/, note 039
  (step-by-step BG/NBD derivation) http://www.brucehardie.com/notes/039/.
  Index: http://www.brucehardie.com/notes/
- Fader, Hardie and Shang (2010), "Customer-Base Analysis in a Discrete-Time
  Noncontractual Setting", Marketing Science 29(6) 1086-1108 (the BG/BB
  model). https://pubsonline.informs.org/doi/10.1287/mksc.1100.0580
- Fader and Hardie (2007), "How to Project Customer Retention", Journal of
  Interactive Marketing 21(1) 76-90 (the shifted-beta-geometric model).
  http://www.brucehardie.com/papers/021/
- Batislam, Denizel and Filiztekin (2007) MBG/NBD, discussed via
  https://repub.eur.nl/pub/38235/ERS-2013-001-LIS.pdf and
  https://www.researchgate.net/publication/313738321_New_Perspectives_on_Customer_Death_Using_a_Generalization_of_the_ParetoNBD_Model

## BTYD tooling status

- `lifetimes` archived on GitHub 2024-06-28, read-only, README points to
  PyMC-Marketing as successor; last PyPI release 0.11.3 on 2020-07-06.
  https://github.com/CamDavidsonPilon/lifetimes/blob/master/README.md ;
  https://pypi.org/project/Lifetimes/
- `pymc-marketing` CLV module: BG/NBD, Pareto/NBD, gamma-gamma, MBG/NBD and
  shifted-beta-geometric; MAP and full MCMC fitting; release 0.19.4 on
  2026-05-06, Python 3.12 to 3.14. https://www.pymc-marketing.io/en/stable/ ;
  https://pypi.org/project/pymc-marketing/ ;
  https://www.pymc-labs.com/blog-posts/pareto-nbd
- `btyd` fork archived 2024-07-21, last release 0.1b3 (2022-11-08).
  https://github.com/ColtAllen/btyd ; https://pypi.org/project/btyd/
- R: `CLVTools` active (docs updated Nov 2025; covers Pareto/NBD with
  time-varying covariates, GGom/NBD). https://www.clvtools.com/ ;
  `BTYDplus` for the literature variants (Pareto/NBD HB, Pareto/GGG).
  https://github.com/mplatzer/BTYDplus
- Fitting-hazard guidance (multiple starting points, short calibration
  windows): https://rdrr.io/cran/BTYD/man/pnbd.EstimateParameters.html ;
  https://rdrr.io/cran/BTYD/man/bgnbd.EstimateParameters.html

## Uplift modelling and evaluation (access date 2026-07-12)

- Ascarza (2018), "Retention Futility: Targeting High-Risk Customers Might Be
  Ineffective", Journal of Marketing Research 55(1) 80-98.
  https://journals.sagepub.com/doi/10.1509/jmr.16.0163 ; paper PDF:
  https://www.hbs.edu/ris/Publication%20Files/ascarza_jmr_18_783d54d4-e548-41ed-b1d7-8a180f1ae85a.pdf
- Radcliffe (2007), "Using Control Groups to Target on Predicted Lift",
  Direct Marketing Analytics Journal; Radcliffe and Surry (2011), "Real-World
  Uplift Modelling with Significance-Based Uplift Trees", Stochastic Solutions
  white paper. https://stochasticsolutions.com/pdf/sig-based-up-trees.pdf
- Gutierrez and Gerardy (2017), "Causal Inference and Uplift Modelling: A
  Review of the Literature", PMLR 67.
  http://proceedings.mlr.press/v67/gutierrez17a.html
- causalml (Uber): release 0.16.0 current on PyPI; KDD 2025 workshop shows an
  active community. https://github.com/uber/causalml ;
  https://pypi.org/project/causalml/
- econml (PyWhy): maintained; DRLearner and CausalForestDML are the
  uplift-relevant estimators. https://github.com/py-why/EconML
- scikit-uplift: last release 0.5.1 (2022); treat as dormant.
  https://pypi.org/project/scikit-uplift/

## Segmentation and cluster stability

- Hennig (2007), "Cluster-wise assessment of cluster stability",
  Computational Statistics and Data Analysis 52(1) 258-271; bootstrap Jaccard
  thresholds (below 0.6 dissolved, 0.75 valid, 0.85 highly stable);
  `fpc::clusterboot`. https://www.homepages.ucl.ac.uk/~ucakche/papers/clusta.pdf ;
  https://search.r-project.org/CRAN/refmans/fpc/html/clusterboot.html
- von Luxburg (2010), "Clustering Stability: An Overview", Foundations and
  Trends in Machine Learning 2(3). https://arxiv.org/abs/1007.1075
- Silhouette limits (bias toward convex, well-separated clusters):
  https://link.springer.com/chapter/10.1007/978-3-031-33374-3_17
- RFM as baseline plus k-means validation in current CRM practice:
  https://www.digitalapplied.com/blog/rfm-segmentation-2026-ecommerce-customer-framework ;
  https://www.researchgate.net/publication/394047969_Customer_Segmentation_Using_RFM_and_K-Means_Clustering_to_Support_CRM_in_Retail_Industry
- Segment migration tracking in CRM stacks:
  https://www.crmcarecloud.com/rfm-segmentation/ ;
  https://www.dbmarketing.com/articles/Art123.htm
- P2V-MAP basket embeddings: Gabel, Guhl and Klapper (2019), Journal of
  Marketing Research. https://journals.sagepub.com/doi/abs/10.1177/0022243719833631 ;
  code https://github.com/sbstn-gbl/p2v-map
- customer2vec on Instacart data (doc2vec, 200-dim vectors, 12 clusters by
  silhouette, near-identical aggregate profiles across clusters):
  https://www.griddynamics.com/blog/customer2vec-representation-learning-and-automl-for-customer-analytics-and-personalization
- Instacart production word2vec features:
  https://www.slideshare.net/SharathRao6/learned-embeddings-for-search-and-discovery-at-instacart

## Store segmentation and assortment localization

- RELEX store-clustering pitfalls (category-level clustering, naming, vendor
  input, 20/80 category focus):
  https://www.relexsolutions.com/resources/store-clustering-pitfalls-and-how-to-avoid-them/
- Toolio localization guidance (feature set; 5 to 10 cluster-level plans for
  about 100 stores):
  https://www.toolio.com/post/store-localization-and-clustering-best-practices-for-retail-planners
- dunnhumby AI assortment release (store-level recommendations clustered
  upward, planogram integration):
  https://www.dunnhumby.com/news/dunnhumby-unveils-ai-powered-assortment-solution-for-localised-ranging/
- Fisher and Vaidyanathan, demand estimation and assortment optimization
  (demand transference; localization lift 12.8% calibration, 7.6% validation;
  figures attributable to the paper, no line-level verification, see
  `research/store-segmentation-practice.md`):
  https://web-docs.stern.nyu.edu/old_web/emplibrary/Fisher%20%26%20Vaidyanathan%20Demand%20estimation%20and%20assortment%20optimization.pdf
- Practitioner category-uplift range for localized assortment (3% to 10%,
  vendor claim): https://www.retailtouchpoints.com/features/executive-viewpoints/5-widespread-myths-about-localized-assortment
