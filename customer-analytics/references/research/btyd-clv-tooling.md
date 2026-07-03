<!-- Compiled 2026-07-12. -->

---

# Fact sheet: Python/R BTYD-CLV tooling, state as of 2026-07-12

Access date for every source below: **2026-07-12**.

## 1. `lifetimes` (CamDavidsonPilon) — archived

1. **The repo is archived and read-only.** GitHub banner: "This repository was archived by the owner on Jun 28, 2024. It is now read-only." README badge reads "Inactively Maintained" and states: "This codebase has moved to 'archived-mode'. We won't be adding new features, improvements, or even answering issues in this codebase." Source: https://github.com/CamDavidsonPilon/lifetimes/blob/master/README.md

2. **The README names one successor: PyMC-Marketing.** Quote: "A project has emerged as a successor to lifetimes, PyMC-Lab/PyMC-Marketing, please check it out!" Source: https://github.com/CamDavidsonPilon/lifetimes/blob/master/README.md

3. **Last release was 0.11.3 on 2020-07-06.** No release since. Source: https://libraries.io/pypi/Lifetimes (corroborated by PyPI project history at https://pypi.org/project/Lifetimes/)

## 2. `pymc-marketing` CLV module — the live successor

4. **Models implemented: BG/NBD, Pareto/NBD, Gamma-Gamma, Shifted-BG (discrete/contractual, i.e. shifted-beta-geometric), and Modified BG/NBD (MBG/NBD).** The Modified BG/NBD "assumes non-repeat customers are still active"; the Shifted-BG model is "for discrete-time, contractual modeling with cohorts and covariates." Source: https://www.pymc-marketing.io/en/stable/ (CLV API index) and BG/NBD notebook https://www.pymc-marketing.io/en/stable/notebooks/clv/bg_nbd.html

5. **Fitting supports both MAP and full MCMC.** The Pareto/NBD write-up states "MCMC inference … yields posterior estimates" and that "regularization via maximum a posteriori estimate significantly improves out-of-sample prediction accuracy over traditional MLE fitting." So MAP is the fast default and NUTS/MCMC is available for full posteriors. Source: https://www.pymc-labs.com/blog-posts/pareto-nbd

6. **Current release: 0.19.4, published 2026-05-06; requires Python ≥3.12 (3.12–3.14).** Source: https://pypi.org/project/pymc-marketing/

7. **Install weight: it is built on the full PyMC / PyTensor Bayesian stack** (its own description: "built on top of PyMC"), so it pulls a compiler-backed probabilistic-programming toolchain — materially heavier than `lifetimes`' numpy/scipy/pandas footprint. Source (framing): https://www.pymc-marketing.io/en/stable/. Note: PyPI did not enumerate pinned dependency versions, so the exact transitive list is not sourced here.

8. **Known-issue caveat:** the official Pareto/NBD blog post does not flag convergence or numerical difficulties — it emphasizes accessibility and MAP-over-MLE accuracy gains. Practitioner-level fitting traps for these models are covered in section 6 below (they are model-inherent, not pymc-marketing-specific). Source: https://www.pymc-labs.com/blog-posts/pareto-nbd

## 3. `btyd` (ColtAllen fork of lifetimes) — archived/transitioned

9. **The repo is archived; development moved to pymc-marketing.** Banner: "This repository was archived by the owner on Jul 21, 2024." README: "Development has transitioned to a new project repo: pymc-marketing," with a "Transitioned" status badge. Source: https://github.com/ColtAllen/btyd

10. **Last PyPI release was 0.1b3 on 2022-11-08; requires Python ≥3.8,<3.10.** Snyk/PyPI classify it as inactive. Sources: https://pypi.org/project/btyd/ and https://snyk.io/advisor/python/btyd

## 4. R ecosystem — still actively maintained

11. **`CLVTools` (bachmannpatrick) is actively maintained (docs updated Nov 2025).** Covers Pareto/NBD, Extended Pareto/NBD (time-varying covariates), BG/NBD, GGom/NBD (Gamma-Gompertz/NBD), plus the Gamma/Gamma spend model. Sources: https://cran.r-project.org/package=CLVTools and https://www.clvtools.com/

12. **`BTYDplus` (mplatzer) extends the older `BTYD` CRAN package** with NBD, MBG/NBD, BG/CNBD-k, MBG/CNBD-k, Pareto/NBD (HB — hierarchical Bayes), Pareto/NBD (Abe), and Pareto/GGG — the harder-to-implement literature variants. Source: https://github.com/mplatzer/BTYDplus

