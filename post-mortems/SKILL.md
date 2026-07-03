---
name: post-mortems
description: |
  Structured post-mortems for trading losses, incidents, outages, and failed builds.
  Trigger on: "post-mortem", "what went wrong", "we lost money on", "the run failed,
  figure out why", "incident review", "/post-mortems". Begin at GATE PM1 of THE
  CONTRACT. The sourced UTC timeline and the transitory-vs-structural verdict are the
  core artifacts; lessons ship only with an enforcement location; the dated handoff note
  plus its sweep proof line close the loop.
---

# Post-mortems

A loss teaches nothing by itself; the write-up does the teaching, and only when it names the mechanism plainly and turns the lesson into a check that fires next time. One rule governs every event here: diagnose transitory versus structural before taking any irreversible action. The worked exemplar is a nightly billing export that ran six weeks against a stale rate table. Nothing asserted the table's effective date against the run date, and the reconciliation step compared row counts instead of totals, so the drift never surfaced. Both root causes became standing gates: the date assertion now runs inside the job, and reconciliation now compares totals.

Set `SKILL_DIR=$HOME/.claude/skills/post-mortems` (fallback: `/path/to/skills/post-mortems`).

## Scope gate

IF the event is under five minutes of impact and zero dollars (a flaky test, a one-off crash with no consequence): write the one-line lesson where it belongs (a code comment, an alert rule) and stop; full ceremony would tax trivia. ELSE: run the full contract. A post-mortem MUST ship within one week of the event; past that, the details rot and the artifact quality drops with them.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE PM1** | Fill the scope card: what happened, when (UTC), blast radius | PM1 gate card (template below) | Card printed; the headline number present; no `<`, `TODO`, `TBD` |
| **GATE PM2** | Reconstruct the timeline from sources, not memory | The TIMELINE table: UTC-timestamped rows from last-known-good through detection to mitigation, each row citing its source (log path, order id, message link) | Every row sourced; gaps marked as gaps, not smoothed over |
| **GATE PM3** | Mechanism: five-whys to a falsifiable direct cause | The mechanism chain, each "why" answered by evidence from the timeline; contributing factors listed separately from the direct cause | The direct cause is falsifiable and named plainly, no passive fog |
| **GATE PM4** | Verdict: transitory or structural, with evidence | The verdict paragraph | The verdict names the evidence that would have to change to flip it |
| **GATE PM5** | Lessons as testable rule changes | The lessons table: `lesson | the rule or check that now enforces it | where it lives (file, skill, alert)` | Every lesson has a live enforcement location; "be more careful" rows are deleted |
| **GATE PM6** | Handoff: dated note plus sweep | The note at `<notes-dir>/YYYY-MM-DD-<slug>.md`, one page, plain-text links | Sweep proof line on the note pasted; DELIVERY block ends the message |

Restated because they are the three most-violated rules, binding during PM2 through PM5: every timeline row cites a source, and unsourced rows are marked "unverified" (PM-R1); the direct cause is stated plainly with its actor and mechanism ("the sizing formula multiplied by the outcome count and nothing asserted the total"), never as passive fog ("sizing issues occurred") (PM-R3); a lesson without an enforcement location is not done (PM-R5).

## Values

**Transitory versus structural (PM4).** The verdict decides what happens next, so it gets evidence, not vibes:

| Verdict | It means | Evidence that supports it | What follows |
|---|---|---|---|
| Transitory | The mechanism was a one-off outside the system's design (venue outage, fat-fingered config, a counterparty's bug) | The mechanism cannot recur without a second independent failure; base rates support rarity | Fix the immediate damage; add detection; no strategy or architecture change |
| Structural | The mechanism is built into how the system works (unasserted size math, missing edge, timezone mismatch in the join) | The mechanism recurs whenever the same code path or assumption runs | The system changes: a gate, an assertion, a halt; continuing unchanged is a decision and is written down as one |
| ELSE | Evidence is insufficient to call it | Say so, list what evidence would decide it, and set the follow-up date | Interim containment, verdict revisited on the date |

