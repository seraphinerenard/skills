<!-- Compiled 2026-07-12. -->

All versions and dates below are verified against the live GitHub and PyPI APIs.

---

**1. Survey consensus (Roth, Sant'Anna, Bilinski & Poe, "What's Trending in DiD")**
- Fact: latest version is arXiv v3, 9 Jan 2023; published Journal of Econometrics 235(2):2218-2244 (2023). No newer revision exists. https://arxiv.org/abs/2201.01194
- What it recommends: under staggered timing and heterogeneous effects, drop plain TWFE and use a heterogeneity-robust estimator. It treats Callaway-Sant'Anna, Sun-Abraham, Borusyak-Jaravel-Spiess (BJS) imputation, de Chaisemartin-D'Haultfoeuille, and Gardner two-stage as valid alternatives that trade efficiency against which assumptions they impose, so it names no single winner. It warns that pre-trend tests are weak evidence and pushes transparency plus formal sensitivity analysis (Rambachan-Roth).
- 2024-2026 update: BJS was formally published in Review of Economic Studies 91(6):3253-3285, Nov 2024 (https://academic.oup.com/restud/article/91/6/3253/7601390). No successor survey; the consensus has stabilized around these five estimators. Judgment: the 2023 survey is still the reference synthesis.

**2. Python implementations (all dates verified via PyPI/GitHub API, 2026-07-12)**
- `pyfixest` 0.60.0 (2026-06-11; repo pushed 2026-07-12, 160 open issues, very active). Implements Sun-Abraham via `sunab`, Gardner two-stage via `did2s`, TWFE, and local projections. It does NOT implement Callaway-Sant'Anna. Judgment: trustworthy and actively maintained; it mirrors R `fixest`. Best Python choice for Sun-Abraham / did2s. https://github.com/py-econometrics/pyfixest
- `csdid` 0.4.2 (PyPI 2026-07-01; repo pushed 2026-07-02). Port of the R `did` package (CS 2021); maintainers include Sant'Anna (`pedrohcgs`). Judgment: maintained and authoritative-adjacent, but the R `did` remains the reference; no published R-parity test suite, so validate against R for high-stakes work. https://github.com/d2cml-ai/csdid
- `differences` 0.3.0 (2026-04-12). NOT abandoned — it revived in April 2026 after a gap (v0.2.0 was Dec 2023). Faithful CS `ATTgt` implementation by Bernardo Dionisi. Judgment: usable, lower activity (9 issues). https://github.com/bernardodionisi/differences
- `diff-diff` 3.7.0 (2026-07-09; created 2026-01-01, 315 stars, pushed today). New unified sklearn-style toolkit implementing CS, Sun-Abraham, BJS imputation, Gardner, Chen-Sant'Anna-Xie efficient DiD, and HonestDiD; claims benchmarking against R `did`/`fixest`/`synthdid`. Judgment: promising and the broadest single package, but only ~6 months old and unproven; the 3.x version reflects fast iteration, not maturity — cross-check against R before trusting. https://github.com/igerber/diff-diff
- `statsmodels` / `linearmodels`: no modern staggered-DiD estimators; `linearmodels` gives panel fixed effects only (manual DiD). Judgment: not suitable for staggered adoption.

**3. Pre-trend diagnostics**
- Roth 2022, "Pretest with Caution," AER: Insights 4(3):305-22 (Sept 2022): conventional pre-trend tests often have low power, and conditioning estimates on passing a pretest distorts point estimates and confidence-interval coverage, sometimes worsening bias. https://www.aeaweb.org/articles?id=10.1257/aeri.20210236
- Rambachan & Roth 2023, "A More Credible Approach to Parallel Trends," Review of Economic Studies: replaces the pass/fail pre-trend test with sensitivity/breakdown analysis under smoothness or relative-magnitude restrictions.
- Python HonestDiD: yes, one is maintained — `anzonyquispe/honestdid` v0.1.1 (2026-03-03; repo pushed 2026-07-09, 0 open issues). Judgment: real and active but young (v0.1.x); `diff-diff` also bundles HonestDiD. The R `HonestDiD` remains canonical, so verify Python output against it. https://github.com/anzonyquispe/honestdid

**4. Practitioner default in 2025-2026**
- Callaway-Sant'Anna (2021) is the de facto default in applied economics for staggered adoption. Reasons: doubly-robust group-time ATT with clean event-study aggregation, robustness to heterogeneous effects, thorough documentation, active authors, and first-class support in Stata 18 (`hdidregress`/`xthdidregress`). In Python specifically, because `pyfixest` omits CS, practitioners either run Sun-Abraham in `pyfixest` or reach CS through `csdid`/`differences`/`diff-diff` (or call R). BJS imputation is the common efficiency-minded second choice.

---

**Sources (accessed 2026-07-12)**
- https://arxiv.org/abs/2201.01194
- https://academic.oup.com/restud/article/91/6/3253/7601390
- https://www.aeaweb.org/articles?id=10.1257/aeri.20210236
- https://github.com/py-econometrics/pyfixest and https://pypi.org/project/pyfixest/
- https://github.com/d2cml-ai/csdid and https://pypi.org/project/csdid/
- https://github.com/bernardodionisi/differences and https://pypi.org/project/differences/
- https://github.com/igerber/diff-diff and https://diff-diff.readthedocs.io/en/stable/
- https://github.com/anzonyquispe/honestdid
- https://github.com/bcallaway11/did (R reference, v2.5, 2026-06-15)