## 5. Practitioner reality, 2025–2026

13. **Consensus in current Python guides: `lifetimes` is legacy, `pymc-marketing` is the recommended active Python choice, and CLVTools is the R counterpart.** The BG/NBD + Gamma-Gamma pairing remains the production workhorse (BG/NBD for the transaction/alive process, Gamma-Gamma for monetary value); Pareto/NBD is now accessible in Python via pymc-marketing's Bayesian implementation. Sources: https://towardsdatascience.com/pymc-marketing-the-key-to-advanced-clv-customer-lifetime-value-forecasting-bc0730973c0a/ ; https://www.pymc-marketing.io/en/stable/guide/clv/clv_intro.html ; https://juanitorduz.github.io/bg_nbd_pymc/

## 6. Parameter-interpretation and fitting traps (with primary papers)

14. **BG/NBD assumes dropout can occur only immediately after a purchase**, so a customer with zero repeat purchases has had no dropout opportunity and the model returns P(alive) = 1.0 for every one-time buyer — counterintuitive. Sources: https://github.com/CamDavidsonPilon/lifetimes/issues/44 ; Reutterer lecture notes http://www.reutterer.com/notes/btyd_clv.pdf

15. **P(alive) jumps up at the moment of a purchase, then decays until the next one** (a purchase is evidence of being alive), a well-known BG/NBD saw-tooth quirk. Source: Bruce Hardie technical note 021, "Computing P(alive) Using the BG/NBD Model," http://www.brucehardie.com/notes/021/

16. **MBG/NBD (Batislam, Denizel & Filiztekin 2007) was motivated to fix this**: it adds a dropout opportunity at t=0 (right after the first purchase), so zero-repeat customers are no longer forced to P(alive)=1. Sources: Batislam et al., "Empirical validation and comparison of models for customer base analysis" (referenced in) https://repub.eur.nl/pub/38235/ERS-2013-001-LIS.pdf ; and the generalization discussed in https://www.researchgate.net/publication/313738321_New_Perspectives_on_Customer_Death_Using_a_Generalization_of_the_ParetoNBD_Model

17. **Flat/near-flat likelihood and parameter unidentifiability on short calibration windows are documented fitting hazards.** The BTYD estimation docs advise running estimation "from multiple starting points to ensure the models converge," and short calibration slices (e.g. 10% of data) tend to overfit. Sources: https://rdrr.io/cran/BTYD/man/pnbd.EstimateParameters.html and https://rdrr.io/cran/BTYD/man/bgnbd.EstimateParameters.html

### Primary papers (canonical URLs)

18. **Pareto/NBD original — Schmittlein, Morrison & Colombo (1987), "Counting Your Customers: Who Are They and What Will They Do Next?", Management Science 33(1):1–24.** Historically hard to fit due to parameter-estimation computational cost. Source: https://pubsonline.informs.org/doi/10.1287/mnsc.33.1.1

19. **BG/NBD — Fader, Hardie & Lee (2005), "'Counting Your Customers' the Easy Way: An Alternative to the Pareto/NBD Model", Marketing Science 24(2):275–284.** Paper PDF: http://brucehardie.com/papers/018/fader_et_al_mksc_05.pdf ; implementation technical note 004 (Excel): http://www.brucehardie.com/notes/004/

20. **Gamma-Gamma monetary-value note — Fader & Hardie (2013), "The Gamma-Gamma Model of Monetary Value", technical note 025.** Source: http://www.brucehardie.com/notes/025/

21. **Additional Hardie technical notes located for parameter/expression interpretation:** note 009 "Deriving the Pareto/NBD Model and Related Expressions" (http://www.brucehardie.com/notes/009/), note 012 "Deriving P(X(t)=x) Under the Pareto/NBD Model" (http://www.brucehardie.com/notes/012/), note 029 "Computing P(X(t,t+s)=x) Under the BG/NBD Model" (http://www.brucehardie.com/notes/029/), note 039 "A Step-by-Step Derivation of the BG/NBD Model" (http://www.brucehardie.com/notes/039/). Index: http://www.brucehardie.com/notes/

---

Note on one gap: pinned dependency versions for pymc-marketing could not be sourced from PyPI (the page rendered only the "built on PyMC" description), so finding 7's install-weight contrast is qualitative, not a version-level manifest.
