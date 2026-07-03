"""The Northline analyst: one tool-calling loop, four credential paths.

Provider resolution (override with NORTHLINE_PROVIDER=anthropic|openai|github|claude-code):
  ANTHROPIC_API_KEY  -> Anthropic SDK
  OPENAI_API_KEY     -> OpenAI SDK
  GITHUB_TOKEN       -> GitHub Models (OpenAI-compatible endpoint)
  none of the above  -> Claude Agent SDK, riding the local Claude Code login

Tools: describe_schema, run_sql (read-only, SELECT-gated), get_forecast.
stream_chat() is an async generator; the SSE endpoint serializes one dict per frame:
  {"type": "delta", "text": ...}
  {"type": "tool", "name": ..., "input": {...}, "summary": ...}
  {"type": "error", "message": ...}
"""

import json
import os
import sqlite3
from typing import AsyncIterator

import stock

DB = os.path.join(os.path.dirname(__file__), "northline.db")
MAX_ROWS = 500
MAX_TOOL_TURNS = 12

GITHUB_MODELS_URL = "https://models.github.ai/inference"

TOOLS = [
    {
        "name": "describe_schema",
        "description": "Tables, columns, and row counts of the Northline Coachworks store.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "run_sql",
        "description": (
            "Run one read-only SELECT against the store. One statement, no writes. "
            "Rows are capped at 500."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "A single SELECT or WITH statement."}},
            "required": ["query"],
        },
    },
    {
        "name": "get_demand_forecast",
        "description": (
            "Weekly order forecast for one bus model: mean and 80% interval per week, "
            "plus the holdout MAPE of the chosen model and the seasonal-naive baseline. "
            "model_id: 1 = N45 Legacy, 2 = N30 Micro, 3 = NE Volt."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "model_id": {"type": "integer"},
                "weeks": {"type": "integer", "description": "Horizon in weeks, default 13."},
            },
            "required": ["model_id"],
        },
    },
    {
        "name": "get_inventory_status",
        "description": (
            "The computed inventory position: per-component cover vs lead time with "
            "critical/warning/ok status, revenue exposure, units at risk per bus model, "
            "and the recommended order plan with costs and priorities. Use this instead "
            "of re-deriving stock maths in SQL."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "draft_purchase_orders",
        "description": (
            "Write draft purchase orders to the approval queue. Drafts do NOT commit "
            "spend: a person approves or rejects each one in the Agent hub, and only "
            "approval creates a real PO. Use when the user asks you to act on a "
            "shortfall, not merely report it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "component_id": {"type": "integer"},
                            "qty": {"type": "integer"},
                        },
                        "required": ["component_id", "qty"],
                    },
                }
            },
            "required": ["items"],
        },
    },
]

SYSTEM = """You are the supply and demand analyst for Northline Coachworks, a school-bus
manufacturer. You answer questions using the SQLite store behind your tools. The data contract:

- bus_models: model_id, name, category, price_cad (1 N45 Legacy, 2 N30 Micro, 3 NE Volt)
- demand_weekly: model_id, week (ISO Monday), orders (buses ordered that week)
- suppliers: supplier_id, name, lead_time_weeks
- components: component_id, name, category, supplier_id, unit_cost_cad
- bom: component_id, model_id, qty_per_bus (fractional values are option take rates)
- inventory: component_id, on_hand
- purchase_orders: po_id, component_id, qty, eta_week

Costs are Canadian dollars. For stock questions (cover, stockouts, what to order,
exposure) call get_inventory_status rather than re-deriving the maths; for demand
questions call get_demand_forecast and quote its interval and holdout MAPE rather
than a bare point estimate. When the user asks you to act (order, expedite, fix),
call draft_purchase_orders — drafts land in an approval queue, so say that a person
still has to approve them in the Agent hub. Give numbers with baselines and units ("0.4 weeks of
cover against a 10-week lead"). If a question is outside this data (competitor
pricing, labour), say what is missing instead of guessing. Keep answers short
enough to read in a chat dock; no headers, no bullet lists unless listing items."""


