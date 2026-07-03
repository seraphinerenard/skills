---
name: ideation
description: |
  Divergent idea generation and story development. MANDATORY in two situations:
  (1) before recommending ideas of any kind (products, strategies, investments, features,
  services, names, approaches): begin at GATE I-1 and run the full widen-diverge-gauntlet
  contract instead of presenting first thoughts; (2) before building any deck or long-form
  document: begin at GATE I-5, the story phase, and get the storyline approved before
  any slide or section gets written. No scripts ship with this skill: the quota tables ARE the
  checks, and every quota count is printed under its table.
---

# Ideation

A language model's first answer is the statistically modal answer: the idea most people would produce. Doshi and Hauser (Science Advances, 2024) found AI assistance made individual stories better while making the pool more alike; Anderson and colleagues (Creativity and Cognition, 2024) found groups ideating with the same model converge on the same ideas. The obvious idea is the one an incumbent has already priced in. This skill forces width before depth, kills weak ideas before the user sees them, and makes fake divergence visible through countable quotas.

Set `SKILL_DIR=$HOME/.claude/skills/ideation` (fallback: `/path/to/skills/ideation`).

## Scope gate

IF the user asks you to evaluate ONE existing idea: run GATE I-3 (the gauntlet) on it, present it in the I-4 format, stop. IF the task is the story phase for a deck or document with no idea generation: begin at GATE I-5. ELSE (any request to propose, recommend, or brainstorm): run the full contract from GATE I-1.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT printed in the conversation.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE I-1** | Widen the frame two levels up, sideways, and second-order before generating anything | Frame card (template below), 2+ named entries per row | Card printed; no `<`, `TODO`, `TBD` |
| **GATE I-2** | Diverge using the technique menu; number every candidate | CANDIDATES table + its quota line | All six quotas met; quota line printed under the table |
| **GATE I-3** | Attack every candidate with the five gates | GAUNTLET table + kill-quota line | At least half the rows DEAD with the killing gate named |
| **GATE I-4** | Present survivors only | One 5-field block per survivor | Every field filled; no adjectives doing the work of evidence |
| **GATE I-5** | (Decks and documents) Define the transformation; draft 2 or 3 candidate stories on different spines; put the choice to the user | Transformation card + story synopses + an AskUserQuestion call | The user chose; IF AskUserQuestion is unavailable, options presented and the turn STOPPED |
| **GATE I-6** | Expand the chosen story | STORYLINE table | Titles alone deliver the whole argument; explicit user approval recorded |

Restated because they are the three most-violated rules: never present an idea that has not been through the gauntlet (I1); rows 1 to 3 of the candidates table are the obvious ones and MUST be flagged "(obvious)" (I2); never choose the story for the user (I7).

## Values

**Predictability tags.** Every candidate carries one:

| Tag | Meaning |
|---|---|
| high | Any model's first suggestion; retrieved, not constructed |
| med | Needs one non-obvious connection to reach |
| low | Reachable only through the widened frame, a far analogy, or a hard constraint |
| ELSE | IF you cannot tag a row, it is high |

At most 60% of rows share one tag. IF every row is "med", re-tag honestly.

**The technique menu.** Use at least three techniques across the candidate set; the mechanism column shows which. Full drills and the research behind each are in `references/creativity-methods.md`.

| Technique | Move |
|---|---|
| Ban the default | State the obvious answer, then require every further idea to differ on mechanism, customer, or channel; add each used mechanism to the banned list and go again |
| Inversion | Design the worst possible answer, list why it fails, negate each property |
| Far-domain analogy | Name 3 fields that face the same shaped problem under different economics; port the mechanism, keeping its logic and swapping the nouns; NAME the source field in the mechanism cell |
| Constraint injection | Re-ideate under: capital under $5K; no software; exactly one customer; must embarrass an incumbent to copy |
| Extremes | The 10x-cheaper version; the 10x-smaller-market version; the one customer paying 100x |
| Second-order | Skip the direct beneficiary; who benefits after them, who is forced to act, who gets squeezed |
| Historical rhyme | Find the closest prior episode (a capex cycle, a platform shift); apply what worked in its second year |
| ELSE | IF stuck under 20 rows, run one more constraint round; quotas never shrink |

**Widening, worked example.** The conversation mentions Sandisk. One level up: NAND flash and storage hardware (Micron, Kioxia, SK Hynix). Two levels up: the data-centre buildout and what it strains (power, transformers, cooling, land, electricians). Sideways: device refresh cycles, edge inference, the used-equipment market, freight for heavy electrical gear. Second-order: regional utilities get squeezed; switchgear makers with four-year backlogs get pricing power; interconnection queues break. The mention is a sample of the user's interest, never its boundary.

**Story spines.** Draft each candidate story on a different row. Full mechanics and worked slide flows are in `references/story-frameworks.md`.

| The deck's job | Spine |
|---|---|
| Recommend a decision to seniors or a board | SCQA: Situation, Complication, Question, Answer as the governing thought |
| Win one decision fast, few slides | ABT: and, but, therefore; one But only |
| Move an audience comfortable where it is | Sparkline: alternate what-is with what-could-be, end on the new normal |
| Proposal or RFP with an explicit ask | Monroe: attention, need, satisfaction, visualization, action |
| Teach what happened and why | Story spine: because-of-that causal chain |
| ELSE | Ask the user what decision the deck must produce, then pick from this table |

## Artifact templates

