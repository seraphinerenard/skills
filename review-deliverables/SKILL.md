---
name: review-deliverables
description: |
  The final red-team gate before any deliverable ships, and the home of the honesty
  gate. Trigger on: "review this before it ships", "final review", "red-team this",
  "pre-delivery review", "run the honesty gate", "/review-deliverables". Begin at
  GATE R-1 of THE CONTRACT. This skill ships no checker of its own: it runs every
  other skill's checker by absolute path (the CHECKER MAP below) and the writing
  sweep, and every proof line lands in the delivery block.
---

# Review deliverables

Nothing ships on its author's word. This skill is the last pass between finished work and the client: every mechanical checker runs again, every claim gets audited for overclaim, and a hostile reader's questions get written answers. The recurring house lesson across accessibility, MCP publishing, and demo work is the same sentence: state limits, do not overclaim. This skill is where that sentence gets enforced.

Set `SKILL_DIR=$HOME/.claude/skills/review-deliverables` (fallback: `/path/to/skills/review-deliverables`).

## Scope gate

IF the request is to re-verify one file already reviewed this session after a stated fix: re-run that file's mapped checkers, paste the proof lines, update the verdict card, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE R-1** | List every deliverable file with its type and audience | R-1 inventory card (template below) | Card printed; every file matched to a CHECKER MAP row, quoted verbatim |
| **GATE R-2** | Run every mapped checker by absolute path | Every proof line, pasted from tool results | Zero FAILs, or each fixed and re-run; a missing checker reported as a blocker |
| **GATE R-3** | The honesty pass: claims audit, overclaim kill list, Limitations check | The claims-audit table (template below) | Zero kill-list hits remain; every README or report has a Limitations section |
| **GATE R-4** | The skeptical-reader pass: written answers to the five questions per deliverable | The five answers, written out | No unanswered question; unanswerables became fixes or stated limitations |
| **GATE R-5** | Verdict | R-5 verdict card: SHIP, or the fix list with owners | Verdict card printed |
| **GATE R-6** | Deliver: the review report passes the writing sweep | DELIVERY block | Proof lines pasted; block ends the message |

Restated because they are the three most-violated rules, binding during R-2 and R-3: checker runs MUST appear as tool results, typed output is a failed gate (R2); one FAIL anywhere holds the verdict at NOT-SHIP until the fix or an owner-skill `allow:` marker lands (R3); every overclaim is rewritten to scoped language with its coverage number, never silently deleted (R5).

## Values

**The checker map.** Every deliverable matches exactly one row; the inventory card quotes the row.

| Deliverable type | Checkers (run each, absolute paths) |
|---|---|
| HTML interface, page, or dashboard view | `$HOME/.claude/skills/design/scripts/check_design.py` then `$HOME/.claude/skills/writing-instructions/scripts/sweep.py` |
| HTML chart or data graphic | `$HOME/.claude/skills/make-charts/scripts/check_chart.py` then the sweep |
| Video source (Remotion or motion page) | `$HOME/.claude/skills/make-videos/scripts/check_video.py` then the sweep on visible copy |
| Prose file: report, memo, README, brief (.md, .txt) | the sweep |
| Proposal or SOW | the sweep, then `$HOME/.claude/skills/ai-engagements/scripts/smell_check.py` |
| SKILL.md | `$HOME/.claude/skills/skill-writing/scripts/check_skill.py` |
| ELSE | the sweep over any visible prose, plus a named line in the verdict card: "no mechanical check exists for <thing>" |

**The overclaim kill list.** Each hit is rewritten, never shipped. The register to match: "supports WCAG 2.2 AA conformance work; automated checks find roughly half of issues; manual review remains mandatory."

| Banned claim | Scoped rewrite |
|---|---|
| certified, certifies compliance | "supports <standard> conformance work", plus who actually certifies |
| guarantees, guaranteed | the measured rate on the frozen eval set, with the set named |
| 100%, finds all, complete coverage | the counted coverage number, and what sits outside it |
| fully automated | the automation rate, plus the named human step |
| ensures compliance | the checks performed, and the ones that remain manual |
| eliminates risk | the specific risk reduced, by how much, measured how |
| real-time (when the system is batch) | the actual cadence: "refreshed every 5 minutes" |
| production-ready | the deployment it runs in, named; ELSE "tested in staging only" |
| ELSE: any superlative with no number | the number, or delete the sentence |