# ---------------------------------------------------------------- tools

def _connect_ro() -> sqlite3.Connection:
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def tool_describe_schema() -> str:
    con = _connect_ro()
    out = []
    for (name,) in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ):
        cols = [r[1] for r in con.execute(f"PRAGMA table_info({name})")]
        n = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        out.append(f"{name} ({n} rows): {', '.join(cols)}")
    con.close()
    return "\n".join(out)


def tool_run_sql(query: str) -> str:
    q = query.strip().rstrip(";").strip()
    if ";" in q:
        return "Error: one statement only."
    if not q.lower().startswith(("select", "with")):
        return "Error: read-only — only SELECT or WITH statements are allowed."
    con = _connect_ro()
    try:
        cur = con.execute(q)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchmany(MAX_ROWS)
        capped = cur.fetchone() is not None
    except sqlite3.Error as e:
        return f"SQL error: {e}"
    finally:
        con.close()
    payload = {"columns": cols, "rows": rows}
    if capped:
        payload["note"] = f"truncated to {MAX_ROWS} rows"
    return json.dumps(payload, default=str)


def tool_get_demand_forecast(model_id: int, weeks: int = 13) -> str:
    con = _connect_ro()
    try:
        result = stock.model_forecast(con, model_id, horizon=weeks)
    except Exception as e:
        return f"Error: {e}"
    finally:
        con.close()
    return json.dumps(result)


def tool_draft_purchase_orders(items: list) -> str:
    if not items:
        return "Error: no items given."
    con = sqlite3.connect(DB)
    as_of = con.execute("SELECT MAX(week) FROM demand_weekly").fetchone()[0]
    created = []
    for item in items:
        cid, qty = int(item["component_id"]), int(item["qty"])
        row = con.execute(
            "SELECT name, unit_cost_cad FROM components WHERE component_id=?", (cid,)
        ).fetchone()
        if not row or qty <= 0:
            continue
        con.execute(
            "INSERT INTO po_drafts (component_id, qty, cost_cad, source, status, created_at)"
            " VALUES (?,?,?,?,'draft',?)",
            (cid, qty, qty * row[1], "analyst", as_of),
        )
        created.append(f"{qty:,} x {row[0]} (${qty * row[1]:,.0f})")
    con.commit()
    con.close()
    if not created:
        return "Error: no valid items."
    return ("Drafted for approval in the Agent hub: " + "; ".join(created)
            + ". A person must approve each draft before it becomes a purchase order.")


def tool_get_inventory_status() -> str:
    con = _connect_ro()
    try:
        status = stock.inventory_status(con)
    finally:
        con.close()
    # Trim the payload the model reads: drop per-component ids it does not need.
    slim = {
        "as_of": status["as_of"],
        "counts": status["counts"],
        "avg_cover_weeks": status["avg_cover_weeks"],
        "exposure_cad": status["exposure_cad"],
        "units_at_risk": status["units_at_risk"],
        "service_level_pct": status["service_level_pct"],
        "components": [
            {k: c[k] for k in ("name", "category", "supplier", "lead_weeks", "on_hand",
                               "incoming", "weekly_use", "effective_cover_weeks",
                               "status", "shortfall_units")}
            for c in status["components"]
        ],
        "order_plan": status["order_plan"],
        "order_plan_cost": status["order_plan_cost"],
    }
    return json.dumps(slim)


def _execute(name: str, tool_input: dict) -> str:
    if name == "describe_schema":
        return tool_describe_schema()
    if name == "run_sql":
        return tool_run_sql(tool_input.get("query", ""))
    if name == "get_demand_forecast":
        return tool_get_demand_forecast(
            int(tool_input["model_id"]), int(tool_input.get("weeks") or 13)
        )
    if name == "get_inventory_status":
        return tool_get_inventory_status()
    if name == "draft_purchase_orders":
        return tool_draft_purchase_orders(tool_input.get("items", []))
    return f"Error: unknown tool {name}"


