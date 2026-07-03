# Backend contract

The reference implementation is `templates/northline/backend/`. This file states the contract so a rebuild on another stack (Node, warehouse-backed, multi-tenant) keeps the same shape.

## Layers

```
store (SQLite / warehouse)
  ├── views API  — GET endpoints the panels read
  ├── engine     — the domain maths (forecast, consumption, cover, exposure,
  │                order plan), exposed as endpoints AND as agent tools
  └── agent      — Claude tool-use loop, exposed as SSE endpoints (chat,
                   recommendations)
```

Panels and agent tools query the same store through the same engine. The moment the agent reads a copy or re-derives the maths, chat answers and panels drift apart and trust dies. The what-if simulator is the same engine with parameters, never a second implementation.

## Endpoints (reference app)

| Route | Returns |
|---|---|
| `GET /api/kpis` | Headline numbers: `{skus_tracked, critical, warning, service_level_pct, at_risk_cad, avg_cover_weeks, as_of}` |
| `GET /api/insights` | The Overview feed: computed findings `{severity, title, body}` with the triggering numbers in the body |
| `GET /api/demand` | Per-model demand summaries with recent weekly series |
| `GET /api/demand-forecast?model_id=&weeks=` | `{history, forecast: [{week, mean, lo, hi}], backtest_mape, baseline_mape}` |
| `GET /api/inventory` | The full engine output: per-component cover and status, exposure, units at risk, order plan, supplier concentration |
| `POST /api/whatif` | Baseline vs scenario engine runs for `{demand_pct, lead_delta_weeks, service_level, risk_tolerance, budget_cad}` |
| `POST /api/chat` | SSE stream (below) |
| `POST /api/recommendations` | The same SSE stream, driven by a fixed procurement prompt with a strict output format the view parses into cards |

Every payload carries `as_of` (ISO date of the freshest row) so panels can show their staleness honestly.

## SSE event shapes

`POST /api/chat` takes `{"messages": [{role, content}, ...]}` and streams `text/event-stream`. Each event is one JSON line:

```json
{"type": "delta", "text": "The battery pack holds 0.5 weeks "}
{"type": "tool", "name": "run_sql", "input": {"query": "SELECT ..."}, "summary": "8 rows"}
{"type": "done"}
{"type": "error", "message": "..."}
```

Rules: emit `tool` events the moment the call is made, before the result exists if the call is slow; the client renders each as a step. `delta` events carry raw text only. Exactly one `done` terminates the stream.

## Agent tools

Three tools, defined once, with tight schemas:

```json
{"name": "describe_schema", "description": "Tables, columns, and row counts of the operations store.",
 "input_schema": {"type": "object", "properties": {}}}

{"name": "run_sql", "description": "Run one read-only SELECT against the store. One statement, no writes.",
 "input_schema": {"type": "object", "properties": {"query": {"type": "string"}},
                  "required": ["query"]}}

{"name": "get_demand_forecast", "description": "Weekly order forecast for a bus model: mean and 80% interval, plus holdout MAPE.",
 "input_schema": {"type": "object", "properties": {"model_id": {"type": "integer"},
                  "weeks": {"type": "integer"}}, "required": ["model_id"]}}

{"name": "get_inventory_status", "description": "The computed inventory position: cover vs lead time, statuses, exposure, and the order plan. Use instead of re-deriving stock maths in SQL.",
 "input_schema": {"type": "object", "properties": {}}}
```

`run_sql` guards, all three mandatory:

1. Connection opened read-only (`sqlite3.connect("file:northline.db?mode=ro", uri=True)`).
2. Statement must start with `SELECT` or `WITH` after stripping whitespace and comments; reject `;` beyond a trailing one.
3. Row cap (500) and a statement timeout, so a runaway join cannot stall the stream.

The system prompt carries the data contract: what each table means, the units (orders/week, CAD, weeks of cover), the date range loaded, and the instruction to decline questions outside the data rather than guess. It also instructs the agent to give numbers with baselines, per writing-instructions.

## Provider resolution

The analyst should run with whatever credential the machine has, so the demo never dies on a missing key. The template resolves in this order (forceable with `NORTHLINE_PROVIDER`):

| Credential found | Driver |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic SDK, native tool use, streamed |
| `OPENAI_API_KEY` | OpenAI SDK, function calling, streamed |
| `GITHUB_TOKEN` | GitHub Models through the OpenAI SDK (`https://models.github.ai/inference`, model ids like `openai/gpt-4o`) |
| none | Claude Agent SDK riding the machine's Claude Code login |

Rules that keep the fallbacks safe: the OpenAI and GitHub paths share one driver (only `base_url` and model differ); the Claude Agent SDK path disables the built-in filesystem and shell tools (`tools=[]`), exposes only the three data tools through an in-process MCP server, bypasses permission prompts because those tools are read-only, and ignores the host machine's settings (`setting_sources=[]`). Every driver emits the same SSE event shapes, so the frontend never knows which provider answered.

## Forecasting

`forecast.py` in the template fits Holt-Winters (yearly seasonality on weekly demand, `statsmodels` `ExponentialSmoothing`) per bus model and reports a seasonal-naive baseline. Contract:

- Backtest first: hold out a trailing window (13 weeks in the template), fit on the rest, report MAPE for both the model and the naive baseline. If the model does not beat naive, serve naive and say so in the payload (`"model": "seasonal_naive"`).
- Intervals from holdout residuals (empirical 10th/90th percentiles), never from a formula the data has not earned.
- The endpoint and the agent tool call the same function.

## Seeding synthetic data

`seed.py` is the executable data contract. Rules that make demo data believable:

- Fixed seed (`numpy.random.default_rng(11)`), so every rebuild produces identical numbers and screenshots stay true.
- Shape before noise: base level per series, seasonality (school districts order in winter and spring), a trend per product line (the electric model grows), then noise last.
- Events with consequences: an industry-wide chassis shortage that visibly dents one autumn. Reviewers look for cause and effect.
- Units in column names (`unit_cost_cad`, `lead_time_weeks`) so the agent's SQL answers carry units without guessing.
