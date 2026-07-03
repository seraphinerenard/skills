<!-- Compiled 2026-07-12. -->

All facts below carry their source URL and access date 2026-07-12. Where automated retrieval normalized a release year to 2024, the value is cross-checked against PyPI (authoritative) and flagged.

---

# PyMC status, mid-2026 — Bayesian hierarchical elasticity estimation

## 1. PyMC version (as of 2026-07-12)

- Latest release: **PyMC 6.1.0, uploaded July 7, 2026** on PyPI. Requires **Python >=3.12**; built on PyTensor. (https://pypi.org/project/pymc/, accessed 2026-07-12)
- Release sequence from PyPI history: 5.28.4 (Apr 7, 2026) → 5.28.5 (May 1, 2026) → **6.0.0 (May 13, 2026)** → 6.0.1 (May 20, 2026) → **6.1.0 (Jul 7, 2026)**. (https://pypi.org/project/pymc/, accessed 2026-07-12)
- **6.0.0 is the major-version break** (the fetched GitHub release page rendered the year as "2024", but PyPI authoritatively dates the same version May 13, **2026**, and the whole 5.28.x→6.x sequence is internally consistent for 2026). Major 6.0.0 changes (https://github.com/pymc-devs/pymc/releases/tag/v6.0.0, accessed 2026-07-12):
  - Depends on **PyTensor 3.0**; **default backend is now numba** (revert with `pytensor.config.linker = "cvm"`).
  - **Nutpie became the default NUTS sampler when installed** (`pip install pymc[nutpie]`); nutpie default tuning = 400 steps vs PyMC NUTS 1000.
  - **PyMC is now safely pip-installable.**
  - **ArviZ 1.0 integration**: `arviz.InferenceData` replaced by `xarray.DataTree`; `plot_trace` → `plot_trace_dist`; default credible interval changed from 0.94 HDI to **0.89 equal-tailed interval**.
  - Removed several deprecated functions from the root namespace; overhauled `sample_posterior_predictive` (new `sample_vars`/`freeze_vars`).
- 6.1.0 adds PyTensor 3.1 compatibility, deprecates `DensityDist` in favour of `CustomDist`, and adds deterministics extract/reinsert helpers. (https://pypi.org/project/pymc/, accessed 2026-07-12)
- "Nutpie by default" is **conditional**, tracked in PyMC issue #8079 (opened Jan 30, 2026; closed via PR #8248; v6 milestone). Conditions: all variables continuous/differentiable, no custom step samplers claiming other vars, and no linker settings forcing a non-numba/non-JAX backend. (https://github.com/pymc-devs/pymc/issues/8079, accessed 2026-07-12)

## 2. JAX / NumPyro backend and nutpie

- `pm.sample(nuts_sampler=...)` accepts three alternatives: **`"numpyro"`** (NumPyro JAX NUTS, i.e. `sample_numpyro_nuts`), **`"blackjax"`**, and **`"nutpie"`**. GPU sampling works only with the JAX-backed samplers: numpyro, blackjax, and nutpie's JAX backend. (https://www.pymc-marketing.io/en/stable/notebooks/general/other_nuts_samplers.html, accessed 2026-07-12; https://www.pymc.io/projects/examples/en/latest/samplers/fast_sampling_with_jax_and_numba.html, accessed 2026-07-12)
- Timing example from the PyMC "Faster Sampling with JAX and Numba" gallery notebook (documents PyMC v5.6.0, July 2023), probabilistic-PCA model: **Python NUTS 47.6 s; NumPyro 12.9 s (~3.7×); BlackJAX 11.6 s (~4.1×); nutpie 16.1 s (~3.0×)**. (https://www.pymc.io/projects/examples/en/latest/samplers/fast_sampling_with_jax_and_numba.html, accessed 2026-07-12)

**nutpie (Rust nuts-rs wrapper):**
- Latest version **0.16.11, uploaded June 30, 2026**; requires Python >=3.12; needs PyMC + Numba for PyMC models (`bridgestan` optional for Stan). Recent history: 0.16.10 (May 11, 2026), 0.16.9 (May 8, 2026), 0.16.8 (Mar 11, 2026), 0.16.4 (Nov 28, 2025). License MIT. (https://pypi.org/project/nutpie/, accessed 2026-07-12)
- **Two compile backends** (a PyTorch backend is stated to be "on the way"). **numba is the default** for PyMC models; JAX is opt-in:
  ```python
  compiled = nutpie.compile_pymc_model(model)                    # numba (default)
  compiled = nutpie.compile_pymc_model(model, backend="jax")     # JAX
  ```
  Docs: numba "tends to have relatively long compilation times, but samples small models very efficiently," while "for larger models the `jax` backend sometimes outperforms `numba`." GPU is via the JAX backend with a CUDA `jaxlib` (`pip install 'jax[cuda12]'`, verify with `jax.devices()`). (https://pymc-devs.github.io/nutpie/pymc-usage.html, accessed 2026-07-12; https://github.com/pymc-devs/pymc/issues/7497, accessed 2026-07-12)
- Reported speed: nutpie gives "an average ~2× speedup on posteriordb compared to Stan," typically higher ESS per gradient evaluation, converging with fewer gradient evaluations. (https://pymc-devs.github.io/nutpie/, accessed 2026-07-12; https://github.com/pymc-devs/nutpie/blob/main/README.md, accessed 2026-07-12)
- **Experimental normalizing-flow adaptation** (Fisher-HMC reparameterization). Install `pip install 'nutpie[nnflow]'`; enable with `transform_adapt=True` plus `.with_transform_adapt(num_layers=…, nn_width=…, num_diag_windows=…)`. It **requires the JAX backend with `gradient_backend="jax"`**; flow training is GPU-accelerable independently of the model. Reported gain on a 100-dim funnel: **42,527 gradient evals / min-ESS ~1,836 with flow vs 124,219 evals / min-ESS ~31 without**. (https://pymc-devs.github.io/nutpie/nf-adapt.html, accessed 2026-07-12) A March 20, 2026 write-up on Gelman's blog covers nutpie's mass-matrix adaptation and notes GPU sampling still has headroom (page returned HTTP 403 on fetch, so contents UNVERIFIED beyond the title/date). (https://statmodeling.stat.columbia.edu/2026/03/20/nutpie-state-of-the-art-mass-matrix-adaptation-for-hmc/, accessed 2026-07-12)

## 3. Performance for hierarchical models at scale

- The canonical PyMC Labs benchmark, "MCMC for Big Datasets: How Much Faster Is JAX and GPU," by **Martin Ingram, Dec 22, 2021**: a Bradley-Terry hierarchical model over **160,420 tennis matches, ~6,000 player parameters**, 1,000 warmup + 1,000 draws × 4 chains. Wall-clock: **PyMC+JAX+GPU (vectorized) 2.7 min; JAX+GPU (parallel) ~4.5 min; JAX+CPU ~7.5 min; standard PyMC ~12 min; Stan (cmdstanpy 1.0.0) ~20 min**. GPU-vectorized gave **~11× more ESS/s than PyMC and Stan and ~4× more than JAX-on-CPU**; JAX-CPU alone gave **2–3× ESS/s**. GPU **crossover point ≈ 50,000 observations** (below it, GPU overhead makes it slower). **nutpie was not in this benchmark** (predates it). (https://www.pymc-labs.com/blog-posts/pymc-stan-benchmark, accessed 2026-07-12)
- Community guidance is consistent: for thousands of groups, the JAX/GPU path (numpyro or nutpie-JAX) is the scaling lever; numba compile time is the main cost for large graphs, and JAX can overtake numba on large models. (https://pymc-devs.github.io/nutpie/pymc-usage.html, accessed 2026-07-12) A recent Discourse thread specifically discusses a hierarchical model with a copula on GPU choosing between NumPyro and nutpie under PyMC 5.19. (https://discourse.pymc.io/t/hierarchical-model-with-copula-on-gpu-numpyro-or-nutpie-using-pymc-5-19/17853, accessed 2026-07-12)

## 4. Published retail-elasticity case study (PyMC ecosystem)

- **"Hierarchical Pricing Elasticity Models," Dr. Juan Camilo Orduz** (PyMC Labs contributor), page dated **Aug 1, 2024**. This is the concrete, verifiable elasticity reference. (https://juanitorduz.github.io/elasticities/, accessed 2026-07-12)
  - Model: **constant-elasticity demand, linearized as `log(q) = log(A) + b·log(p)`**, where elasticity `= d log q / d log p = b`.
  - Data: **87 SKUs across 33 categories** after filtering (≥10 unique dates and ≥10 unique prices per SKU).
  - Three specifications compared: (1) **no pooling** (independent intercept + slope per SKU), (2) **fixed date effects** (SKU + date intercepts), (3) **hierarchical/partial pooling** with SKU elasticities nested in category-level distributions.
  - Priors (hierarchical model): category-level elasticity location `Normal(0, 1)`, category-level scale `HalfNormal(1)`, SKU elasticity `Normal(category_location, category_scale)`, SKU intercept `Normal(0, 1)`, date intercept `Normal(0, 1)`, category error variance `HalfNormal(global_scale)`. Fit with **NumPyro SVI** (reparameterization + AutoGuideList of AutoNormal/AutoMultivariateNormal), not MCMC.
  - **CORRECTION / flag**: search-engine summaries repeatedly asserted a PyMC Labs case study with "**5,000+ SKUs across ~200 categories**." That figure is **UNVERIFIED and appears to be a search-summarizer fabrication** — the actual page has **87 SKUs / 33 categories**. Do not cite the 5,000/200 numbers.
- Additional tutorial (secondary): **"Bayesian Price Elasticity with PyMC," Arthur Mello, Level Up Coding, March 2026** — builds three PyMC models of increasing complexity validated on synthetic data. Full text was behind a Medium redirect and could not be fetched, so its model internals are **UNVERIFIED**. (https://levelup.gitconnected.com/bayesian-price-elasticity-with-pymc-6e4836a1efa5, accessed 2026-07-12)
- PyMC Labs' own blog index (https://www.pymc-labs.com/blog-posts) is JS-rendered and exposes no post list to automated retrieval; the pricing-labelled post that does render, `/blog-posts/price-benchmark`, is the **"LLM Price is Right" benchmark** (Maxim Laletin & Allen Downey, Sept 17, 2025) — an LLM price-estimation Elo benchmark over 820 grocery items, **not** an elasticity/hierarchical model. (https://www.pymc-labs.com/blog-posts/price-benchmark, accessed 2026-07-12)

## 5. pymc-marketing scope (does NOT cover pricing/elasticity)

- Latest version **0.19.4, released May 6, 2026**; Apache-2.0; Python >=3.12. History: 0.19.0 (Mar 24, 2026), 0.18.0 (Feb 10, 2026), 0.17.0 (Oct 21, 2025). (https://pypi.org/project/pymc-marketing/, accessed 2026-07-12)
- Modules: **MMM** (media mix modeling), **CLV** (BG/NBD, Pareto/NBD, Gamma-Gamma buy-till-you-die), **Customer Choice Analysis** (Multivariate Interrupted Time Series / MVITS), **Bass diffusion**, and **discrete-choice** models. (https://github.com/pymc-labs/pymc-marketing, accessed 2026-07-12)
- **No pricing or price-elasticity module.** The README has **zero mentions of price elasticity**. The MMM transformations (geometric/other **adstock**, **logistic saturation**, time-varying intercepts via GPs) model **media-spend response, not price** — they are not a price-elasticity facility. (https://github.com/pymc-labs/pymc-marketing, accessed 2026-07-12; https://www.pymc-marketing.io/en/stable/, accessed 2026-07-12)
- Practical takeaway for elasticity work: pymc-marketing is the wrong package; hierarchical elasticity is hand-built in core **PyMC 6.x** (or NumPyro), as in the Orduz reference above.

---

### Verification caveats
- Every fetched GitHub release page and the levelup article rendered years as "2024/2025"; PyPI (authoritative, cross-checked) fixes all PyMC/nutpie/pymc-marketing dates to **2026**. Day/month matched across sources.
- Orduz post date (Aug 1, 2024) is as printed on the page; plausibly a genuine 2024 post, but automated retrieval carries a year-normalization bias, so treat the year as **reported, not independently confirmed**.
- "5,000 SKU / 200 category" elasticity figure: **rejected as unverified** (real page = 87/33).
- Gelman-blog nutpie post (Mar 2026) and the Arthur Mello PyMC elasticity tutorial: titles/dates seen in search, full contents **UNVERIFIED** (403 / Medium redirect).
