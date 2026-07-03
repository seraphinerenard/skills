---
name: dashboarding
description: |
  Build agentic dashboards that replace a BI stack: a data layer, tool-calling analyst
  agents, forecasting views, and a chat dock that pins answers as panels. Trigger on:
  "build a dashboard", "agentic BI", "replace our reports", "operations dashboard",
  "add a chat analyst", "/dashboarding". Begin at GATE DB-1 of THE CONTRACT: the
  questions table is approved before any code. Deliverables start as a cp of
  templates/northline/ (a runnable reference app, fictional school-bus manufacturer);
  the writing sweep and the DB-5 round-trip commands are the mandatory checks.
  Design and make-charts prerequisites inlined; the full skills win on conflict.
---

# Dashboarding

A dashboard built by this skill answers named business questions. Every panel exists because an operator asked something specific, and the panel title states the current answer as a full sentence computed from the data. The analyst agent holds the SQL and forecast tools; answers worth keeping get pinned as panels, and that loop is what replaces the BI stack. A grid of unasked-for widgets is the failure mode this skill exists to prevent.

Set `SKILL_DIR=$HOME/.claude/skills/dashboarding` (fallback: `/path/to/skills/dashboarding`).

## Scope gate

IF the request edits a dashboard that already has a questions table and rename ledger: make the edit, rerun the DB-5 round trip the edit touches plus the sweep, paste the outputs, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE DB-1** | Name the 5 to 10 business questions | Questions table (template below), user-approved | Every row has owner, decision, and the answering table; approval quoted (AskUserQuestion where available; ELSE present and stop) |
| **GATE DB-2** | Write the data contract | Data-contract card | Tables, grain, units, refresh cadence, as_of source, all filled |
| **GATE DB-3** | `cp -r $SKILL_DIR/templates/northline <target>` and reframe it | RENAME LEDGER (template below) | `cp` ran as a tool call; every ledger row has a fictional replacement; IF `cp` fails, stop and report the path |
| **GATE DB-4** | Adapt seed, engine, views, and agent tools to the contract | The running app (backend and frontend start) | Panel titles computed from data, never hardcoded; each panel cites its questions-table row |
| **GATE DB-5** | Run the round-trip verifications | The round-trip block (template below) with pasted outputs | All six round trips pasted from real tool results |
| **GATE DB-6** | Sweep the copy | Sweep proof line on view/copy source files | `PASS sweep` as a tool result |
| **GATE DB-7** | Deliver | DELIVERY block | Proof lines and round-trip block referenced; block ends the message |

Restated because they are the three most-violated rules: a panel with no questions-table row does not get built (DB1); the agent and the panels read the same store through the same engine, never a copy (DB6); `run_sql` is read-only and gated, and the refusals are pasted, not narrated (DB3).

## Values

**The three layers.** Store (SQLite in the template; swap for the warehouse) feeds a views API, a domain engine (forecast, cover, exposure, order plan), and the agent, which exposes the SAME engine as tools. The what-if simulator is the same engine with parameters, never a second implementation. Wiring detail: `references/architecture.md`.

**The chat dock.** Bottom-right pill, expanded to a 400px column at max 70vh, never a modal over the dashboard it talks about. Streams from the first token (a dead cursor for four seconds reads as a hang). Every tool call renders as a collapsed step ("run_sql, 8 rows") expanding to the exact SQL and result. Every completed answer offers Pin as panel (pin stores question, answer, steps, pinnedAt). The agent declines questions the data cannot answer and names the missing data. SSE event shapes (`delta`, `tool`, `done`, `error`) are in `references/architecture.md`; frontend parsing patterns in `references/frontend-patterns.md`.

**`run_sql` guards, all three mandatory.** Connection opened read-only (`file:<db>?mode=ro`); statement MUST start with SELECT or WITH after stripping whitespace and comments, one statement only; row cap 500 and a statement timeout.

**Forecast panels.** One chart shows history (solid, brighter), the forecast mean (dashed), and the interval band (accent at 12 to 15% opacity). The subtitle states the backtest: "MAPE 6.2% on the last 13 held-out weeks". Backtest against a seasonal-naive baseline; IF the model does not beat naive, serve naive and say so in the payload. Intervals come from holdout residuals, never a formula the data has not earned.

**Views.** A BI replacement is a multi-view product: an Overview answering "what needs action today", one view per question family (demand, supply, money), one view where the agent proposes actions, one simulator, and one agent desk; left sidebar with the brand block; the dock on every view. Platform components (all under a hundred lines each against the design tokens): command palette (Cmd/Ctrl+K), right-side detail drawer, tabs for sibling analyses, sortable columns with CSV export, sparklines in table cells, toasts, persisted light/dark toggle.

**The dashboard acts.** Agents draft actions into an approval queue; a person approves; approval writes to the store and every panel reprices; the queue is the audit trail. A goal optimizer takes named constraints (service target, budget, risk tolerance) and shows the trade-off frontier, never one asserted answer. Watchers run standing rules (stockout countdowns, arriving POs, demand outside the band) on the same engine.

**Seeded data.** Fixed seed (`numpy.random.default_rng(11)` in the template); shape before noise (base level, seasonality, trend, then noise); events with consequences (a shortage that visibly dents one autumn); units in column names (`unit_cost_cad`, `lead_time_weeks`).

**Theming and motion.** One brand hue across light and dark themes; the warning tier gets its own colour, never the brand accent; toggle persisted. Motion: entrances once (cards rise with a 60ms stagger, charts draw via stroke-dashoffset, KPI numbers count up on mount), 200 to 900ms, one easing curve, everything collapses under prefers-reduced-motion. The one sanctioned loop is a breathing status dot, marked `allow:D11`.

