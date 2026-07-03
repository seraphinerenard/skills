# Northline Coachworks — agentic dashboard reference app

Northline Coachworks is a fictional school-bus manufacturer. This app is the dashboarding skill's quality target: a BI replacement with six views, a FastAPI backend over a seeded SQLite store, a Vite + React + Tailwind v4 frontend, and a Claude analyst wired into every AI surface. Copy it, replace `seed.py` with the client's data contract, and rename everything.

The demand-to-inventory chain drives the whole app: weekly order forecasts per bus model translate through the bill of materials into component consumption, which meets stock, open purchase orders, and supplier lead times.

## Run it

Backend (Python 3.11+):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py                       # writes northline.db (fixed seed, reproducible)
uvicorn app:app --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev                          # http://localhost:5173, proxies /api to :8000
```

The AI surfaces (chat dock, agent hub, recommendations) pick their credential automatically; every other view works with none at all. Light theme by default; the top-bar toggle persists per browser.

Platform interactions: Cmd/Ctrl+K opens the command palette (views, components, actions); clicking any component row opens the detail drawer with its position, BOM usage, open POs, and a draft-PO action; tables sort on click and export to CSV; every action confirms with a toast.

The agent can act: ask it to order something and it drafts purchase orders into the Agent hub's procurement queue. Approving a draft writes a real PO with the supplier's lead time and the whole dashboard reprices. The goal optimizer searches order plans against a service target and budget and can send its plan to the same queue.

## The eight views

| View | What it answers |
|---|---|
| Overview | The insight feed (stockout risk, revenue exposure, supplier concentration), the KPI row, status by category, demand snapshot |
| Demand forecast | Weekly order intake per bus model: history, forecast with 80% interval, holdout MAPE against a seasonal-naive baseline |
| Inventory health | Per-component effective cover vs supplier lead time, shortfalls, blocked production value, supplier concentration |
| AI recommendations | The analyst turns the inventory position into a priced, prioritized order list, tool calls visible |
| Suppliers | Risk scorecards ranked by critical SKUs and spend at stake, with each supplier's book |
| Production plan | Week-by-week constrained build simulation: buildable vs demand, the gating component, and the committed-horizon loss |
| What-if simulator | Global and granular levers (per-model demand, per-supplier lead times) over the full stock maths |
| Agent hub | Four surfaces: the analyst desk, the goal optimizer (spend-vs-exposure frontier), the procurement approval queue, and the alert feed |

## What is inside

| Path | Job |
|---|---|
| `backend/seed.py` | The executable data contract: 3 bus models, 26 components, 10 suppliers, a BOM with option take rates, 3 years of weekly demand, stock and open POs. Fixed seed 11. |
| `backend/forecast.py` | Holt-Winters vs seasonal-naive on weekly demand; serves whichever wins the 13-week holdout, with empirical 80% intervals. |
| `backend/stock.py` | The inventory engine: forecast consumption through the BOM, effective cover vs lead time, status bands, revenue exposure, the order plan, and the what-if scenario maths. |
| `backend/insights.py` | The Overview feed: computed findings with the numbers that triggered them. |
| `backend/agent.py` | The analyst: multi-provider tool-use loop with `describe_schema`, read-only `run_sql`, `get_demand_forecast`, `get_inventory_status`. |
| `backend/app.py` | View endpoints plus SSE `/api/chat` and `/api/recommendations`. |
| `frontend/src/views/` | The six views; `components/` holds the shared panels, charts, and the chat. |

## Providers

The analyst resolves its credential in this order; set `NORTHLINE_PROVIDER` to force one.

| Provider | Selected when | SDK and model |
|---|---|---|
| `anthropic` | `ANTHROPIC_API_KEY` is set | Anthropic SDK; `NORTHLINE_MODEL`, default `claude-opus-4-8` |
| `openai` | `OPENAI_API_KEY` is set | OpenAI SDK; `NORTHLINE_OPENAI_MODEL`, default `gpt-4o` |
| `github` | `GITHUB_TOKEN` is set | GitHub Models via the OpenAI SDK against `https://models.github.ai/inference`; `NORTHLINE_GITHUB_MODEL`, default `openai/gpt-4o` |
| `claude-code` | no key at all | Claude Agent SDK, riding this machine's Claude Code login; `NORTHLINE_MODEL` optional |

The `claude-code` path needs the `claude` CLI installed and logged in; the agent runs with the built-in tools disabled, permissions bypassed for its own read-only data tools, and this machine's settings ignored (`setting_sources=[]`).

The database opens read-only everywhere except `seed.py`, and `run_sql` accepts only single SELECT/WITH statements capped at 500 rows.
