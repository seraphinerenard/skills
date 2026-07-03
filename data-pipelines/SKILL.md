---
name: data-pipelines
description: |
  Build incremental data pipelines: downloaders, enrichers, exporters, sync jobs.
  Trigger on: "build a pipeline", "download and enrich", "sync this data", "backfill",
  "incremental update job", "/data-pipelines". Begin at GATE DP1 of THE CONTRACT.
  Every pipeline is idempotent, resumes from a high-water mark, stores UTC, and prints
  a reconciliation table after every run; the pasted reconciliation and the dry-run
  output are the mandatory checks, plus sweep.py on any runbook prose.
---

# Data pipelines

A pipeline that cannot be re-run safely is a time bomb, and a pipeline that re-fetches everything on every run gets throttled, banned, or slow. The house pattern is enrich-only-new: list what exists, fetch the delta, verify the counts, and say what "healthy" looks like. Timezone sloppiness is the recurring wound, because most exports bin their rows by UTC days and a local-time join on "date" moves every boundary row into the wrong bucket, so UTC is structural here, not advisory.

Set `SKILL_DIR=$HOME/.claude/skills/data-pipelines` (fallback: `/path/to/skills/data-pipelines`). The sweep lives at `$HOME/.claude/skills/writing-instructions/scripts/sweep.py`.

## Scope gate

IF the request is a one-off transform of a local file with no refresh ("convert this CSV to parquet"): write the script with the CONTRACT header and a `--dry-run` flag, run it, paste the output, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE DP1** | Fill the pipeline card: source, sink, key, stages, cadence, owner | DP1 gate card (template below) | Card printed; the key's date parts declared UTC; no `<`, `TODO`, `TBD` |
| **GATE DP2** | Design against the design-rules table below; write the stage list with the high-water-mark mechanism named | The stage table: `stage | input | output | idempotent because | resume via` | Every stage has a non-empty "idempotent because" and "resume via" cell |
| **GATE DP3** | Write the code: CONTRACT header comment, `--dry-run` flag, retry policy, rate-limit respect | The script(s) on disk | `--dry-run` executes end to end and prints the planned work without writing |
| **GATE DP4** | Run for real on the smallest real slice (one day, one key) | The RECONCILIATION artifact: pasted counts table | Zero unexplained drops; re-running the same slice changes nothing (paste the second run) |
| **GATE DP5** | Full run or backfill | The full-run RECONCILIATION artifact | Counts explained; high-water mark advanced and printed |
| **GATE DP6** | Deliver with the runbook line | DELIVERY block | Runbook line present; sweep proof on any prose file |

Restated because they are the three most-violated rules, binding during DP3 and DP4: re-running any stage on the same input produces the same output, byte-for-byte or row-for-row (DP-R1); timestamps are stored in UTC with the timezone in the column name, local time only at display edges (DP-R3); every run ends by printing the reconciliation counts, and an unexplained drop blocks delivery (DP-R6).

## Values

**Design rules.**

| ID | Rule |
|---|---|
| DP-R1 | Idempotent stages: re-run equals same result. Writes are upserts keyed on the natural key, or write-to-temp-then-atomic-rename. Appending without a key check is banned. |
| DP-R2 | Resume via high-water mark on the key (max date, max id, cursor token), persisted next to the sink. "Run everything again" is not a resume strategy. The enrich-only-new pattern is the default: list existing keys in the sink, fetch only the missing ones. |
| DP-R3 | Timestamps stored in UTC; the column name carries the zone (`ts_utc`, `trade_date_utc`). A source whose zone is unknown gets probed and documented before ingestion. |
| DP-R4 | Units live inside column names: `cost_cad`, `lead_weeks`, `size_usd`. A bare `amount` column is a failed review. |
| DP-R5 | Anything synthetic (test rows, sampled fixtures) uses a fixed seed, stated in the code. |
| DP-R6 | Every run prints the reconciliation table; dropped rows carry a reason and a count. |
| DP-R7 | Secrets from environment variables only; a literal token in code or logs is a blocking failure. |
| DP-R8 | The schema (tables, columns, types, units, key) is written down in a file next to the code, updated in the same commit that changes it. |
| DP-R9 | Retry policy in numbers: 3 attempts, exponential backoff starting at 2 s, retry only on transient classes (timeouts, 429, 5xx); 4xx other than 429 fails fast. The source API's published rate limit is quoted in the code comment beside the client. |
| DP-R10 | Partial-batch behaviour is declared in the card: skip-and-log (default for enrichment) or halt-all (required when later stages read earlier outputs of the same run). |
| DP-R11 | ELSE: an undecidable design point goes to the user with the two options and your recommendation, then stop. |

