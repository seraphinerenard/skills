# skills

A library of 36 agent skills for Claude Code, aimed at machine learning and analytics consulting work.

## What this repo contains

Each top-level directory is one skill. Every skill holds a `SKILL.md` file. A skill can also hold four optional directories. `scripts/` holds checkers. `assets/` holds starter files and libraries. `references/` holds background. `demos/` holds worked examples.

The library has two tiers.

The hard-gate tier holds 24 skills. Small models execute these skills step by step. Every skill in this tier follows the conformance protocol below.

The expert tier holds 12 skills for machine learning and analytics consulting. Frontier-class models read these skills as field manuals. Each one covers method selection, industry data traps, worked mathematics, sourced tool status, and runnable code. This tier carries no gates and no artifacts. The conformance protocol does not apply to it.

### The conformance protocol

`skill-writing/SKILL.md` defines the protocol. Every hard-gate skill obeys these five rules.

1. **A contract of numbered gates.** Each phase ends with a required artifact. Print the artifact before you start the next phase. A placeholder such as `<`, TODO, or TBD fails the gate.
2. **Values inline.** Every binding number, colour, size, and budget lives in `SKILL.md`. Reference files hold background only. Each decision table ends with an ELSE row. Each artifact quotes the table row it matched.
3. **Copy, do not create.** Start each deliverable from a `cp` of a supplied starter file. Starters carry `@keep` sentinel comments. Checkers require the sentinels, which proves the copy happened.
4. **Executable checks.** Each checker uses python3 and the standard library only. A checker prints `FAIL <rule-id> <file>:<line>` for each violation. It honours `allow:<rule-id> <reason>` escape markers. It ends a clean file with a proof line: `PASS <checker> v1 file=<name> sha=<8 hex digits>`.
5. **A delivery block ends every job.** The block lists the files, the gate status, the pasted proof lines, and the allow count.

## The skills

Foundations:

| Skill | Purpose |
|---|---|
| `writing-instructions` | House prose style, banned patterns with rule IDs, `scripts/sweep.py`. Root dependency of every other skill. |
| `skill-writing` | The protocol itself, and how to author or revise a skill. `scripts/check_skill.py`. |
| `ideation` | Idea generation with countable diversity quotas, plus the story phase for decks and long documents. |
| `design` | Frontend work with inline palettes, density tables, token-only colour, and `scripts/check_design.py`. |
| `review-deliverables` | The final review gate. Runs every mapped checker, then an honesty pass. |

Deliverables:

| Skill | Purpose |
|---|---|
| `make-charts` | Charts with a number in the title, a skeleton starter, and `scripts/check_chart.py`. |
| `make-documents` | Reports, memos, briefs, and one-pagers with assertion headings and an executive summary. |
| `make-videos` | Remotion MP4 files (mode A) and GSAP motion pages (mode B), plus `scripts/check_video.py`. |
| `dashboarding` | Agentic business intelligence on a reference app, with a questions gate and pasted round-trips. |
| `client-comms` | Status updates, recaps, follow-ups, bad news, and handoffs from five fixed templates. |
| `write-papers` | Papers with an evidence map, a rerun ledger, a verified-citation ledger, and sized limitations. |

Consulting practice:

| Skill | Purpose |
|---|---|
| `ai-engagements` | Delivery doctrine: error-cost matrix, data audit, evaluation before demo, `scripts/smell_check.py`. |
| `discovery` | Four question banks and the one-page signed brief that feeds `ai-engagements`. |
| `write-proposals` | Bid decision, requirements ledger, assumptions register, claims audit, and pricing shapes. |
| `brand-kit` | Client brand material turned into token sets, with `scripts/check_contrast.py`. |
| `demo-reframe` | Retargets a reference demo per client through a concept map and a rename ledger. |
| `accessibility-audit` | WCAG 2.2 AA scan, mandatory manual checklist, and coverage denominators. |
| `publish-mcp-tools` | MCP servers with an incumbent gate, no silent truncation, and `scripts/check_mcp_readme.py`. |

Quantitative work, operations, and research:

