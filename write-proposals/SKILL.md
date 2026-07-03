---
name: write-proposals
description: |
  Consulting proposals, SOWs, and RFP responses as documents. Trigger on: "write the
  proposal", "draft the SOW", "respond to this RFP", "bid document", "/write-proposals".
  Begin at GATE P-1 of THE CONTRACT: the bid/no-bid verdict comes before any drafting.
  The claims audit is mandatory: no capability claim ships without a named basis.
  Checks: the writing sweep plus ai-engagements scripts/smell_check.py, both pasted.
  Response DECKS take their storyline from ideation Part 3; this skill owns the
  document substance: compliance, assumptions, pricing, acceptance criteria.
---

# Write proposals

A proposal is scored, not read for pleasure: an evaluator sits with a rubric, your document, and your competitors' documents, and nobody is in the room to explain. The sections below exist because bids die on missed requirements, buried assumptions, and claims the evaluator cannot verify. Everything here is the substance layer; formatted-document form routes to make-documents.

Set `SKILL_DIR=$HOME/.claude/skills/write-proposals` (fallback: `/path/to/skills/write-proposals`).

## Scope gate

IF the request edits one section of an existing proposal that already passed its gates: edit, re-run both checks, paste the proof lines, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT. Do not start a phase until the previous artifact exists.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE P-1** | Bid/no-bid against the decision table | P-1 gate card (template below) | Every table row answered with evidence; verdict recorded. IF the verdict is no-bid: present it with reasons and stop |
| **GATE P-2** | RFP only: extract every numbered requirement | The requirements ledger: `req # | their words (short) | our answer location | compliance` | Every numbered requirement appears; partial and non-compliance stated with a mitigation, never hidden. IF unsolicited (no RFP): record "ledger n/a, unsolicited" and continue |
| **GATE P-3** | Outline in the fixed section order, mirroring the RFP's own numbering | The skeleton artifact (template below) | Every section present or struck with a reason; unknowns already logged as assumption rows |
| **GATE P-4** | Audit every capability claim | The claims-audit table: `claim | basis` | Every claim carries a named past delivery with a date, a staffed capability, or the flag NEW; a claim with no basis is rewritten or cut |
| **GATE P-5** | Draft the document through the writing-instructions contract (its W gates) | The full draft on disk | Every gap discovered while drafting became an assumptions-register row, not a delay |
| **GATE P-6** | Run both checkers; fix every FAIL | Both proof lines as tool results | Zero FAILs, or each `allow:` justified in one line |
| **GATE P-7** | Deliver | DELIVERY block | Proof lines pasted; block ends the message |

Restated because they are the three most-violated rules: every unknown becomes a numbered assumption with its impact if wrong, never silent filler (P4); staffing is named roles with allocations, never "our expert team" (P6); discriminators are sentences an evaluator can quote into scoring notes (P7).

## Values

**Bid/no-bid table (GATE P-1).** Answer every row with evidence, not hope.

| Question | Bid signal | No-bid signal |
|---|---|---|
| Can we name a delivered reference for the core ask? | A named delivery with a date and a metric | Nothing closer than adjacent work |
| Do we have the people in the delivery window? | Named roles with confirmed availability | A staffing plan that starts with hiring |
| Is compliance achievable as the RFP is written? | Full or partial-with-mitigation on every requirement | A mandatory requirement we cannot meet |
| Is the incumbent wired to win? | Open field, or the incumbent is disqualified or disliked | The RFP reads like the incumbent wrote it |
| ELSE (a row cannot be answered) | Ask the user before proceeding | |

**The fixed section order (GATE P-3).** Mirror the RFP's numbering where one exists; where none exists, use this order:

1. Executive summary: what you will deliver, by when, for how much (where permitted), and the two or three discriminators, each a full sentence.
2. Understanding of the problem, in THEIR vocabulary (proves you read the ask).
3. Approach: a reference architecture that names every component, with no gaps a reviewer must fill.
4. Phasing with dates and the artifact each phase ends with.
5. Team: named roles with allocation percentages.
6. Assumptions register: numbered rows A1, A2, ... as `assumption | basis | impact if wrong`.
7. Scope: in and out, itemized.
8. Pricing, on a shape from the pricing table below.
9. Acceptance criteria per deliverable: deliverables are nouns with tests, not activities.
10. Compliance matrix (RFP responses): the requirements ledger, completed.

**Pricing shapes.**

