# Calibration, history matching, and simulation-optimization

Companion to assets/sim_opt_bayes.py. Sources with URLs and access dates
sit in sources.md.

## Kennedy-O'Hagan calibration and its identifiability trap

The frame (Kennedy and O'Hagan, JRSS B 2001) models field observations as

    y(x) = eta(x, theta) + delta(x) + epsilon

with eta the simulator at inputs x and calibration parameters theta, delta
a GP discrepancy over x, epsilon observation noise. The estimation problem
is well known to be non-identifiable: a shift in theta can be absorbed by
delta, so the data alone cannot separate "the parameter is 7" from "the
parameter is 5 and the model is wrong in a way that looks like 7".

Brynjarsdottir and O'Hagan (Inverse Problems 2014) demonstrated the two
failure modes on a worked example: omit delta and the theta posterior
concentrates tightly on wrong values (confident and biased); include an
unconstrained delta and theta barely updates (honest and useless). The
working middle is an informative discrepancy prior encoding where and how
the simulator is expected to be wrong (sign constraints, smoothness,
boundary behaviour).

Consulting translation: report calibrated theta as tuning values whose
defence is predictive accuracy inside the calibration envelope. A physical
claim about theta ("the true digging rate is 7.2 kt/h") needs the
discrepancy prior argued in writing. Extrapolation outside the envelope
inherits no warranty from the calibration; say so in the readout, since
scenario studies exist precisely to extrapolate.

## History matching with implausibility

For expensive simulators, history matching (Vernon, Goldstein, Bower,
Bayesian Analysis 2010, the galaxy-formation paper; standard practice in
reservoir engineering) rules parameter space out in waves. For observed
target z and an emulator of the simulator output:

    I(theta) = |z - E[eta(theta)]| / sqrt(V_emulator + V_obs + V_discrepancy)

Discard theta where I exceeds 3 (Pukelsheim's three-sigma rule holds for
any unimodal distribution), refit the emulator on the surviving region with
new runs, repeat. Multiple outputs take the maximum implausibility across
targets, or the second-highest when one target is suspect.

Worked evaluation: z = 41,200 t/day observed; at a candidate theta the
emulator says 39,000 with sd 800; observation error sd 600; discrepancy
budget sd 1,000. Then I = 2,200 / sqrt(800^2 + 600^2 + 1000^2) =
2,200/1,414 = 1.55, so the candidate survives. Set V_discrepancy to zero
and I = 2,200/1,000 = 2.20, still surviving here, yet on tighter emulators
the zero-discrepancy shortcut is what empties parameter space and produces
the classic "no parameters fit" dead end, which in truth reads "no
parameters fit a model asserted to be perfect".

Why history matching leads at clients: each wave is a set of plain
simulator runs plus a GP fit, every exclusion has a one-line justification,
and the output ("this region of parameters is consistent with history")
matches how engineers already argue. Full Bayes posteriors come after, on
the surviving region, when the decision needs them.

### Simulation-based inference status

The sbi package (community-maintained, Tuebingen mackelab lineage)
implements neural posterior estimation and its sequential variants, with
flow-matching estimators arriving in recent versions. Through 2026 the
production users are physics, astronomy, and neuroscience; industrial DES
calibration cases are scarce. Treat NPE as the option when the simulator is
cheap enough for 10k+ runs and the posterior must be amortized (repeated
calibration of the same model family, e.g. one model per mine site); lead
with history matching otherwise.

## Drift and recalibration for a running twin

The residual stream e_t = actual KPI minus twin prediction is the health
signal. Practices that hold up:

- Chart e_t with a CUSUM or EWMA; alarm thresholds derive from the twin's
  own replication CI, so an alarm means "the plant moved beyond what the
  twin's noise explains".
- Tie scheduled reviews to decision tempo: monthly for planning twins,
  weekly for scheduling twins, immediate on known physical change (fleet
  change, liner change, roster change). Event-triggered recalibration
  catches step changes; the calendar catches slow drift.
- Recalibrate parameters first (a history-matching wave over recent data);
  revisit structure when parameter moves go unphysical, since a digging
  rate that must climb 30 percent to fit the data is a structure bug
  wearing a parameter costume.
- model-operations owns the monitoring machinery; the twin's residual
  stream enters it exactly as an ML model's residuals would.

## Ranking and selection against Bayesian optimization

| Situation | Method | Mechanics |
|---|---|---|
| k <= 20 discrete policies, best one wanted at a stated confidence level | KN procedure (Kim and Nelson 2001) | Sequential elimination on paired differences; composes with CRN, and the indifference zone delta is a business number you elicit ("differences under 300 t/day are operationally meaningless") |
| k <= 20, fixed compute budget, best expected pick | OCBA (Chen et al.) | Allocates replications proportional to how likely each arm is to change the answer; typically 30 to 70 percent cheaper than equal allocation at equal decision quality |
| Continuous or mixed design space, expensive noisy evaluations | BO with noise-aware acquisition | qLogNEI (Ament et al., NeurIPS 2023, the LogEI family) in BoTorch under Ax (1.0 released Nov 2025); the log-space forms fix the vanishing-gradient pathology of classic EI |
| Design space and budget both small | Full factorial plus paired-t | Nothing beats exhaustive when it is affordable, and the client can audit it |
| ELSE | Shortlist with the client, then KN over the shortlist | Adoption follows comprehension |

Craft points, each encoded in assets/sim_opt_bayes.py:

- Incumbent choice under noise: compute EI against the best posterior mean
  at observed points. An incumbent taken from the best raw observation is
  biased high by luck, EI collapses, and the search stalls exploring
  nothing.
- Winner's curse at reporting time: re-evaluate the chosen configuration on
  fresh replications. Demo measurement: the random-search winner's training
  value 8.657 fell to 8.394 (+/- 0.132) on 20 fresh replications, a 3
  percent optimistic bias that would have been quoted to the client.
- Fit the GP noise term from data (a white-noise kernel component); fixing
  noise at zero makes the surrogate interpolate replication luck.
- CRN and BO: standard GP machinery assumes independent noise across
  evaluations, so CRN's correlation goes unexploited; research exists
  (Pearce, Poloczek, Branke on BO with CRN) and no mainstream tooling does
  it as of Ax 1.0. Where CRN matters most (small discrete candidate sets),
  ranking and selection uses it natively, which is one more reason the k <=
  20 row above avoids BO.
- Multi-fidelity BO (supported in BoTorch via knowledge-gradient and
  multi-fidelity acquisition variants) pays when a coarse model runs 10x+
  cheaper and correlates above about 0.7 with the fine model on the design
  region; below that the cheap runs buy noise steering.

Budget rule of thumb with its critique: the folklore "10d initial points"
for GP surrogates traces to Loeppky, Sacks, and Welch (2009), whose own
paper frames it as an initial design heuristic for deterministic computer
experiments; stochastic simulators need replication on top, and total
budgets near 20d reach usable optima only for d up to about 10 and
well-conditioned responses. Present budgets as a starting plan plus a
stopping rule (posterior improvement flat over the trailing third of
evaluations), never as a fixed promise of convergence.

## OptQuest inside commercial tools

AnyLogic, Simio, and Arena embed OptTek's OptQuest, which runs scatter
search with tabu memory and neural-network screening. It treats the
simulation as a black box and by default optimizes single noisy
evaluations, so configure replications per iterate (or its built-in
confidence stopping where exposed) before trusting any ranking it emits.
Its practical strength is constraint handling over mixed discrete decision
variables inside the vendor UI, where the client's own engineers can rerun
the study; when the study must live in the client's Python stack instead,
the Ax route wins on reproducibility and CI integration.