def _summarize(name: str, result: str) -> str:
    if name == "run_sql":
        try:
            n = len(json.loads(result).get("rows", []))
            return f"{n} rows"
        except (json.JSONDecodeError, AttributeError):
            return result[:80]
    if name == "get_demand_forecast":
        try:
            d = json.loads(result)
            return f"{d['model']}, MAPE {d['backtest_mape']}%"
        except (json.JSONDecodeError, KeyError):
            return result[:80]
    if name == "get_inventory_status":
        try:
            d = json.loads(result)
            return (f"{d['counts']['critical']} critical, {d['counts']['warning']} warning, "
                    f"${d['exposure_cad'] / 1e6:.1f}M at risk")
        except (json.JSONDecodeError, KeyError):
            return result[:80]
    if name == "draft_purchase_orders":
        return result[:100]
    return "ok"


# ---------------------------------------------------------------- providers

def resolve_provider() -> str:
    explicit = os.environ.get("NORTHLINE_PROVIDER")
    if explicit:
        return explicit
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("GITHUB_TOKEN"):
        return "github"
    return "claude-code"


async def stream_chat(messages: list[dict]) -> AsyncIterator[dict]:
    """messages: [{"role": "user"|"assistant", "content": str}, ...] from the UI."""
    provider = resolve_provider()
    if provider == "anthropic":
        gen = _anthropic_stream(messages)
    elif provider == "openai":
        gen = _openai_compatible_stream(
            messages,
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=None,
            model=os.environ.get("NORTHLINE_OPENAI_MODEL", "gpt-4o"),
        )
    elif provider == "github":
        gen = _openai_compatible_stream(
            messages,
            api_key=os.environ["GITHUB_TOKEN"],
            base_url=GITHUB_MODELS_URL,
            model=os.environ.get("NORTHLINE_GITHUB_MODEL", "openai/gpt-4o"),
        )
    elif provider == "claude-code":
        gen = _claude_code_stream(messages)
    else:
        raise ValueError(f"unknown NORTHLINE_PROVIDER {provider!r}")
    async for event in gen:
        yield event


async def _anthropic_stream(messages: list[dict]) -> AsyncIterator[dict]:
    import anthropic

    client = anthropic.AsyncAnthropic()
    model = os.environ.get("NORTHLINE_MODEL", "claude-opus-4-8")
    convo = [{"role": m["role"], "content": m["content"]} for m in messages]

    for _ in range(MAX_TOOL_TURNS):
        async with client.messages.stream(
            model=model,
            max_tokens=4096,
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            tools=TOOLS,
            messages=convo,
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta" and event.delta.type == "text_delta":
                    yield {"type": "delta", "text": event.delta.text}
            response = await stream.get_final_message()

        if response.stop_reason != "tool_use":
            return  # the SSE endpoint emits the single terminal "done" frame

        convo.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                result = _execute(block.name, block.input)
                yield {
                    "type": "tool",
                    "name": block.name,
                    "input": block.input,
                    "summary": _summarize(block.name, result),
                }
                results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )
        convo.append({"role": "user", "content": results})

    yield {"type": "error", "message": "tool-call limit reached before an answer"}


