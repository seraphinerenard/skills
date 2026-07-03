---
name: analyze-data
description: |
  Data analysis discipline for any dataset question. Trigger on: "analyze this data",
  "what does the data say", "dig into these trades", "EDA", "profile this table",
  "why did metric X move", "/analyze-data". Begin at GATE AD1 of THE CONTRACT.
  No analysis before the pasted PROFILE artifact; no claim ships without a row in the
  CLAIMS ledger; reports pass the writing sweep (scripts/sweep.py in writing-instructions).
---

# Analyze data

Wrong analysis is worse than no analysis: a confident number that was never recomputed, a join that silently mixed timezones, a "top performer" list made of survivors. This skill makes every number traceable to a pasted command, forces the timezone question before the first join, and keeps causal language honest. The two artifacts that matter are the PROFILE (pasted, before any analysis) and the CLAIMS ledger (one row per shipped number).

Set `SKILL_DIR=$HOME/.claude/skills/analyze-data` (fallback: `/path/to/skills/analyze-data`). The sweep lives at `$HOME/.claude/skills/writing-instructions/scripts/sweep.py`.

## Scope gate

IF the request is one lookup ("how many rows", "what is the max date"): run the query, paste the command and its output, stop. IF the dataset was already profiled in this session and the CLAIMS ledger is open: add rows to the ledger and continue at GATE AD3. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT. Do not start a phase until the previous artifact exists.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE AD1** | Fill the question card: the question as a sentence, the decision it drives, dataset paths, grain, period | AD1 gate card (template below) | Card printed; no `<`, `TODO`, `TBD` |
| **GATE AD2** | Profile every dataset named on the card by RUNNING the profile commands | The PROFILE artifact: pasted tool outputs (row count, columns with types and units, nulls on key columns, min and max of every timestamp column with its timezone stated, duplicate-key check, one 5-row sample) | Every output present as a tool result; timezone of every timestamp column stated in writing |
| **GATE AD3** | Analyse. Every claim gets a ledger row the moment it is made | The CLAIMS ledger (template below), one row per claim | Every number destined for the report has a row with a pasted result and an n |
| **GATE AD4** | Build any charts through the inlined make-charts rules below | The chart files | Titles state the finding with its number; units on axes; source line present |
| **GATE AD5** | Write the report through the inlined writing rules; state uncertainty with n and the untested boundary | The report file | Every report number matches its ledger row |
| **GATE AD6** | Run the sweep on the report; fix FAILs; deliver | DELIVERY block | Sweep proof line pasted; block ends the message |

Restated because they are the three most-violated rules, binding during AD2 and AD3: a number that was not recomputed here does not ship (AD-R1); every timestamp column's timezone is stated before any date join or grouping, and cross-source joins normalize to UTC (AD-R2); "top performer" claims run the survivorship check first (AD-R6).

## Values