**The CONTRACT header.** First lines of every pipeline script:

```
# CONTRACT skill=data-pipelines key=<the natural key, e.g. trade_date_utc> hwm=<where the high-water mark lives>
# schema: <path to the schema file>   healthy: <one sentence, e.g. "daily run adds ~2,400 rows in <60 s">
```

**The `--dry-run` flag.** Mandatory. It MUST: read the high-water mark, list the keys it would fetch, print the planned row estimate and destinations, and write nothing.

**Reconciliation format.** Printed by the pipeline itself at the end of every run:

```
stage        | rows in | rows out | dropped | reason
fetch        |     n/a |    2412  |       0 |
parse        |    2412 |    2409  |       3 | malformed json, ids logged
enrich       |    2409 |    2409  |       0 |
upsert       |    2409 |    2409  |       0 | 1817 insert, 592 update
hwm: 2026-07-05 -> 2026-07-06 (UTC)
```

## Artifact templates

```gate-card
GATE DP1 - pipeline card
source: <API/db/files, with the rate limit if an API>
sink: <db/table/files>
key: <natural key; date parts are UTC>
stages: <fetch -> parse -> enrich -> upsert, or as designed>
cadence: <on demand | daily HH:MM UTC | continuous>
partial-batch: <skip-and-log | halt-all>    [row: "<the DP-R10 option that applies and why>"]
owner: <who gets the failure alert>
end-of-card
```

### Inlined from writing-instructions (full skill wins on conflict)

Runbooks and schema docs: complete sentences, Canadian spelling, no em dashes, no emoji, numbers with units. Kill list applies (robust, seamless, leverage, streamline and kin are banned in docs too).

## Rules

The design-rules table above is the rule set (DP-R1 to DP-R11). Two operational additions:

| ID | Rule |
|---|---|
| DP-R12 | Backfills run oldest-first in bounded chunks with the reconciliation printed per chunk, so an interruption resumes from the mark instead of restarting. |
| DP-R13 | A pipeline that feeds alerts follows the house alerting doctrine: the pipeline emits facts to logs; phone-bound messages are composed by an LLM from those facts, never template strings (see daemon-ops for the alert path). |
| DP-R14 | ELSE: ask the user. |

## Checks

No checker script ships with this skill; the pipeline's own output is the check:

1. `--dry-run` output pasted as a tool result at DP3.
2. The small-slice run AND its identical re-run pasted at DP4 (idempotency is demonstrated, not asserted).
3. The reconciliation table pasted for every real run; unexplained drops block.
4. Any prose file (runbook, schema doc) passes the sweep:

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <doc file>
```

Paste the proof line. A missing or crashing sweep is a blocking failure to report.

## Delivery block

```delivery-block
DELIVERY data-pipelines
files:
  <script / schema / runbook paths>  (<size> B)
gates: <DP1..DP6 status, skips recorded>
checks:
  dry-run: <one line: keys planned, rows estimated>
  reconciliation: <last run's table, pasted>
  idempotency: <second-run line showing zero changes>
  <sweep proof line for prose files>
runbook: <command> | <schedule> | logs at <path> | healthy = <one sentence>
allows: <count> (<list or none>)
end-of-delivery
```
