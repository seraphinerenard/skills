---
name: ai-engagements
description: |
  Scope, design, and deliver ML/AI work in a consulting engagement. Trigger on:
  "scope an AI engagement", "should we use RAG or an agent", "AI PoC", "client AI
  project", "AI feasibility study", "/ai-engagements". Begin at GATE E-1 of THE
  CONTRACT: no architecture talk, no demo, and no estimate before its gate passes.
  Model choice and pricing come from the claude-api skill, never memory. All
  client-facing prose passes writing-instructions; the smell
  checker scripts/smell_check.py is mandatory on anything priced or promised.
---

# AI engagements

Clients buy outcomes, not models. An engagement is won at scoping, when the problem, the metric, and the data get named, and lost at evaluation, when a demo that was never measured meets real traffic in front of the people who paid for it. Every gate below exists because skipping it ended an engagement somewhere. The artifact skills cover how deliverables look; this one covers whether the thing you deliver works.

Set `SKILL_DIR=$HOME/.claude/skills/ai-engagements` (fallback: `/path/to/skills/ai-engagements`).

## Scope gate

IF the request is a question about an in-flight engagement that already has a signed E-1 card and a frozen eval set: answer it from the engagement log, run `smell_check.py` on any text that leaves your hands, paste the proof line, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT. Do not start a phase until the previous artifact exists.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE E-1** | Scope: task as input to output, error-cost matrix, HITL position, client-named metric | E-1 gate card (template below) | Matrix quadrant quoted verbatim; metric has baseline, target, and date; sponsor sign-off recorded. IF the client cannot name a metric: the engagement is a priced workshop, load the discovery skill, stop |
| **GATE E-2** | Data audit by opening real extracts | The data-audit table, one row per claimed source | Every row records a 50-row sample you read yourself, with the date. A row you cannot fill this way stays empty and blocks the estimate |
| **GATE E-3** | Eval set from real inputs, client-reviewed | Pasted `wc -l cases.jsonl` tool output showing 20 or more, plus the sign-off note | NO DEMO EXISTS BEFORE THIS GATE. Set frozen and versioned; ugly cases included |
| **GATE E-4** | Baseline with the dumbest credible system | `baseline.json` committed; the score quoted in chat | One prompt, no retrieval, no tools; this is the number every later architecture must beat |
| **GATE E-5** | Build by escalation; budget cost and latency | Engagement-log rows (each escalation with the score that justified it) plus the filled cost-model block | Cost block shows current claude-api prices with their quote date and the agent multiplier; latency budget named from the shipping surface |
| **GATE E-6** | UAT and handover | UAT pass rate on the frozen set; the handover package list | UAT failures harvested into the eval set (the set only grows); the client reruns the harness without you in the room |
| **GATE E-7** | Deliver | DELIVERY block | smell_check and sweep proof lines pasted |

Restated because they are the three most-violated rules: no demo before the eval set exists (E3); prices come from the claude-api skill at the moment of writing, never memory (E5); the client-facing number is the pass rate on the frozen set and nothing else (E7).

## Values

**The frequency-by-error-cost matrix.** Place the task; the quadrant decides the automation posture and the HITL position.

| | Low cost of error | High cost of error |
|---|---|---|
| High frequency | Automate fully; spot-audit a sample | Automate with a human sign-off queue |
| Low frequency | Do not build; a script or a person is cheaper | Decision support only; the human decides |
| ELSE (frequency or error cost unknown) | Get the numbers first; the matrix has no unknown row | |

**Architecture selection.** Check disqualifiers first; one hit removes the row. Take the least complex surviving row, baseline it, escalate only on a measured eval failure. Full table with cost, latency, and risk per row: `references/architecture-selection.md`.

| Approach | Reach for it when | Walk away when |
|---|---|---|
| Classical ML | Tabular data, a labelled history, a numeric target | Labels are missing, or the input is open-ended text |
| RAG | Answers live in the client's documents and must cite them | The corpus is under about 50 documents (put them in the prompt), is stale with no refresh owner, or the task needs actions |
| Agent (tool loop) | The task needs live systems mid-flight: queries, lookups, actions | A fixed 2 to 3 step pipeline covers every observed case, or the surface has a sub-2-second budget |
| Fine-tuning | Format or tone must be exact and prompting has measurably plateaued | Under about 500 clean examples, or requirements still move |
| Buy, do not build | A vendor product passes your eval set out of the box | The workflow is the client's edge, or data cannot leave the tenancy |
| ELSE | Nothing survives the disqualifiers | Shrink the task and return to GATE E-1 |

**Eval sizing.**

| Cases | Buys you |
|---|---|
| 20 | Feasibility: the shape works |
| 100 | Tuning prompts and retrieval |
| 300 or more | Regression gating where a 2-point move is signal |
| ELSE (under 20) | Not an eval set; GATE E-3 stays closed |

**Cost model.** Cost is arithmetic; do the arithmetic before the proposal, with prices from claude-api:

```
monthly = requests/month x calls-per-request x
          (input tokens x input $/token + output tokens x output $/token)
agent loops: calls-per-request runs 3 to 10; cap steps in code, log cost per request
```

Worked shape at illustrative prices ($3/M in, $15/M out): 100,000 requests at 2,000 in + 500 out is about $1,350 a month single-call; the same traffic as an agent loop lands at $4,000 to $13,500. Prompt caching cuts repeated-context cost when the system prompt and documents are stable; quote current cache pricing from claude-api.

