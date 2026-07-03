# Sources

Two classes: web sources checked during this build (access date given) and
standard bibliographic references cited from the literature (identifier
given, no access claim). The DES tooling facts in SKILL.md condense the
researcher fact sheet at research/des-tooling.md, which carries its own
annotated URL list, all accessed 2026-07-12.

## Web sources, accessed 2026-07-12

- Kritzinger, Karner, Traar, Henjes, Sihn, "Digital Twin in manufacturing:
  A categorical literature review and classification", IFAC-PapersOnLine
  51(11), 2018. https://www.sciencedirect.com/science/article/pii/S2405896318316021
  Basis for the model/shadow/twin taxonomy and the finding that true twins
  are scarce next to models and shadows.
- "To Twin Or Not To Twin", COOCK Smart Port project deliverable D3.1,
  2024. https://arxiv.org/pdf/2401.12747 Port-logistics survey of when
  building a twin pays; supports the fidelity-economics stance.
- Meta engineering blog, "Efficient Optimization With Ax, an Open Platform
  for Adaptive Experimentation", Nov 2025.
  https://engineering.fb.com/2025/11/18/open-source/efficient-optimization-ax-open-platform-adaptive-experimentation/
  Ax 1.0 release; BoTorch underneath.
- BoTorch tutorial, "q-Noisy Constrained EI" and the LogEI acquisition
  family docs. https://botorch.org/docs/tutorials/closed_loop_botorch_only
  qLogNEI/qLogEI usage for noisy objectives.
- sbi documentation and project pages. https://sbi-dev.github.io/sbi/ and
  https://transferlab.ai/software/sbi/ Community maintenance (Tuebingen
  mackelab lineage plus TransferLab), neural posterior estimation scope.
- Heather, Monks, Harper, Mustafee, Mayne, "On the reproducibility of
  discrete-event simulation studies in health data science", 2025.
  https://arxiv.org/pdf/2501.13137 Empirical audit; most open DES models
  fail to rerun for environment and pinning reasons; SimPy and R simmer
  named the dominant FOSS DES pair in healthcare.
- Full DES tooling URL list (SimPy 4.1.2, salabim 26.0.8, Ciw 3.2.7,
  AnyLogic 9, FlexSim/Autodesk USD export, Arena stagnation, Plant
  Simulation X, Twinn Witness, JaamSim, JumpProcesses.jl, OpenUSD/Omniverse,
  FMI 3.0): see research/des-tooling.md in this folder.

## Bibliographic references

- Law, A. M., Simulation Modeling and Analysis, 5th ed., McGraw-Hill, 2015.
  <!-- allow:CAN published book title uses the US spelling -->
  Chapters 6 (input modelling) and 9 (output analysis, relative-precision
  replication rule).
- Welch, P. D., "The statistical analysis of simulation results", in The
  Computer Performance Modeling Handbook, 1983. Warm-up procedure.
  <!-- allow:CAN published book title uses the US spelling -->
- Hoad, K., Robinson, S., Davies, R., "Automated selection of the number of
  replications for a discrete-event simulation" and the AutoSimOA warm-up
  work, Journal of Simulation, 2010. MSER-5 recommendation.
- Sargent, R. G., "Verification and validation of simulation models",
  Proceedings of the Winter Simulation Conference, 2010 edition of the
  long-running tutorial. Validation test catalogue.
- Kim, S.-H., Nelson, B. L., "A fully sequential procedure for
  indifference-zone selection in simulation", ACM TOMACS 11(3), 2001. KN
  procedure.
- Chen, C.-H. et al., Optimal Computing Budget Allocation line of work
  (OCBA), from Chen, Lin, Yucesan, Chick 2000 onward.
- Kruskal, W. H., "Ordinal measures of association", JASA 53, 1958.
  Spearman and Kendall relations for the bivariate normal.
- Iman, R. L., Conover, W. J., "A distribution-free approach to inducing
  rank correlation among input variables", Communications in Statistics,
  1982. Rank-reordering correlation induction.
- Higham, N. J., "Computing the nearest correlation matrix, a problem from
  finance", IMA Journal of Numerical Analysis 22, 2002.
- Kennedy, M. C., O'Hagan, A., "Bayesian calibration of computer models",
  JRSS B 63(3), 2001.
- Brynjarsdottir, J., O'Hagan, A., "Learning about physical parameters: the
  importance of model discrepancy", Inverse Problems 30(11), 2014.
- Vernon, I., Goldstein, M., Bower, R., "Galaxy formation: a Bayesian
  uncertainty analysis", Bayesian Analysis 5(4), 2010. History matching
  with implausibility.
- Pukelsheim, F., "The three sigma rule", The American Statistician 48(2),
  1994.
- Ament, S. et al., "Unexpected improvements to expected improvement for
  Bayesian optimization", NeurIPS 2023. LogEI/qLogNEI family.
- Loeppky, J. L., Sacks, J., Welch, W. J., "Choosing the sample size of a
  computer experiment", Technometrics 51(4), 2009. The 10d heuristic and
  its stated limits.
- Pearce, M., Poloczek, M., Branke, J., work on Bayesian optimization with
  common random numbers (Winter Simulation Conference / arXiv, 2019
  onward). CRN-aware BO exists in research, absent from mainstream tooling.
- Lewis, P. A. W., Shedler, G. S., "Simulation of nonhomogeneous Poisson
  processes by thinning", Naval Research Logistics Quarterly 26, 1979.
