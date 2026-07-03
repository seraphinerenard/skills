# Sources

Two tiers. Tier 1 entries were verified on the access date shown (fetched directly or through search-result cross-checks on that date). Tier 2 entries are canonical literature cited from the published record; the URLs are publisher landing pages supplied for convenience and were not re-fetched on 2026-07-12. The MEIO vendor claims carry their own source list inside [research/meio-practice.md](research/meio-practice.md); the load-bearing ones are repeated here.

## Tier 1, verified 2026-07-12

Solvers and benchmarks:

- Mittelmann optimization benchmarks (Gurobi withdrew August 2024; MindOpt December 2024; HiGHS and COPT remain posted), https://plato.asu.edu/bench.html, accessed 2026-07-12
- Gurobi statement on its Mittelmann-benchmark participation, https://www.gurobi.com/resources/update-on-gurobi-participation-in-mittelmann-benchmarks/, accessed 2026-07-12
- Gurobi 13.0 release (November 2025; PDHG with GPU support, faster MIP/MINLP), https://www.gurobi.com/news/gurobi-releases-version-13-0-with-improved-performance-and-new-solving-capabilities/, accessed 2026-07-12
- Gurobi 12.0 release (November 2024), https://www.gurobi.com/news/gurobi-12-0-brings-new-performance-improvements-innovative-nonlinear-capabilities-and-smarter-resource-management/, accessed 2026-07-12
- HiGHS releases (1.11.0 dated June 6, 2025; later releases through 2026 visible on the page), https://github.com/ERGO-Code/HiGHS/releases, accessed 2026-07-12
- HiGHS project page and licence (MIT), https://highs.dev/, accessed 2026-07-12
- highspy on PyPI, https://pypi.org/project/highspy/, accessed 2026-07-12
- HiGHS in SciPy (linprog from 1.6.0, milp from 1.9.0), https://en.wikipedia.org/wiki/HiGHS_optimization_solver, accessed 2026-07-12
- HiGHS R package on CRAN (maintenance activity dated June 2026), https://cran.r-project.org/web/packages/highs/highs.pdf, accessed 2026-07-12

Lumber and sawmill practice:

- USNR CSS optimizer (real-time curve-sawing optimization and grade classification), https://internationalforestindustries.com/2024/11/20/usnr-the-new-css-features-the-latest-in-optimization-and-controls/, accessed 2026-07-12
- USNR trimmer optimizer product page, https://www.usnr.com/en/product/nsstrimmeropt, accessed 2026-07-12
- Optitek sawmill simulator (FPInnovations; mill modelling and monitoring use), https://library.fpinnovations.ca/en/permalink/fpipub39105, accessed 2026-07-12
- Optitek simulator description (log breakdown simulation), https://www.researchgate.net/figure/Optitek-simulator-FPInnovations_fig2_230668094, accessed 2026-07-12

Multi-echelon inventory practice (full list in research/meio-practice.md, all accessed 2026-07-12):

<!-- allow:B9 guaranteed-service appears in the cited title -->
- Eruguz, Sahin, Jemai, Dallery 2016, survey of guaranteed-service models (IJPE 172, 110-125), https://www.sciencedirect.com/science/article/abs/pii/S0925527315005162
- Graves-Willems lineage and Optiant acquisition by Logility, https://www.supplychainbrain.com/articles/7493-logility-acquires-optiant-inventory-optimization-vendor
<!-- allow:CAN help-center is part of the URL -->
- Optilogic Cyclo documentation (verbatim GSM statement), https://optilogic.com/resources/help-center/docs/getting-started-with-cyclo-multi-echelon-inventory-optimization
- Callioni, Billington et al. 2004, Hewlett-Packard supply-chain profitability (Interfaces 34(1), 59-72; savings above $130 million), https://pubsonline.informs.org/doi/10.1287/inte.0103.0054
<!-- allow:B9 guaranteed-service comparison is the cited subject -->
- De Smet, Aghezzaf, Desmet 2019, guaranteed- against stochastic-service comparison (IJPR 57(13), 4148-4165), https://www.tandfonline.com/doi/abs/10.1080/00207543.2018.1518606
- Achkar et al. 2024, GSM extensions for industrial MEIO (EJOR 313(1); Gartner 2016 benefit figures cited within), https://arxiv.org/pdf/2306.10961
- Arkieva on MEIO adoption and incentive conflicts (13% figure; vendor blog, no disclosed survey), https://blog.arkieva.com/multi-echelon-inventory-optimization-challenges-solutions/
- Sophus MEIO guide (30 to 40% adoption estimate; vendor blog, no disclosed survey), https://sophus.ai/multi-echelon-inventory-optimization-guide/
- ToolsGroup SO99+ (probabilistic engine), https://www.toolsgroup.com/product/so99/
- Kinaxis probabilistic MEIO by Wahupa, https://www.kinaxis.com/en/solutions/applications/probabilistic-meio-wahupa
- Willems 2008, data set of 38 real multi-echelon chains (MSOM 10(1), 19-23), https://pubsonline.informs.org/doi/10.1287/msom.1070.0176
- Morrice and Valdez 2005, discrete-event simulation at Freescale (WSC 2005), https://informs-sim.org/wsc05papers/212.pdf
- Lokad on normal-distribution safety stock failure, https://www.lokad.com/tv/2019/1/9/why-safety-stock-is-unsafe/

