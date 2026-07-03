<!-- Compiled 2026-07-12. -->

---

# DES tooling for operations consulting: 2024-2026 status

Access date for all URLs: 2026-07-12. Vendor claims and practitioner or independent reports are marked separately. Two names that circulate in tool lists resolve to no DES engine at all, flagged in section 5.

## 1. SimPy

Current release is **SimPy 4.1.2, published 2026-05-24 on PyPI**. The release history matters for the maintenance read: 4.1.0 and 4.1.1 both landed in November 2023, so 4.1.2 followed an ~18-month gap with no releases. The project is "Production/Stable," MIT-licensed, lists four maintainers, and supports CPython and PyPy across Python 3.8 through 3.14. The canonical repo is the team-simpy GitLab, not GitHub (GitHub copies are forks). Read: alive and stable, low and irregular cadence, effectively feature-frozen core.
- https://pypi.org/project/simpy/ — version 4.1.2 (2026-05-24), Python 3.8-3.14, four maintainers, "5 - Production/Stable."
- https://simpy.readthedocs.io/ — process-based DES on standard Python generators; resources model limited-capacity congestion points.

Known limitations are documented by independent sources, not just folklore. SimPy ships no statistical distributions, no output/confidence-interval analysis, no common-random-number streams, no GUI, and no animation; it runs single-threaded and processes events sequentially. Practitioners treat the missing animation as the main adoption barrier against commercial tools.
- https://arxiv.org/html/2405.01562v1 — "Discrete Event Simulation: It's Easy with SimPy!" (2024 tutorial). States statistical sampling, CRN, output analysis, UI and animation are all outside SimPy's core; recommends salabim for animation.
- https://github.com/hsma-programme/simpy_visualisation — NHS-linked project stating visual output is a recognized SimPy limitation "hindering adoption of FOSS simulation in comparison to commercial modelling offerings."

Ecosystem add-ons that fill the gaps: **vidigi** (PyPI, by the HSMA/hsma-tools group) converts SimPy or Ciw event logs into Plotly animations embeddable in Streamlit/Dash/Shiny; it is explicitly early-stage with limited test coverage. NumPy/SciPy/pandas supply the missing statistics; SimPy + Streamlit is the common web-app delivery pattern.
- https://pypi.org/project/vidigi/ and https://github.com/Bergam0t/vidigi — animation of entity flow from SimPy/Ciw logs via Plotly.

Real use. The strongest documented industrial/consulting adoption is UK healthcare: **HSMA (Health Service Modelling Associates)**, a 15-month NHS training programme, teaches SimPy as its DES engine and publishes open example models (NHS 111 demand, rheumatology follow-up). German consultancy **SimPlan AG** markets SimPy DES as a service line. Academic-industrial use in semiconductor supply chains and inventory validation exists but is mostly research-grade.
- https://hsma.co.uk/hsma_content/modules/current_module_details/module_2_des/2b_simpy_des_1.html — SimPy as the NHS programme's DES engine.
- https://www.simplan.de/en/services/simpy-discrete-event-simulation-with-python/ — commercial SimPy consulting (vendor).

## 2. Salabim, Ciw, and other Python/adjacent DES

**Salabim** is far more actively developed than SimPy. Latest is **26.0.8, released 2026-06-24** (calendar-style versioning, YY.0.patch), sole maintainer Ruud van der Ham. It bundles what SimPy lacks: queues, resources, stores, statistical sampling, monitors, and native 2D and 3D animation with mp4/avi video capture. **Yieldless mode became the default at 23.3.0 (2023)**, removing the `yield` keyword from process code; yieldless depends on `greenlet`, so it will not run on some targets (for example Pythonista), and a parallel "yield version" of the docs is maintained. Version 25.0.9 (May 2025) added running salabim inside Excel via `xlwings lite` with no Python install (blind animation only); 25.0.16 (Nov 2025) confirmed Python 3.14.
- https://salabim.org/changelog.html — 26.0.8 (2026-06-24) and the 25.x/26.x history.
- https://www.salabim.org/manual/Overview.html — yieldless default, greenlet caveat, 2D/3D animation and video.

Independent SimPy-vs-salabim comparison (School of Simulation / Ross Munro, practitioner blog): SimPy has a minimal Pythonic API and a larger legacy user base; salabim has a broader object-oriented API, built-in animation, queues, state tracking and monitors, so complex models come out shorter and more declarative in salabim. With matched seeds both produce identical numeric output.
- https://www.schoolofsimulation.com/blog_posts/simpy-vs-salabim-simulation-comparison — practitioner comparison.