| Skill | Purpose |
|---|---|
| `analyze-data` | Profile before analysis, a claims ledger, the UTC join law, and survivorship checks. |
| `data-pipelines` | Idempotent and resumable pipelines, reconciliation counts every run, UTC storage. |
| `backtest-gauntlet` | Lookahead audit, fill realism, a sizing assertion, pre-registered verdicts, a paper gate. |
| `post-mortems` | Sourced UTC timeline, a transitory-or-structural verdict, and lessons with enforcement locations. |
| `daemon-ops` | launchd and systemd units from templates, heartbeats, and lint-then-observe installs. |
| `realtime-feeds` | SignalR, SSE, and WebSocket clients with gap marking, dual clocks, and reconnect proof. |

Expert tier:

| Skill | Purpose |
|---|---|
| `demand-forecasting` | Retail, perishables, building materials, utility load, spares. Censored demand and reconciliation. |
| `price-forecasting` | Lumber, aggregates, power, gas. Futures-curve evidence and vintage-data discipline. |
| `feature-engineering` | Leakage taxonomy, panel feature canon, dataset traps, and completeness protocols. |
| `consulting-cases` | Market sizing, PVM bridges, cohort and NRR work, discounted cash flow, diligence. |
| `supply-chain-optimization` | Network design, lot sizing, cutting stock, inventory theory, solver craft. |
| `price-optimization` | Elasticity identification, hierarchical Bayes, markdown dynamic programs, promotion MILP. |
| `predictive-maintenance` | Survival analysis under censoring, condition monitoring, alert economics, event evaluation. |
| `customer-analytics` | Churn, BTYD lifetime value, uplift targeting with Qini, segmentation, store clustering. |
| `simulation-digital-twins` | Discrete-event craft, Monte Carlo with copulas, calibration, simulation optimization. |
| `retail-analytics` | Foot traffic, phantom inventory, on-shelf availability, assortment, site selection. |
| `causal-inference` | Geo experiments, synthetic control, CUPED, staggered difference-in-differences, marketing mix models. |
| `model-operations` | Drift mathematics, retraining economics, forecast value added, data contracts, handoff. |

## How to use a skill

Link one skill directory into your Claude Code skills directory:

```bash
ln -sfn "$PWD/analyze-data" ~/.claude/skills/analyze-data
```

Link every skill in the repo with one loop:

```bash
for s in */; do
  [ -f "$s/SKILL.md" ] || continue
  ln -sfn "$PWD/${s%/}" ~/.claude/skills/"${s%/}"
done
```

Name the skill in your request, or type its slash command. Read `SKILL.md` first. Start at the first gate. Print each required artifact in order.

Two skills call external skills that this repo does not contain. `ai-engagements` reads model prices from a `claude-api` skill. `make-videos` mode A follows a `remotion-best-practices` skill. Supply both yourself, or replace those steps with current vendor documentation.

## How to run the checkers

Check protocol conformance across the hard-gate tier:

```bash
python3 skill-writing/scripts/check_skill.py \
  writing-instructions/SKILL.md skill-writing/SKILL.md ideation/SKILL.md \
  design/SKILL.md review-deliverables/SKILL.md make-charts/SKILL.md \
  make-documents/SKILL.md make-videos/SKILL.md dashboarding/SKILL.md \
  client-comms/SKILL.md write-papers/SKILL.md ai-engagements/SKILL.md \
  discovery/SKILL.md write-proposals/SKILL.md brand-kit/SKILL.md \
  demo-reframe/SKILL.md accessibility-audit/SKILL.md publish-mcp-tools/SKILL.md \
  analyze-data/SKILL.md data-pipelines/SKILL.md backtest-gauntlet/SKILL.md \
  post-mortems/SKILL.md daemon-ops/SKILL.md realtime-feeds/SKILL.md
```

The command exits 0 only when every file passes. Do not pass the expert-tier skills to this checker. Those 12 skills carry no gates, so the checker reports them as failures.

Check the prose style of any markdown file:

```bash
python3 writing-instructions/scripts/sweep.py README.md
```

Each checker prints one line per violation. A clean file gets a `PASS` proof line with a hash. Run each checker as your last action before you deliver. Any edit after a run voids the proof line.

## Licence

Licensed under the MIT License. Copyright 2026 Seraphine Renard.