**Blast-radius units (PM1).** Dollars for money events, hours of downtime or rework for operational events, users or clients affected for product events; more than one unit when more than one applies.

**Timeline conventions (PM2).** All timestamps UTC, because the exports that feed these investigations usually bin their rows by UTC days and mixing a local zone into the timeline misorders the events around midnight. Rows are facts, one per line; interpretations live in PM3. The first row is the last known good state, so the reader sees the full window.

**Five-whys discipline (PM3).** Each "why" is answered by a timeline row or an artifact, not by plausibility. Stop when the answer is falsifiable and actionable; "market conditions" and "human error" are not stopping points, they are prompts for one more why (what made the condition lethal; what made the error easy).

## Artifact templates

```gate-card
GATE PM1 - scope card
what: <one sentence with the headline number: "the ingest job dropped 12,400 rows over 3 hours">
when: <start and end, UTC>
blast radius: <dollars / hours / users, per the units table>
detected by: <alert name | human | luck>
systems: <the components involved, by name>
end-of-card
```

The lessons table (PM5), printed in full:

```lessons
LESSON | ENFORCED BY | LIVES AT
<what we now know> | <the check, assertion, gate, or alert> | <file/skill/alert name>
end-of-lessons
```

### Inlined from writing-instructions (full skill wins on conflict)

Complete sentences, Canadian spelling, no em dashes, no emoji. No significance inflation: the event's importance is its number, not "pivotal moment". No passive fog: name the actor and the mechanism. Numbers carry units and baselines. The kill list applies (robust, seamless, learnings as a noun, and kin).

## Rules

| ID | Rule |
|---|---|
| PM-R1 | Timeline rows cite sources; unsourced rows are marked "unverified" and cannot carry the direct cause. |
| PM-R2 | Systems are named, people are not blamed: the write-up names components, code paths, and missing checks; a person appears only as "the on-call" or a role when the process around them is the finding. |
| PM-R3 | The direct cause is one falsifiable sentence with actor and mechanism; contributing factors are listed separately and do not dilute it. |
| PM-R4 | The verdict (transitory or structural) follows the evidence table; "structural but we continue unchanged" is a legitimate outcome ONLY when written down as an accepted risk with an owner. |
| PM-R5 | Every lesson lands as an enforcement: an assertion in code, a gate in a skill, an alert rule, a pre-registered criterion. The lessons table's third column is never empty. |
| PM-R6 | The handoff note is one page, dated, and lives in the project's notes directory with links as plain text. It records this incident only; a summary page that aggregates incidents is written separately, never edited from here. |
| PM-R7 | No irreversible action (selling a position, deleting data, decommissioning a system) happens before the PM4 transitory-versus-structural verdict exists; a reflexive reaction taken ahead of the verdict is itself an incident to record. For strategy events, the backtest-gauntlet halt rule governs. |
| PM-R8 | ELSE: when the contract does not fit the event, say which gate does not fit and why, then ask the user. |

## Checks

No checker script; the artifacts are the checks:

1. The TIMELINE table's every row shows a source; the two most load-bearing rows are re-verified against their sources before delivery (paste the verification).
2. The lessons table's third column is non-empty in every row, and each named location actually exists (paste `ls` or the grep that proves the check/gate/alert is live).
3. The handoff note passes the sweep:

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <notes-dir>/<date>-<slug>.md
```

Paste the `PASS sweep` proof line. A missing or crashing sweep is a blocking failure to report.

## Delivery block

```delivery-block
DELIVERY post-mortems
files:
  <handoff note path>  (<size> B)
gates: <PM1..PM6 status, skips recorded>
checks:
  timeline rows: <count>, sources verified: <the two re-checked>
  lessons: <count>, enforcement locations verified: <ls/grep evidence>
  verdict: <transitory | structural | insufficient, revisit <date>>
  <sweep proof line, pasted>
allows: <count> (<list or none>)
end-of-delivery
```