async def _openai_compatible_stream(
    messages: list[dict], api_key: str, base_url: str | None, model: str
) -> AsyncIterator[dict]:
    """OpenAI and GitHub Models share this driver; only base_url and model differ."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    oai_tools = [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in TOOLS
    ]
    convo = [{"role": "system", "content": SYSTEM}] + [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]

    for _ in range(MAX_TOOL_TURNS):
        stream = await client.chat.completions.create(
            model=model, messages=convo, tools=oai_tools, stream=True
        )
        calls: dict[int, dict] = {}
        text_parts: list[str] = []
        finish = None
        async for chunk in stream:
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta
            if delta and delta.content:
                text_parts.append(delta.content)
                yield {"type": "delta", "text": delta.content}
            if delta and delta.tool_calls:
                for tc in delta.tool_calls:
                    slot = calls.setdefault(tc.index, {"id": "", "name": "", "args": ""})
                    if tc.id:
                        slot["id"] = tc.id
                    if tc.function and tc.function.name:
                        slot["name"] = tc.function.name
                    if tc.function and tc.function.arguments:
                        slot["args"] += tc.function.arguments
            if choice.finish_reason:
                finish = choice.finish_reason

        if finish != "tool_calls" or not calls:
            return

        ordered = [calls[i] for i in sorted(calls)]
        convo.append(
            {
                "role": "assistant",
                "content": "".join(text_parts) or None,
                "tool_calls": [
                    {
                        "id": c["id"],
                        "type": "function",
                        "function": {"name": c["name"], "arguments": c["args"] or "{}"},
                    }
                    for c in ordered
                ],
            }
        )
        for c in ordered:
            try:
                tool_input = json.loads(c["args"] or "{}")
            except json.JSONDecodeError:
                tool_input = {}
            result = _execute(c["name"], tool_input)
            yield {
                "type": "tool",
                "name": c["name"],
                "input": tool_input,
                "summary": _summarize(c["name"], result),
            }
            convo.append({"role": "tool", "tool_call_id": c["id"], "content": result})

    yield {"type": "error", "message": "tool-call limit reached before an answer"}


async def _claude_code_stream(messages: list[dict]) -> AsyncIterator[dict]:
    """No key anywhere: drive the Claude Agent SDK, which uses the machine's
    Claude Code login. Tools run in-process through an SDK MCP server."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        create_sdk_mcp_server,
        query,
        tool,
    )

    pending: list[dict] = []  # tool events emitted by the wrappers, drained in order

    def make_tool(spec):
        @tool(spec["name"], spec["description"], spec["input_schema"])
        async def _t(args):
            result = _execute(spec["name"], args or {})
            pending.append(
                {
                    "type": "tool",
                    "name": spec["name"],
                    "input": args or {},
                    "summary": _summarize(spec["name"], result),
                }
            )
            return {"content": [{"type": "text", "text": result}]}

        return _t

    server = create_sdk_mcp_server(
        name="northline", tools=[make_tool(t) for t in TOOLS]
    )
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM,
        mcp_servers={"northline": server},
        allowed_tools=[f"mcp__northline__{t['name']}" for t in TOOLS],
        tools=[],  # no built-in filesystem or shell tools; the analyst gets data tools only
        permission_mode="bypassPermissions",  # read-only tools + approval-gated drafts
        setting_sources=[],  # ignore this machine's CLAUDE.md and settings
        max_turns=MAX_TOOL_TURNS,
        model=os.environ.get("NORTHLINE_MODEL"),  # None -> the CLI's default model
    )

    if len(messages) == 1:
        prompt = messages[0]["content"]
    else:
        lines = [
            f"{'User' if m['role'] == 'user' else 'Analyst'}: {m['content']}"
            for m in messages
        ]
        lines.append("Answer the last user question.")
        prompt = "\n".join(lines)

    async for msg in query(prompt=prompt, options=options):
        while pending:
            yield pending.pop(0)
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock) and block.text:
                    text = block.text
                    # Turns arrive as separate blocks; keep them readable when joined.
                    if not text.endswith(("\n", " ")):
                        text += "\n\n"
                    yield {"type": "delta", "text": text}
        elif isinstance(msg, ResultMessage) and getattr(msg, "is_error", False):
            yield {"type": "error", "message": str(getattr(msg, "result", "agent error"))[:300]}
    while pending:
        yield pending.pop(0)