**Latency budgets.** Serial steps add: 5 steps at 2 s each is a 10 s answer, fine in a batch queue and dead in a call-centre screen.

| Shipping surface | Budget |
|---|---|
| Typeahead, live call screen | under 2 s |
| Interactive chat or form | 2 to 10 s |
| Work queue, back office | minutes |
| Batch, overnight | hours |
| ELSE | Ask the operator what they wait for today, then pick the row |

**The handover package.** An engagement only you can operate is a subscription the client did not order. Ship: (1) harness, cases, and baseline wired into the client's CI; (2) a runbook (how to add a case, read the scorecard, what to do when the score drops, who owns the judge model and its frozen prompt); (3) cost and latency dashboards with alert thresholds set during UAT; (4) the refresh plan for whatever decays (index re-embedding cadence, drift checks, prompt review on model upgrades); (5) the engagement log with the scores behind each decision.

## Artifact templates

```gate-card
GATE E-1 - scoping
task: <input> -> <output>, three real examples attached
matrix: <quadrant>    [row: "<the matrix row, quoted verbatim>"]
hitl: <review-before-ship queue | audit-after-ship sample | full-auto>
metric: <client's metric, in the client's units> from <baseline> to <target> by <date>
sponsor: <name, sign-off date, or "sent-awaiting">
end-of-card
```

The data-audit table (GATE E-2), one row per source, a row is fillable only after you opened the extract:

```
| source | owner | access path | 50-row sample read | label quality | refresh | constraints |
| <system> | <name> | <how you got in> | y, <date read> | <what you saw> | <cadence> | <PII, residency> |
```

The cost-model block (GATE E-5):

```
requests/month: <n>    calls/request: <n> (agent multiplier applied: <y/n>)
prices: input $<x>/M, output $<y>/M (claude-api, quoted <date>)
monthly: $<n>    latency: <steps> x <s per step> = <s>, against a <surface> budget of <s>
```

### Inlined from writing-instructions (full skill wins on conflict)

Every heading is a complete sentence in sentence case. No contrast framing ("it's not X, it's Y"). No em dashes, no emoji. Numbers carry units, baselines, and sources. Kill list: delve, robust, seamless, leverage, streamline, unlock, elevate, empower, holistic, synergy, actionable, stakeholders, cutting-edge, transformative, journey, landscape (figurative), AI-powered. Canadian spelling: colour, centre, behaviour, labelled, modelling.

## Rules

| ID | Rule |
|---|---|
| E1 | No architecture is named to the client before the decision table runs; the first architecture said out loud becomes the contract. |
| E2 | A data dictionary is a claim; only an opened extract fills a data-audit row. |
| E3 | No demo exists before the eval set: 20 real cases minimum, expected outputs client-signed, frozen and versioned. The demo runs cases FROM the set. |
| E4 | The baseline is the dumbest credible system; every escalation is justified by a recorded score gap, never by enthusiasm. |
| E5 | Prices, context limits, and model names come from the claude-api skill at the moment of writing; answers from memory are stale the day they are written. |
| E6 | Agent loops ship with a step cap in code, per-request cost logging, and outlier alerts from day one. |
| E7 | The client-facing number is the pass rate on the frozen set, and nothing else; "works great" without a denominator is banned. |
| E8 | If the inputs are enumerable, ship a form with the model behind it; chat earns its friction only on genuinely open input. |
| E9 | The latency budget is set from the shipping surface at design time, and the step count is checked against it before the architecture is chosen. |
| E10 | Client-facing numbers come from retrieved or computed values with a source reference, never free generation; numbered outputs route through a review queue until the eval set shows a sustained clean run, with spot-audits after. |
| E11 | Fine-tuning waits for a measured prompting-and-RAG failure on the same eval, stable requirements, and about 500 clean examples. |
| E12 | The eval set only grows; a wrong case is deleted with a note, never edited to pass. The judge model and its prompt stay frozen for the life of the set. |
| E13 | ELSE: a situation these rules do not cover goes back to the client sponsor as a question, not a guess. |

## Checks

```
python3 $SKILL_DIR/scripts/smell_check.py <proposal, SOW, or status report> [...]
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <the same files>
```

`smell_check.py` prints `FAIL E-SMELL` for soft commitments (AI-powered, best-in-class, up to N%, subject to data availability, and kin) and `FAIL E-DENOM` for percentage quality claims with no denominator nearby. Escape a deliberate use with `allow:E-SMELL <reason>` in a comment near the line. Output ends `PASS smell_check v1 file=<name> sha=<8hex>`; exit 0. Both runs MUST appear as tool results after the last edit; a missing or crashing checker is a blocking failure to report.

## Delivery block

```delivery-block
DELIVERY ai-engagements
files:
  <path>  (<size> B)
gates: <E-1..E-7 status, skips recorded>
checks:
  <smell_check proof line, pasted>
  <sweep proof line, pasted>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- `references/architecture-selection.md`: the full decision table with disqualifying conditions and the decision procedure.
- `references/eval-harness.md`: the runnable stdlib eval harness with regression gating; copy it into the engagement repo at GATE E-3.
- `references/pitfalls.md`: the demo-to-prod failure stories behind rules E1 to E12; read before the design review and again before UAT.