**Ciw** (Cardiff University, Palmer/Knight) targets open queueing networks specifically. Current **3.2.7**, Python 3.8-3.12. Differentiators: reproducibility-by-design, multiple customer classes, Type I blocking, baulking, reneging, priorities, server schedules, and graph-theoretic **deadlock detection** (`ciw.deadlock.StateDigraph` + `simulate_until_deadlock`, returning `times_to_deadlock`) that no commercial tool packages.
- https://ciw.readthedocs.io/ and https://ciw.readthedocs.io/en/latest/Guides/System/deadlock.html — deadlock detection API.
- https://www.tandfonline.com/doi/full/10.1080/17477778.2018.1473909 — Ciw journal paper (Journal of Simulation).

Adjacent libraries worth naming: **simmer** for R (trajectory-based, C++/Rcpp core, magrittr piping; CRAN package refreshed May 2026) is the R counterpart chosen alongside SimPy in the healthcare-reproducibility work below; **kalasim** (Kotlin/JVM) started as a "blunt rewrite of salabim," uses coroutines, koin DI, and Apache Commons Math, aimed at enterprise/JVM and real-time; **de_sim** (KarrLab) is a data-driven Python OO DES.
- https://r-simmer.org/ — simmer for R.
- https://www.kalasim.org/about/ — Kotlin salabim rewrite.
- https://github.com/galenseilis/awesome-des — curated DES library index.

## 3. Commercial tools at clients

**AnyLogic** (vendor: The AnyLogic Company). Multimethod is the moat: DES + agent-based + system dynamics in one model. 2025 shipped 8.9.4-8.9.7 plus eight Cloud releases (2.5.3-2.6.0); current desktop 8.9.6 (Sept 2025) added Material Handling blocks (SeizeRobot/ReleaseRobot), Rail/Pedestrian/Fluid library work. **AnyLogic 9 is a 100% browser-based web IDE**, in Technology Preview SaaS via AnyLogic Cloud, integrating modeling and cloud into one platform. RL story is **Pathmind/NativeRL** (PPO), exporting the model as a standalone Java env for cloud RL training. Pricing is quote-based; secondary aggregators (treat as unverified, likely stale) list Professional roughly **$12,390-$18,990** and University Researcher **$3,550-$4,250**, with PLE free.
- https://www.anylogic.com/blog/anylogic-9-overview-and-roadmap/ and https://anylogic.help/9/ — browser-based AnyLogic 9 (vendor).
- https://www.anylogic.com/blog/anylogic-8-9-6/ family and https://www.anylogic.com/purchase/ — releases and quote-based pricing (vendor).
- https://checkthat.ai/brands/anylogic/pricing — aggregator price bands (unverified).

**Simio** (vendor). Positions everything as the "Intelligent Adaptive Process Digital Twin." The scheduling differentiator is **RPS (Risk-based Planning and Scheduling)**: one DES run yields both a resource-constrained deterministic schedule and a probability-based risk analysis of that schedule, plus an APS layer wired to MES/ERP. Editions: Personal (free runtime), Design, Team, Enterprise, Portal; academic grants free; commercial pricing quote-only.
- https://www.simio.com/manufacturing-digital-twin-simulation/ and https://www.simio.com/whitepapers/what-is-aps — RPS/APS digital-twin positioning (vendor).

**Arena** (Rockwell Automation). Signals of stagnation are concrete: last major version **16.20, dated September 2022**, no major release since; through 2023-2025 the public activity was CISA ICS security advisories (uninitialized-pointer local code execution; fix at 16.20.11), and Wikipedia notes a suggestion that Arena may be folded into the FactoryTalk brand. Rockwell total revenue fell ~9% in FY2024. No divestiture found (searches surface the unrelated "Arena Group" media company). Read: maintained for security, not advancing.
- https://en.wikipedia.org/wiki/Arena_(software) — v16.20 (2022), possible FactoryTalk consolidation.
- https://www.cisa.gov/news-events/ics-advisories/icsa-25-329-02 — 2025 Arena security advisory.

**FlexSim** (Autodesk, acquisition closed **November 2023**). What changed since: **FlexSim 2025 (2024-12-11)** added USD export, Container objects, Task Sequence Queues; **2025 Update 1** upgraded the NVIDIA Omniverse Connector so USD exports carry simulation object properties (connections, processing/setup times), added dynamic AGV load types and timed travel; tighter link to Autodesk Factory Design Utilities. The FlexSim Answers forum migrated onto Autodesk Forums on 2025-04-25. Subscription ~**$6,000/yr** per aggregators (unverified). Dominant in high-fidelity 3D material handling, warehousing/AGVs, plus healthcare and mining.
- https://www.flexsim.com/news/flexsim-2025-update-1-change-object-class-exports-agv-timed-travel-more/ — USD export, Omniverse Connector properties, AGV load types (vendor).
- https://adsknews.autodesk.com/en/news/autodesk-acquires-factory-simulation-flexsim/ — acquisition (vendor).