## Tier 2, canonical literature from the published record

Formulations and integer programming:

- Gilmore, P.C., and R.E. Gomory. A linear programming approach to the cutting-stock problem. Operations Research 9(6), 1961, 849-859; Part II, Operations Research 11(6), 1963. https://pubsonline.informs.org/doi/10.1287/opre.9.6.849
- Dantzig, G.B. A comment on Edie's "Traffic delays at toll booths" (origin of set-covering shift scheduling). Operations Research 2(3), 1954, 339-341. https://pubsonline.informs.org/doi/10.1287/opre.2.3.339
- Krarup, J., and O. Bilde. Plant location, set covering and economic lot size: an O(mn) algorithm for structured problems (tight reformulation of uncapacitated lot sizing). Numerische Methoden bei Optimierungsaufgaben 3, 1977.
- Pochet, Y., and L.A. Wolsey. Production Planning by Mixed Integer Programming. Springer, 2006 (lot-sizing formulations, (l,S) inequalities, formulation strength). https://link.springer.com/book/10.1007/0-387-33477-7

Inventory:

<!-- allow:B9 guaranteed-service appears in the cited title -->
- Simpson, K.F. In-process inventories (guaranteed-service base model). Operations Research 6(6), 1958, 863-873. https://pubsonline.informs.org/doi/10.1287/opre.6.6.863
- Clark, A.J., and H. Scarf. Optimal policies for a multi-echelon inventory problem. Management Science 6(4), 1960, 475-490. https://pubsonline.informs.org/doi/10.1287/mnsc.6.4.475
- Graves, S.C., and S.P. Willems. Optimizing strategic safety stock placement in supply chains. Manufacturing & Service Operations Management 2(1), 2000, 68-83. https://pubsonline.informs.org/doi/10.1287/msom.2.1.68.23267
- Silver, E.A., D.F. Pyke, and D.J. Thomas. Inventory and Production Management in Supply Chains, 4th ed. CRC Press, 2016 (base stock, (s,S), service-level semantics).

Uncertainty:

- Birge, J.R., and F. Louveaux. Introduction to Stochastic Programming, 2nd ed. Springer, 2011 (two-stage structure, EVPI, VSS). https://link.springer.com/book/10.1007/978-1-4614-0237-4
- Kleywegt, A.J., A. Shapiro, and T. Homem-de-Mello. The sample average approximation method for stochastic discrete optimization. SIAM Journal on Optimization 12(2), 2002, 479-502. https://epubs.siam.org/doi/10.1137/S1052623499363220
- Dupacova, J., N. Groewe-Kuska, and W. Roemisch. Scenario reduction in stochastic programming: an approach using probability metrics. Mathematical Programming 95, 2003, 493-511. https://link.springer.com/article/10.1007/s10107-002-0331-0
- Heitsch, H., and W. Roemisch. Scenario reduction algorithms in stochastic programming. Computational Optimization and Applications 24, 2003, 187-206. https://link.springer.com/article/10.1023/A:1021805924152
- Bertsimas, D., and M. Sim. The price of robustness. Operations Research 52(1), 2004, 35-53. https://pubsonline.informs.org/doi/10.1287/opre.1030.0065 <!-- allow:C1 robustness is the paper's title -->
- Mohajerin Esfahani, P., and D. Kuhn. Data-driven distributionally robust optimization using the Wasserstein metric. Mathematical Programming 171, 2018, 115-166. https://link.springer.com/article/10.1007/s10107-017-1172-1 <!-- allow:C1 robust optimization term of art in the paper title -->
- Knueven, B., et al. A parallel hub-and-spoke system for large-scale scenario-based optimization under uncertainty (mpi-sppy). Mathematical Programming Computation, 2023. https://link.springer.com/article/10.1007/s12532-023-00247-3
- Dowson, O., and L. Kapelevich. SDDP.jl: a Julia package for stochastic dual dynamic programming. INFORMS Journal on Computing 33(1), 2021, 27-33. https://pubsonline.informs.org/doi/10.1287/ijoc.2020.0987
- RSOME documentation (robust and distributionally robust modelling in Python), https://xiongpengnus.github.io/rsome/ <!-- allow:C1 robust optimization term of art -->

Lumber planning literature:

<!-- allow:CAN Wood and Fiber Science is the journal name -->
- Maness, T.C., and D.M. Adams. The combined optimization of log bucking and sawing strategies. Wood and Fiber Science 23(2), 1991, 296-314.
- Kazemi Zanjani, M., M. Nourelfath, and D. Ait-Kadi. A multi-stage stochastic programming approach for production planning with uncertainty in the quality of raw materials and demand. International Journal of Production Research 48(16), 2010, 4701-4723. https://www.tandfonline.com/doi/abs/10.1080/00207540903055727

Forecast-to-decision pipelines:

- Salinas, D., V. Flunkert, J. Gasthaus, and T. Januschowski. DeepAR: probabilistic forecasting with autoregressive recurrent networks. International Journal of Forecasting 36(3), 2020, 1181-1191 (quantile forecasts as decision inputs). https://www.sciencedirect.com/science/article/pii/S0169207019301888
- Madeka, D., et al. Deep inventory management. arXiv:2210.03137, 2022 (Amazon buying decisions driven by learned demand distributions). https://arxiv.org/abs/2210.03137