### Inlined from design (full skill wins on conflict)

The dashboard is product UI: 16px body, 13 to 14px table cells with `font-variant-numeric: tabular-nums`, rows 36 to 44px. All colour decisions live in the token/theme layer (Tailwind theme or CSS custom properties), which is rule D2's spirit; no colour literals scattered through components. No gradients, no glass, no pure #000000, no emoji, one accent under 80% saturation, semantic colours reserved. Any standalone HTML the dashboard ships MUST pass `check_design.py`.

### Inlined from make-charts and writing-instructions (full skills win on conflict)

Chart titles are full sentences computed from the data ("Four components run out before their suppliers can deliver"); axis labels carry units; direct labels over legends; no pie, donut, or gauge; bars start at zero. Panel copy: sentence-case full sentences, numbers with units and baselines, an "as of" stamp per panel, no em dashes, no emoji, Canadian spelling, fictional names only.

## Artifact templates

Questions table (GATE DB-1):

```
| # | question (full sentence) | owner | decision it drives | answering table/view |
|---|---|---|---|---|
| 1 | Which components stop the production line next month? | procurement lead | reorder or expedite | inventory + engine cover |
APPROVAL: <the user's approval, quoted>
```

```gate-card
GATE DB-2 - data contract
tables: <name (grain, key columns with units)> per table
refresh: <cadence per table>
as_of: <the column or query that dates every payload>
boundaries: <what the data cannot answer>
end-of-card
```

RENAME LEDGER (GATE DB-3), one row per replacement, fictional names only:

```
| northline item | replacement |
|---|---|
| Northline Coachworks (brand) | <fictional client name> |
| bus models (per seed.py) | <the vertical's entities> |
| seed.py series and events | <vertical-appropriate seasonality, trend, one named event; fixed seed kept> |
| brand tokens (frontend theme) | <client palette mapped onto the token roles> |
| view names and questions list | <from the DB-1 table> |
```

Round-trip block (GATE DB-5). Run each command; paste real output under it:

```
1 as_of:      curl -s localhost:<port>/api/kpis        -> payload shows as_of
2 sql gate:   POST run_sql "DROP TABLE components"      -> refusal pasted
              POST run_sql "INSERT INTO components VALUES (1)" -> refusal pasted
              POST run_sql "SELECT 1; SELECT 2"          -> refusal pasted
              POST run_sql "UPDATE components SET qty=0" -> refusal pasted
3 chat:       one question in -> tool steps visible -> streamed answer -> pin works
4 act:        agent drafts an order -> approval writes -> KPIs reprice (before/after pasted)
5 decline:    an unanswerable question ("What is driver satisfaction?") -> the agent names the missing data
6 reconcile:  one KPI number vs a hand-run SQL query -> both pasted, equal
```

## Rules

| ID | Rule |
|---|---|
| DB1 | Every panel maps to a questions-table row; its title is a full sentence stating the current answer, computed from the same queries the agent would run. |
| DB2 | The dock streams from the first token, renders every tool call as an expandable step with the exact SQL, offers Pin as panel on every answer, and declines outside-contract questions by naming the missing data. |
| DB3 | `run_sql`: read-only connection, SELECT/WITH prefix only, single statement, row cap 500, timeout. The four refusal payloads in the round-trip block are pasted, never narrated. |
| DB4 | Forecast panels show history, band, and holdout error; never a lone point estimate; the forecast is visually subordinate to history. |
| DB5 | KPI tiles are monochrome with the single accent reserved for the tile that crossed a threshold. No gauges, no donuts, no five-colour rows, no "AI Insights" lightbulb card, no auto-refresh spinners (a quiet "as of 14:32" stamp instead), no emoji. |
| DB6 | Panels, agent tools, watchers, optimizer, and simulator all read the same store through the same engine; a snapshot copy or re-derived maths is how chat answers and panels drift apart and trust dies. |
| DB7 | Demo data is seeded with a fixed seed, shaped (trend, seasonality, one named event with consequences), and carries units in column names. |
| DB8 | Actions go through the approval queue; the agent never commits spend; approval writes to the store and panels reprice. |
| DB9 | New panels appear only through pin-as-panel or a new questions-table row; panels nobody reads get retired. |
| DB10 | A modal chat window covering the dashboard is banned; the dock sits beside the panels it cites. |
| DB11 | ELSE: a situation this table does not cover follows the northline template's existing pattern; IF the template has none, ask the user. |

## Checks

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <view/copy source files>
python3 $HOME/.claude/skills/design/scripts/check_design.py <any standalone .html shipped>
```

Plus the six round trips in the DB-5 block, each pasted from a real tool result. The sweep and check_design runs MUST appear as tool results; a missing or crashing checker is a blocking failure to report. The round-trip block is the functional check: a dashboard whose refusals, reprice, and reconcile outputs cannot be pasted is not done.

## Delivery block

```delivery-block
DELIVERY dashboarding
files:
  <paths: backend, frontend, seed, README>  (<size> B each)
gates: <DB-1..DB-7 status, skips recorded>
checks:
  <sweep proof line, pasted>
  <check_design proof line if standalone HTML shipped>
  round-trips: <1..6 pass, block printed at GATE DB-5>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- `references/architecture.md`: endpoints, SSE event shapes, tool schemas, provider resolution, forecasting contract, seeding rules.
- `references/frontend-patterns.md`: app skeleton, KPI header, chart, table, dock streaming code, pin-as-panel, the four states.
- `templates/northline/`: the runnable reference app (FastAPI + SSE backend, Vite + React + Tailwind v4 frontend, light and dark themes); its README is the quality target for handover docs.