| Situation | Shape |
|---|---|
| Unknowns dominate (data unseen, scope soft) | Fixed-price discovery phase that ends in a firm quote for the build |
| Scope firm, reference delivery exists | Fixed price by phase, payment on acceptance criteria |
| Client-directed backlog, shifting priorities | Time and materials with a monthly cap and a named review cadence |
| ELSE | Ask the user which shape the client relationship supports |

**The discriminator pattern.** A discriminator is verifiable, dated, and specific: "Only respondent operating this stack in production in Canada since 2023" scores; "deep expertise" does not. Shape: [only/first/the one] + [verifiable fact] + [date, place, or number].

## Artifact templates

```gate-card
GATE P-1 - bid/no-bid
ask: <what is being bid, one sentence>
reference: <named delivery, date, metric | "none - no-bid signal">    [row: "<the matched table row, verbatim>"]
people: <named roles confirmed | gap named>
compliance: <achievable | blocked by req #>
incumbent: <open field | wired - evidence>
verdict: <bid | no-bid, with the deciding row>
end-of-card
```

The skeleton (GATE P-3):

```
PROPOSAL SKELETON - <client, ask>
numbering mirrors: <the RFP's sections | "no RFP, house order">
1 executive summary: <the one-sentence answer to the ask>
2 understanding: <their vocabulary words to use: , , >
3 approach: <architecture components, each named>
4 phasing: <phase: artifact: date>
5 team: <role at allocation, role at allocation>
6 assumptions: <count so far, numbered A1..>
7 scope in/out: <top items each way>
8 pricing: <shape from the pricing table, cited>
9 acceptance: <deliverable: its test>
10 compliance: <ledger row count | "n/a, unsolicited">
```

Assumptions-register row and claims-audit row:

```
| A<n> | <assumption> | <basis: what makes it likely> | <impact if wrong: time, cost, scope> |
| <claim> | <named delivery + date | staffed capability (who) | NEW - flagged to the user> |
```

### Inlined from writing-instructions (full skill wins on conflict)

Full sentences; sentence case; no contrast framing; no em dashes; no emoji; every number carries units, a baseline, and a source; Canadian spelling (colour, centre, behaviour, labelled); kill list banned (robust, seamless, leverage, unlock, elevate, holistic, synergy, actionable, stakeholders, cutting-edge, transformative, AI-powered); named sources only ("a 2024 Uplevel study of 800 developers", never "studies show").

## Rules

| ID | Rule |
|---|---|
| P1 | The proposal mirrors the RFP's structure and numbering; their section 3.2 is your section 3.2. |
| P2 | Every numbered requirement appears in the ledger; partial or non-compliance is stated as such with a mitigation, never hidden. |
| P3 | The executive summary answers the ask in full sentences: what, by when, for how much (where permitted), and the discriminators. |
| P4 | Every unknown filled while writing becomes a numbered assumption with basis and impact-if-wrong; a buried assumption reads as ignorance or a trap, and evaluators price both. |
| P5 | Deliverables are nouns with acceptance criteria; dates are dates; scope-out is itemized next to scope-in. |
| P6 | Staffing is named roles with allocation percentages, never "our expert team" or "senior resources as required". |
| P7 | Discriminators follow the pattern: verifiable fact plus date, place, or number, quotable into an evaluator's scoring notes. |
| P8 | Every capability claim carries its basis from the claims audit; a claim flagged NEW is surfaced to the user before the draft ships. |
| P9 | "Draft before clarifications arrive": gaps become assumption rows immediately; drafting never waits on the client's answer window. |
| P10 | Proposal DECKS take their structure from ideation Part 3 (Monroe); this skill supplies the substance those slides carry. |
| P11 | ELSE: a situation these rules do not cover goes to the user as a question with your recommendation attached. |

## Checks

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <proposal file>
python3 $HOME/.claude/skills/ai-engagements/scripts/smell_check.py <proposal file>
```

Both MUST pass as tool results after the last edit. smell_check flags the soft-commitment phrases (E-SMELL) and percentage claims without denominators (E-DENOM) that end evaluations. A missing or crashing checker is a blocking failure to report, never a licence to self-attest.

## Delivery block

```delivery-block
DELIVERY write-proposals
files:
  <path>  (<size> B)
gates: <P-1..P-7 status, skips recorded>
checks:
  <sweep proof line, pasted>
  <smell_check proof line, pasted>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- The ai-engagements skill: scoping substance (matrix, metric, data audit) that a delivery-phase SOW must carry.
- The ideation skill, Part 3: win themes, discriminators, and the Monroe structure for RFP response decks.
- The discovery skill: the signed brief that seeds section 2 (understanding of the problem).