**The timezone law (AD-R2).** Storage and joins are UTC. Local time exists only at the display edge, labelled. The recurring trap: an export bins its rows by UTC days while the source you join it to labels its dates in a local zone, so `events.db` and `ledger.db` disagree about which day a late-evening record belongs to. Joining them on "date" without normalizing shifts every boundary row by one day and corrupts the daily totals. The PROFILE artifact MUST state, per timestamp column: name, min, max, timezone, and how the timezone was established (column name, docs, or a probe such as comparing a known event's timestamp).

**Profile commands.** Run the matching row and paste the output; run all rows that apply.

| Source | Commands |
|---|---|
| SQLite | `sqlite3 file.db ".tables"` then per table: `sqlite3 file.db "SELECT COUNT(*) FROM t;"`, `sqlite3 file.db ".schema t"`, `sqlite3 file.db "SELECT MIN(ts), MAX(ts) FROM t;"`, `sqlite3 file.db "SELECT key, COUNT(*) c FROM t GROUP BY key HAVING c>1 LIMIT 5;"`, `sqlite3 -header -column file.db "SELECT * FROM t LIMIT 5;"` |
| CSV | `wc -l f.csv`, `head -1 f.csv`, `head -6 f.csv`, and null/dup checks via the python row below |
| Parquet / mixed | `python3 -c "import pandas as pd; df=pd.read_parquet('f.parquet'); print(df.shape); print(df.dtypes); print(df.isna().sum().head(20)); print(df.head())"` |
| JSONL | `wc -l f.jsonl`, `head -3 f.jsonl`, key census: `python3 -c "import json,collections,sys; c=collections.Counter(); [c.update(json.loads(l).keys()) for l in open('f.jsonl')]; print(c)"` |
| ELSE | State the source type and ask the user for the access path, then stop |

**Uncertainty phrasing (AD-R4).** Every finding carries: the n it rests on, the period it covers, and one sentence naming what was not tested ("untested on markets opened after the V2 migration; those are 11% of rows"). A finding without an n is a guess.

**Causal language (AD-R5).**

| You have | You may write |
|---|---|
| A correlation | "X moves with Y" and the coefficient with n |
| Correlation plus a named mechanism | "X moves with Y; the candidate mechanism is Z" plus the test that would confirm Z |
| An intervention or natural experiment, tested | "X caused Y" with the test and its result |
| ELSE | No causal verb: no "drove", "led to", "because of" |

## Artifact templates

```gate-card
GATE AD1 - question card
question: <the question, one sentence>
decision: <what the reader does differently depending on the answer>
datasets: <path(s)>
grain: <one row is one what>
period: <dates covered, with timezone>
end-of-card
```

The CLAIMS ledger, maintained from the first claim onward and printed in full before GATE AD5:

```claims-ledger
CLAIM | EVIDENCE (exact query or script path) | RESULT (pasted) | N
<the sentence as it will appear> | <command> | <output> | <sample size>
end-of-ledger
```

### Inlined from writing-instructions (full skill wins on conflict)

Headings are complete sentences in sentence case. No contrast framing ("it's not X, it's Y"). No em dashes, no emoji. Numbers carry units, baselines, and sources. Kill list: delve, robust, seamless, leverage, streamline, unlock, elevate, empower, holistic, synergy, actionable, stakeholders, significant (without the number), landscape (figurative). Canadian spelling: colour, centre, behaviour, analyze (keep -ize).

### Inlined from make-charts (full skill wins on conflict)

Chart titles are full sentences stating the finding, with the number in them. Axis labels carry units. Source line under every chart: system, period, retrieved date. Bars start at zero; no pie, donut, or gauge; direct labels over legends; greys plus one accent. Load the full make-charts skill for anything beyond a single-panel chart.

## Rules

| ID | Rule |
|---|---|
| AD-R1 | A number that was not recomputed in this session does not ship. Quoting a number from a prior report, a filename, or memory is a failed gate; recompute it and ledger it. |
| AD-R2 | Timestamp columns get their timezone stated at AD2; cross-source date joins normalize to UTC; local-time grouping is allowed only when the card says the decision is local-time-shaped, and the report says so. |
| AD-R3 | Denominators are named: "11 of 148 loads (7.4%)", never a lone percentage. Rates under n=30 are reported as counts. |
| AD-R4 | Every finding states its n, period, and untested boundary. |
| AD-R5 | Causal verbs follow the causal-language table. Correlation stays correlational. |
| AD-R6 | Any ranking or "top performers" claim runs a survivorship check first: state what left the sample during the period and how many; rankings on survivors only are labelled as such. |
| AD-R7 | Outliers are inspected before they are dropped; a dropped row class gets a ledger row of its own with the count and the reason. |
| AD-R8 | Percent changes name the base ("up 40% from 10 to 14 per day"); changes on bases under 20 are reported as raw counts. |
| AD-R9 | The report's headline answers the AD1 question directly; findings that do not bear on the question go to an appendix or die. |
| AD-R10 | ELSE: a situation these rules do not cover gets decided by AD-R1 logic (trace it or drop it); when that fails, ask the user. |

## Checks

No checker script ships with this skill; the artifacts are the checks:

1. The PROFILE outputs MUST be tool results in this conversation, not typed text.
2. The CLAIMS ledger MUST be printed in full before the report is written, and every report number MUST match a ledger row. Spot-check rule: before delivery, re-run the ledger's two most load-bearing queries and confirm the results match the ledger.
3. The report file passes the sweep:

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <report file>
```

Paste the `PASS sweep v1 file=<name> sha=<8hex>` proof line into the delivery block. A missing or crashing sweep is a blocking failure to report, never a licence to self-attest.

## Delivery block

```delivery-block
DELIVERY analyze-data
files:
  <report / chart paths>  (<size> B)
gates: <AD1..AD6 status, skips recorded>
checks:
  ledger rows: <count>, spot-checked: <the two claims re-run>
  <sweep proof line, pasted>
allows: <count> (<list or none>)
end-of-delivery
```