**Plant Simulation** (Siemens Tecnomatix). Supported versions in 2025 advisories are **V2302 and V2404**; Siemens now also offers **Plant Simulation X** as SaaS. Genetic-algorithm optimization and energy-consumption analysis are the headline features. Dominant in automotive and aerospace body/assembly, plus electronics and pharma logistics.
- https://www.siemens.com/en-us/products/tecnomatix/plant-simulation-software/ — Plant Simulation X SaaS (vendor).
- https://www.cisa.gov/news-events/ics-advisories/icsa-25-072-08 — V2302/V2404 versions.

**Witness** (Lanner). Lanner was acquired by **Royal HaskoningDHV in 2019** and folded into the "Twinn" brand; the product is now **Twinn Witness** (Twinn Witness 26 released 2023). Sold as a consultancy-plus-software play. Strongest in FMCG/consumer goods, automotive, energy and utilities.
- https://www.royalhaskoningdhv.com/en/twinn/news/2023/twinn-witness-26 — Twinn Witness 26 (vendor).
- https://www.consultancy.uk/news/19982/ — Lanner acquisition.

## 4. Build-vs-buy, with practitioner sourcing

When Python/SimPy wins (documented drivers): zero license cost and no per-seat handoff friction, native git version control and CI, and direct integration with the pandas/NumPy/scikit-learn/PyTorch stack for optimization and RL. The clearest real-world case is NHS/HSMA: teams need to hand runnable models to non-licensed decision-makers, so they publish SimPy models as **Streamlit/Binder web apps**, using vidigi for the animation that stakeholders expect. Reviewers also flag SimPy's honest weakness: no native visual modeler, so you build reporting, validation and animation yourself.
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10593330/ — "Improving the usability of open health service delivery simulation models using Python and web apps."

When commercial wins: high-fidelity 3D animation for stakeholder buy-in (FlexSim, AnyLogic), prebuilt material-handling/conveyor/AGV libraries, the client's existing licenses and trained non-programmer modelers, and formal vendor support. Independent industry reporting frames the tradeoff bluntly: cost is the biggest pull toward open source, but the learning curve is steeper and there is no formal support channel to lean on "in the heat of the moment."
- https://www.digitalengineering247.com/article/open-source-meets-simulation/simulate — practitioner view on FOSS-vs-commercial support and cost.

Practitioner-community signal (INFORMS / Winter Simulation Conference / OR Society). A serious FOSS-DES research thread is running, led by **Tom Monks and Alison Harper (University of Exeter)** under the **STARS project** (Sharing Tools and Artifacts for Reusable Simulations, MRC-funded May 2024-Oct 2026). Their empirical reproducibility study (Heather, Monks, Harper, Mustafee, Mayne, arXiv:2501.13137) audits open healthcare DES models and finds reproduction is hard even with code available, driven by missing dependency/version pinning and environment setup gaps; they name **SimPy and R simmer as the two most widely used FOSS DES options in healthcare**. They also ran an introductory FOSS-DES tutorial at the OR Society Simulation Workshop 2025. WSC 2024 (Orlando, Dec 15-18) and the SimOpt workshop pushed open-source simulation-optimization libraries; WSC proceedings are free at informs-sim.org.
- https://arxiv.org/pdf/2501.13137 — reproducibility empirical study; SimPy + simmer named as the dominant FOSS DES pair.
- https://github.com/pythonhealthdatascience and https://pythonhealthdatascience.github.io/des_rap_book/ — STARS project and the "Reproducible DES in Python and R" (DES RAP) book.
- https://www.informs-sim.org/wsc25papers/inv144.pdf — WSC 2025 proceedings (free).

## 5. Newer entrants and GPU/ML-integrated research (2024-2026)