```gate-card
GATE I-1 - frame card
mentioned: <the thing the user named>
one level up: <2+ named entries>
two levels up: <2+ named entries>
sideways: <2+ named entries>
second-order: <2+ named entries: who is squeezed, who gains pricing power, what breaks>
end-of-card
```

CANDIDATES table (GATE I-2), followed by its mandatory quota line:

```
| # | idea (one line) | mechanism | customer | channel | predictability |
|---|---|---|---|---|---|
| 1 | ... (obvious) | ... | ... | ... | high |
...
QUOTA LINE: rows=<n>/20+ | mechanisms=<n>/3+ | customers=<n>/3+ | channels=<n>/3+ |
far-domain rows=<n>/3+ (fields: <named>) | largest tag share=<n>% (max 60%)
```

IF any quota fails: generate more rows. Quotas never shrink to fit the list.

GAUNTLET table (GATE I-3), followed by its kill-quota line:

```
| # | feasible | distribution | incumbent | why now | first test | verdict |
|---|---|---|---|---|---|---|
| 1 | pass/fail+reason | ... | ... | ... | ... | LIVE / DEAD (gate <n>) |
KILL LINE: dead=<n>/<total> (MUST be at least half; fewer means the gauntlet was
soft: rerun it harder and say so)
```

Gate meanings: feasible = physics, data access, capital, regulation; distribution = can THIS user reach THIS market; incumbent = why a feature release does not erase it (channel conflict, margin dilution, regulatory exposure, niche too small for them); why now = the thing that changed (a cost curve, a rule, an API, a behaviour); first test = first dollar, user, or datapoint within weeks, and what it would falsify.

Survivor format (GATE I-4), one block per survivor, plain sentences:

```
claim: <one falsifiable sentence>
mechanism: <who pays or acts, and why>
incumbent: <why they structurally will not do this>
strongest objection: <written as sharply as a critic would>
first cheap test: <the contact with reality, and what it falsifies>
```

```gate-card
GATE I-5 - transformation card
audience: <who reads or watches>
now: <what they believe or do today>
after: <what they must believe or do>
context: <presented live | read alone>, budget: <slides or pages>, decision: <the one being made>
end-of-card
```

STORYLINE table (GATE I-6):

```
| slide | assertion title (one full sentence) | evidence | source |
HORIZONTAL-FLOW LINE: titles read in order deliver the argument with no gaps,
no repeats, no topic labels. User approval: <quoted>
```

### Inlined from writing-instructions (full skill wins on conflict)

Survivor claims and story synopses are full sentences in sentence case. No contrast framing ("it's not X, it's Y"). Numbers carry units, baselines, and sources; a market size is a named source or absent. Kill list applies: delve, robust, seamless, leverage, unlock, holistic, synergy, actionable, game-changer, transformative, landscape (figurative). No em dashes, no emoji. Canadian spelling.

## Rules

| ID | Rule |
|---|---|
| I1 | Never present an idea that has not been through the gauntlet; every verdict names its killing gate or its passes. |
| I2 | Rows 1 to 3 are the obvious ones, flagged "(obvious)"; they survive only on gauntlet merit. |
| I3 | Quotas: 20+ rows; 3+ distinct mechanisms, customers, channels; 3+ far-domain rows naming the source field; max 60% one predictability tag. Duplicate cells are how padding is caught: paraphrases share a mechanism cell. |
| I4 | Kill quota: at least half the candidates die. A gauntlet that passes everything "with caveats" was not run. |
| I5 | The model never ranks its own novelty (no positive correlation with expert judgment, CHI 2024): ranking comes from the gauntlet and the user's domain knowledge. |
| I6 | Ideate across the widened frame, then narrow with stated reasons; narrowing at generation time produces the five ideas every model produces. |
| I7 | The story choice is the user's: an AskUserQuestion call, or present the options and STOP the turn. Choosing silently or blending the candidates into porridge is a failed gate. |
| I8 | The storyline passes horizontal flow: titles alone, read in order, deliver the entire argument. "Vendor comparison" fails; a full-sentence claim passes. |
| I9 | No layout, no code, no slide building before the storyline is approved. Slides built before the story get rebuilt; that is the expensive path. |
| I10 | RFP responses: the story substance and win themes route through Monroe here; proposal mechanics live in write-proposals. |
| I11 | ELSE: a situation this table does not cover gets asked, not improvised. |

## Checks

This skill ships no scripts. The checks are countable properties of the printed artifacts, and each count MUST be printed in the artifact's quota line:

1. CANDIDATES: count the rows (20+); count distinct mechanism, customer, channel cells (3+ each); count far-domain rows and name their fields (3+); compute the largest tag share (max 60%).
2. GAUNTLET: count DEAD verdicts (at least half); every DEAD names its gate; every LIVE has all five cells filled with reasons, not ticks.
3. STORYLINE: read the titles alone, in order, out loud; record the user's approval verbatim.

A missing quota line is a failed gate even when the table happens to satisfy the quotas.

## Delivery block

```delivery-block
DELIVERY ideation
files: none (conversational) | <paths if a storyline file was written>
gates: <I-1..I-6 status, skips recorded>
checks:
  <the quota line, kill line, and horizontal-flow line, pasted verbatim>
allows: none
end-of-delivery
```

## References

- `references/creativity-methods.md`: the research (homogenization findings, serial-order effect, verbalized sampling, denial prompting) and the full drill for each technique.
- `references/story-frameworks.md`: SCQA, ABT, sparkline, Monroe, story spine, with worked slide flows and the horizontal-flow test.
