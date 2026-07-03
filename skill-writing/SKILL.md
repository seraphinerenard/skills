---
name: skill-writing
description: |
  Author or revise skills in this repo. Trigger on: "write a skill", "new skill",
  "update the X skill", "make this skill hard-gated", "/skill-writing".
  This file defines THE PROTOCOL every skill in the repo follows: contract phases,
  gate cards, rule IDs, checker conventions, and the delivery block. Begin at GATE S1
  of THE CONTRACT. Conformance is checked by scripts/check_skill.py, which is mandatory.
---

# Skill writing

Skills in this repo are executed by small models. A small model does not follow doctrine; it follows procedure. It skips files it is told to "see", treats hedged rules as optional, narrates checks instead of running them, and improvises any value it was not handed. Every mechanism in this protocol removes one of those failure routes. A skill is not an essay about quality; it is a machine that a weak operator cannot run incorrectly.

Set `SKILL_DIR=$HOME/.claude/skills/skill-writing` (fallback: `/path/to/skills/skill-writing`).

## Scope gate

IF the request is a wording fix or a single-value change to an existing conforming skill: make the edit, run `python3 $SKILL_DIR/scripts/check_skill.py <file>`, paste the proof line, stop. ELSE: run the full contract below.

## The contract

Do the phases in order. Each phase ends with its REQUIRED ARTIFACT. Do not start a phase until the previous artifact exists. Print the contract card (template below) at every phase transition.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE S1** | Read the target domain material; list the 5 to 10 failure modes a small model will hit in this domain | S1 gate card: skill name, prefix, trigger phrases, failure-mode list | Card printed; no `<`, `TODO`, or `TBD` in it |
| **GATE S2** | Decide the phases the skill enforces and the artifact each produces | S2 contract table (same 4-column shape as this one) | Every phase has an artifact a reader can verify exists; at most 7 phases |
| **GATE S3** | Write the VALUES section: every number, hex, size, and name the executor will need, inline | The VALUES section draft | Zero values delegated to references; zero values left to judgment |
| **GATE S4** | Write SKILL.md in the layout-law section order; write starters and the checker | The files on disk | `python3 $SKILL_DIR/scripts/check_skill.py <skill>/SKILL.md` exits 0 |
| **GATE S5** | Dry-run one realistic task through the skill, phase by phase, as a hostile lazy reader | One-paragraph dry-run note naming what a lazy reader could still evade, and the fix applied | Note printed; fixes applied |
| **GATE S6** | Deliver | DELIVERY block (template below) | Proof lines pasted from real runs; block is the final content of the final message |

## Values

**The layout law.** Every SKILL.md uses exactly these sections, in this order. Nothing binding appears after line 400; the file is at most 420 lines.

1. Frontmatter: `name`, `description` (trigger phrases, prerequisites, "begin at GATE 1", checker name).
2. `# Title`, a purpose paragraph of at most 5 lines, then the `SKILL_DIR=` line.
3. `## Scope gate`: the trivial-revision exemption, as an IF/ELSE.
4. `## The contract`: at most 40 lines, at most 7 phases, the 4-column table above.
5. `## Values`: every binding number, token block, palette, size table, and budget, inline.
6. `## Artifact templates`: fenced blocks the executor fills in.
7. `## Rules`: ID'd tables, described below.
8. `## Checks`: exact commands and what their output must look like.
9. `## Delivery block`: the skill's filled-block template.
10. `## References` (optional): rationale and depth only, never binding values.

**The language law.**

- Every requirement is MUST or a table row. The hedge words `prefer`, `consider`, `generally`, `ideally`, `where possible`, `try to`, `aim for`, `as appropriate`, `if possible` are banned in skill files; the checker flags them.
- Every decision table ends with an ELSE row (a default, or "ask the user, then stop").
- Rules carry IDs (`D7`, `W12`). Artifacts cite the matched row verbatim. Checkers print IDs on failure, so "fix D7" is a followable instruction.
- Bold is reserved for gate names. A model scanning bold text must be scanning gates.
- The three rules of the skill most violated in practice are restated verbatim inside the phase where the violation happens, not only in the Rules section.
- Skill files use Canadian English, no emoji, no em dashes (the glyph appears only inside code fences that document patterns).

**The prefix registry.** One prefix per skill, used in rule IDs and gate names:

| Prefix | Skill | Prefix | Skill |
|---|---|---|---|
| W | writing-instructions | P | write-proposals |
| D | design | DOC | make-documents |
| C | make-charts | CC | client-comms |
| V | make-videos | AD | analyze-data |
| I | ideation | R | review-deliverables |
| DB | dashboarding | DI | discovery |
| E | ai-engagements | BK | brand-kit |
| S | skill-writing | DR | demo-reframe |
| AA | accessibility-audit | M | publish-mcp-tools |
| PM | post-mortems | BG | backtest-gauntlet |
| DP | data-pipelines | DO | daemon-ops |
| RF | realtime-feeds | WP | write-papers |

**Checker conventions.** Every checker script MUST:

- Be python3, standard library only (BSD grep has no `-P`; shell sweeps died silently for months).
- Take file paths as arguments: `python3 $SKILL_DIR/scripts/<checker>.py FILE...`
- Print one line per violation: `FAIL <RULE-ID> <file>:<line> <short description>`.
- Honour escape markers `allow:<RULE-ID> <reason>` inside any comment syntax, print each as `ALLOW <RULE-ID> <file>:<line> <reason>`, and count them.
- End each clean file with the proof line: `PASS <checker-name> v<N> file=<basename> sha=<first 8 hex of sha256>`.
- Exit 0 only when every file passed; otherwise exit 1.