**The five skeptical questions.** Answered in writing, per deliverable:

1. Where did this number come from, exactly (system, query, period)?
2. What happens when the output is wrong, and who notices?
3. Who maintains this after handover, and with what runbook?
4. What did you not test?
5. Why should the demo's behaviour generalize to their data?

**The Limitations rule.** Every README and every report-class deliverable carries a Limitations section stating what the thing does NOT do: coverage boundaries, unhandled inputs, freshness limits, and the manual steps that remain. A deliverable with claims and no Limitations section is a fix, not a note.

### Inlined from writing-instructions (full skill wins on conflict)

The review report itself: full-sentence sentence-case headings, no contrast framing, no em dashes, no emoji, Canadian spelling, numbers with units and baselines, kill-list vocabulary banned (delve, robust, seamless, leverage, holistic, actionable, and kin).

## Artifact templates

```gate-card
GATE R-1 - review inventory
deliverable: <path>    type: <name>    [row: "<CHECKER MAP row, pasted verbatim>"]
audience: <who receives this file>
claims-bearing: <yes | no: does it assert capability, coverage, or results?>
(repeat the three lines per deliverable)
end-of-card
```

The claims audit, printed at GATE R-3, one row per claim found:

```claims-audit
| claim (quoted) | evidence for it | limitation stated where the reader will see it (y/n) |
|---|---|---|
| <verbatim claim> | <source: file, query, eval run> | <y, and where | n: fix required> |
end-of-audit
```

```gate-card
GATE R-5 - verdict
verdict: <SHIP | NOT-SHIP>
fixes: <none | numbered list, each with its owner skill and file>
no-mechanical-check: <none | the items covered only by reading>
skips: <none | gates skipped, with the user's words>
end-of-card
```

## Rules

| ID | Rule |
|---|---|
| R1 | Every mapped checker runs by absolute path. A missing or crashing checker is a blocking failure to report, never a skipped check. |
| R2 | Checker runs MUST appear as tool results in the conversation; typed-out output is a failed gate. |
| R3 | One FAIL anywhere holds the verdict at NOT-SHIP until the fix lands and the re-run proof line replaces the old one. |
| R4 | The claims audit covers every number, percentage, and capability claim in every claims-bearing deliverable. |
| R5 | Kill-list hits are rewritten to scoped language with a coverage number; a deleted claim is recorded in the verdict card, never removed silently. |
| R6 | Every README and report-class deliverable carries a Limitations section; absence is a fix with an owner. |
| R7 | The five skeptical questions get written answers per deliverable; an unanswerable question becomes a fix or a stated limitation in the deliverable itself. |
| R8 | The review report passes the writing sweep before delivery. |
| R9 | The reviewer never edits checker scripts and never weakens an owner skill's rule; a disputed check gets an `allow:` marker in the deliverable plus one sentence, under the owner skill's own rules. |
| R10 | The reviewer reviews; the fixes belong to the owner skill. A fix applied here still runs the owner skill's checks. |
| R11 | ELSE: a deliverable type, claim shape, or dispute this table does not cover: run the sweep on its prose, name the gap in the verdict card, and ask the user. |

## Checks

This skill ships no checker of its own. The checks are the mapped checkers of every deliverable under review (CHECKER MAP above), plus the sweep over the review report:

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <review-report.md>
```

Every run MUST appear as a tool result. Any edit to a deliverable after its checker run voids that run; re-run before the verdict.

## Delivery block

```delivery-block
DELIVERY review-deliverables
files:
  <review-report path>  (<size> B)
verdict: <SHIP | NOT-SHIP, from the R-5 card>
gates: <R-1..R-6 status, skips recorded>
checks:
  <every proof line from every mapped checker, pasted verbatim>
  <sweep proof line for the review report>
allows: <count> (<list or none>)
end-of-delivery
```