Two names that circulate in tool lists do not resolve to real DES engines, so flag them: there is **no DES engine named "Quaint"** (the closest 2024 artifact is an open-source **Unity/C# 3D DES**, Journal of Simulation vol. 18 no. 5, 2024). **"POLARS" is not a DES engine** either: **Polars** is a Rust/Arrow dataframe library, while **POLARIS** (Argonne National Lab) is an open-source agent-based transportation framework that happens to contain a DES engine.
- https://www.tandfonline.com/doi/full/10.1080/17477778.2024.2314166 — Unity-based open-source 3D DES (2024).
- https://anl-polaris.github.io/ — Argonne POLARIS transportation ABM with a DES engine.

Credible open-source engines with real traction: **salabim** and **Ciw** (above), **JaamSim** (free, drag-and-drop, 3D; a Fraunhofer study concludes it is a genuine alternative to Arena and Plant Simulation for production/logistics, and a 2024 Brazilian steel-plant study used it in industry), and **kalasim** for JVM shops.
- https://www.sciencedirect.com/science/article/pii/S1877050921004038 — Fraunhofer: JaamSim as a real alternative to commercial DES.

Julia route: **JumpProcesses.jl** (in the SciML/DifferentialEquations.jl ecosystem) implements Gillespie/SSA methods (Direct, RDirect, DirectCR, FRM) and composes jump processes with ODEs/SDEs for hybrid and jump-diffusion models. This is the credible path for stochastic-chemical-kinetics-style DES fused with continuous dynamics and scientific ML.
- https://docs.sciml.ai/JumpProcesses/stable/ — SSA methods and jump-ODE/SDE composition.

GPU/ML-integrated DES research: a Queen's University Belfast / Carleton group (Faheem, Murphy, Wainer et al., IEEE) accelerated **SimPy** manufacturing DES using **TensorFlow on GPU**, reporting speedups of **1.4x to 3.21x**, aimed at real-time sim-to-physical-system communication for Industry 4.0. GPU-driven DES also appeared in network simulation at ACM SIGCOMM 2024.
- https://ieeexplore.ieee.org/document/9631514/ — "GPU-Accelerated Discrete Event Simulations: Towards Industry 4.0 Manufacturing," 1.4x-3.21x speedups over SimPy.

## 6. Interop: OpenUSD/Omniverse and FMI/FMU

**OpenUSD / NVIDIA Omniverse** is the fast-moving visualization/interop layer. At COMPUTEX 2025 NVIDIA expanded the **Omniverse Blueprint for AI factory digital twins** to support OpenUSD schemas and a **SimReady** standardization workflow, with Siemens, Rockwell, Schaeffler, Vention, Sight Machine and others building digital twins on it. The concrete DES tie-in: **FlexSim's USD export now carries simulation object properties into Omniverse** (section 3), so a DES model and a photoreal twin can share one USD scene.
- https://blogs.nvidia.com/blog/omniverse-blueprint-ai-factories-expands/ — OpenUSD schemas + SimReady (vendor).
- https://developer.nvidia.com/blog/designing-ai-factories-using-openusd-and-simready-assets/ — SimReady assets for factory twins (vendor).

**FMI/FMU co-simulation.** FMI 3.0 (released 2022 by the Modelica Association) is the current standard for industrial co-simulation and system-level digital twins, adding **layered standards**, **virtual ECUs**, and more efficient parameter updates for AI/ML use. In July 2024 **NVIDIA and blue automation joined the FMI steering panel**, a signal that the Omniverse and FMI worlds are converging. Open-source glue exists: **OpenTwins** (Wiley, Software: Practice and Experience, 2024) integrates FMI/FMU models with ML/AI on an open digital-twin framework.
- https://fmi-standard.org/news/2022-05-10-fmi-3.0-release/ — FMI 3.0 features (standards body).
- https://onlinelibrary.wiley.com/doi/full/10.1002/spe.3322 — OpenTwins integrating FMI + ML/AI (2024, peer-reviewed).

## Bottom line for the reference

- SimPy is stable but slow-moving (18-month release gap before 4.1.2 in May 2026); its animation/stats gaps are now routinely filled by salabim, vidigi, and Streamlit rather than by SimPy itself.
- The active Python DES frontier is salabim (26.x, yieldless, native animation) and Ciw (queueing + deadlock detection), with a serious reproducibility/FOSS-adoption research programme (STARS, Monks/Harper) coming out of UK healthcare and WSC.
- Among commercial tools, AnyLogic (multimethod, browser-based v9) and FlexSim/Simio (digital-twin + USD/Omniverse) are advancing, while Arena reads as security-maintained but stagnant (no major release since 2022).
- The interop story to watch is OpenUSD/Omniverse for visualization and FMI 3.0 for co-simulation, now linked by FlexSim's USD property export and NVIDIA joining the FMI panel.

Caveats on numbers: all commercial per-seat prices come from third-party aggregators and are unverified against vendor quotes; the AnyLogic and FlexSim figures in particular should be treated as rough and possibly stale.