The proof line is the anti-fabrication device: a model cannot guess the sha, so a pasted proof line is evidence the run happened. State in every skill: the checker run MUST appear as a tool result in the conversation (typed-out output is a failed gate); any file edit after the run voids it (checks are the last action before delivery); a missing or crashing checker is a blocking failure to report, never a licence to self-attest.

**Starter conventions ("copy, don't create").** Deliverables begin as a `cp` of a shipped starter, never as a new empty file. Each starter carries sentinel comments (`@keep:tokens`, `@keep:reduced-motion`, `@keep:eof`) that the skill's checker requires in delivered files, which proves the copy happened. State the exact `cp` command with `$SKILL_DIR` in the skill. IF the `cp` fails: stop and report the path; starting from scratch is a failed gate.

**The contract comment.** Gate-card decisions are embedded in the deliverable itself, so they survive context loss and let the checker cross-validate declared against shipped:

```
<!-- CONTRACT skill=design surface=product-ui palette=mono-pop body=16px accent=#1f4ed8 -->
/* CONTRACT skill=make-videos mode=B palette=broadcast-dark scenes=7 */
# CONTRACT skill=data-pipelines stage=enrich keys=utc-date
```

**Dependency inlining.** A skill that requires another skill inlines the minimal operative subset (for writing-instructions: the kill list and the title rule; for make-charts: the five non-negotiables) under a heading `### Inlined from <skill> (full skill wins on conflict)`. A hop the executor need not take is a hop it cannot fumble.

## Artifact templates

**Gate card.** Fixed info-string, fixed first and last lines. A card containing `<`, `TODO`, or `TBD` is a failed gate; the recovery is to fill it now. One gate card per response: printing two in one message means the work between them was skipped. Fields that cite a decision table MUST quote the matched row verbatim in the `row:` bracket, including the ELSE row when it matched.

```gate-card
GATE <PREFIX><n> - <gate name>
<field>: <value>    [row: "<verbatim citation of the matched table row>"]
<field>: <value>
end-of-card
```

**Contract card.** Printed at every phase transition, 5 lines, no more:

```contract-card
done: <phase just finished>, artifact: <its artifact, by name>
now: <phase starting>
next gate: <the artifact that ends it>
end-of-card
```

**Delivery block.** The final content of the final message; nothing follows it. No checkboxes, paste slots only:

```delivery-block
DELIVERY <skill-name>
files:
  <path>  (<size> B)
gates: <G1 done, G2 done, ... | G3 SKIPPED (user said: "...")>
checks:
  <proof line(s) pasted verbatim from tool output>
allows: <count> (<rule-id list, or "none">)
end-of-delivery
```

**Gate-skip audit.** IF the user tells you to skip a gate: confirm once in one sentence, proceed, and record `GATE <id> SKIPPED (user)` in the delivery block. Skipping silently and skipping without recording are both failures.

**AskUserQuestion gates.** Where a skill requires the user to choose (stories, palettes, scope), the choice MUST be an AskUserQuestion tool call. IF that tool is unavailable: present the options as text and STOP the turn; choosing for the user is a failed gate.

## Rules

| ID | Rule |
|---|---|
| S1 | Every binding value (hex, px, pt, seconds, counts, budgets, names) appears inline in SKILL.md. References hold rationale and depth only. |
| S2 | Every phase produces an artifact whose existence a reader can verify in the conversation or on disk. "Think about X" is not a phase. |
| S3 | Judgment calls are converted to IF/THEN tables with exact numbers and an ELSE row, or deleted. |
| S4 | Checkers are python3 stdlib, print rule IDs and proof lines, exit nonzero on failure. |
| S5 | Deliverables start from a shipped starter via `cp`; starters carry `@keep` sentinels the checker requires. |
| S6 | SKILL.md is at most 420 lines; frontmatter description states the triggers, the first gate, and the checker. |
| S7 | Hedge words are banned; requirements are MUST or table rows; decision tables end with an ELSE row. |
| S8 | An artifact containing `<`, `TODO`, or `TBD` is a failed gate; fill it now, do not proceed. |
| S9 | Skill files use Canadian English, no emoji, no em dashes outside code fences. |
| S10 | Scripts are read-only for executors: a disputed check gets an `allow:` marker plus one sentence, never a script edit. |
| S11 | ELSE, for any situation this table does not cover: stop and ask the user. |

## Checks

```
python3 $SKILL_DIR/scripts/check_skill.py <path-to-SKILL.md> [more paths...]
```

Validates: section order per the layout law, the 420-line cap, the hedge-word ban, gate-card and delivery-block fences present, frontmatter fields, prefix registered, no emoji or em dashes outside fences. Output ends `PASS check_skill v1 file=SKILL.md sha=<8hex>` per clean file, exit 0. Run it on the skill you wrote and paste the proof line into your delivery block. The run MUST appear as a tool result; any edit after the run voids it.

## Delivery block

```delivery-block
DELIVERY skill-writing
files:
  <each file written, with size>
gates: <S1..S6 status>
checks:
  <check_skill proof lines, pasted>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- `references/rationale.md`: why each mechanism exists, with the observed small-model evasion it closes. Read when designing a new enforcement mechanism, not during routine authoring.
