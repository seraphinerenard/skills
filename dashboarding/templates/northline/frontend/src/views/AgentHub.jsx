import { useEffect, useState } from "react";
import ChatPanel from "../components/ChatPanel.jsx";
import { Panel, SeverityCard, LoadingBlock, fmtCad } from "../components/ui.jsx";
import BusMark from "../components/BusMark.jsx";
import { useToast } from "../components/Toast.jsx";

const SUGGESTIONS = [
  "What should I order in the next two weeks, and what does it cost?",
  "Which supplier is the biggest single point of failure right now?",
  "Draft purchase orders for everything critical.",
  "Forecast NE Volt demand for the next quarter and tell me if battery supply keeps up.",
];

const TABS = ["Analyst desk", "Goal optimizer", "Procurement queue", "Alert feed"];

function Desk({ pins, pin, unpin }) {
  return (
    <div className="grid h-full min-h-0 grid-cols-5 gap-4">
      <div className="panel col-span-3 flex min-h-0 flex-col">
        <div className="border-b border-edge px-4 py-3">
          <h2 className="text-sm font-medium">Coachworks analyst</h2>
          <p className="mt-0.5 text-xs text-muted">
            Full-width desk for longer investigations. The analyst can also act: ask it to
            order something and the drafts land in the Procurement queue for your approval.
          </p>
        </div>
        <ChatPanel onPin={pin} suggestions={SUGGESTIONS} placeholder="Ask about demand, stock, suppliers, or orders" />
      </div>

      <div className="col-span-2 min-h-0 overflow-y-auto">
        <h2 className="mb-2 text-sm font-medium text-muted">Pinned answers</h2>
        {pins.length === 0 ? (
          <Panel>
            <div className="py-6 text-center">
              <BusMark size={84} />
              <p className="mt-3 text-sm text-muted">
                Nothing pinned yet. Pin an answer from any conversation and it becomes a
                standing panel here, with the SQL and tool calls attached.
              </p>
            </div>
          </Panel>
        ) : (
          <div className="space-y-3">
            {pins.map((p, i) => (
              <div key={i} className="panel p-4">
                <div className="mb-1 flex items-start justify-between gap-3">
                  <h3 className="text-sm font-medium">{p.question}</h3>
                  <button className="text-xs text-muted hover:text-ink" onClick={() => unpin(i)}>
                    Unpin
                  </button>
                </div>
                <p className="whitespace-pre-wrap text-sm text-ink/90">{p.answer}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function FrontierChart({ frontier }) {
  const W = 560;
  const H = 180;
  const PAD = { l: 46, r: 20, t: 12, b: 26 };
  const maxSpend = Math.max(...frontier.map((f) => f.spend), 1);
  const maxExp = Math.max(...frontier.map((f) => f.exposure_cad), 1);
  const x = (s) => PAD.l + (s / maxSpend) * (W - PAD.l - PAD.r);
  const y = (e) => PAD.t + (1 - e / maxExp) * (H - PAD.t - PAD.b);
  const path = frontier.map((f, i) => `${i ? "L" : "M"}${x(f.spend)},${y(f.exposure_cad)}`).join("");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="mt-2 w-full">
      <line x1={PAD.l} x2={W - PAD.r} y1={H - PAD.b} y2={H - PAD.b} style={{ stroke: "var(--color-edge)" }} />
      <line x1={PAD.l} x2={PAD.l} y1={PAD.t} y2={H - PAD.b} style={{ stroke: "var(--color-edge)" }} />
      <path d={path} fill="none" style={{ stroke: "var(--color-accent-vivid)" }} strokeWidth="2" />
      {frontier.map((f) => (
        <circle key={f.step} cx={x(f.spend)} cy={y(f.exposure_cad)} r="3"
          style={{ fill: f.critical === 0 ? "var(--color-good-vivid)" : "var(--color-accent-vivid)" }}>
          <title>{`${f.component ?? "baseline"}: spend ${fmtCad(f.spend)}, exposure ${fmtCad(f.exposure_cad)}`}</title>
        </circle>
      ))}
      <text x={PAD.l} y={H - 8} fontSize="10" style={{ fill: "var(--color-muted)" }}>$0 spend</text>
      <text x={W - PAD.r} y={H - 8} textAnchor="end" fontSize="10" style={{ fill: "var(--color-muted)" }}>
        {fmtCad(maxSpend)}
      </text>
      <text x={PAD.l - 4} y={PAD.t + 8} textAnchor="end" fontSize="10" style={{ fill: "var(--color-muted)" }}>
        {fmtCad(maxExp)}
      </text>
      <text x={PAD.l - 4} y={H - PAD.b} textAnchor="end" fontSize="10" style={{ fill: "var(--color-muted)" }}>$0</text>
    </svg>
  );
}

function Optimizer({ onDrafted }) {
  const toast = useToast();
  const [params, setParams] = useState({ service_target_pct: 95, budget_cad: 3000000, risk_tolerance: "medium" });
  const [result, setResult] = useState(null);
  const [state, setState] = useState("idle");

  async function run() {
    setState("running");
    try {
      const res = await fetch("/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });
      setResult(await res.json());
      setState("done");
    } catch {
      setState("error");
    }
  }

  async function draftPlan() {
    await fetch("/api/po-drafts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        items: result.plan.map((p) => ({ component_id: p.component_id, qty: p.qty })),
        source: "optimizer",
      }),
    });
    toast(`${result.plan.length} orders drafted for approval`, "good");
    onDrafted();
  }

  return (
    <div className="space-y-4">
      <Panel
        title="Set the goal; the engine searches order plans until it meets it"
        subtitle="Greedy on exposure removed per dollar, re-pricing every remaining candidate through the engine after each pick. The frontier shows what each next dollar buys."
      >
        <div className="mt-3 flex items-end gap-6">
          <label className="text-xs text-muted">
            Service target
            <select
              value={params.service_target_pct}
              onChange={(e) => setParams((p) => ({ ...p, service_target_pct: Number(e.target.value) }))}
              className="mt-1.5 block rounded border border-edge bg-bg px-2 py-1.5 text-sm text-ink"
            >
              <option value="90">90%</option>
              <option value="95">95%</option>
              <option value="98">98%</option>
            </select>
          </label>
          <label className="text-xs text-muted">
            Budget, CAD
            <input
              type="number" step="250000" min="0" value={params.budget_cad}
              onChange={(e) => setParams((p) => ({ ...p, budget_cad: Number(e.target.value) }))}
              className="mt-1.5 block w-40 rounded border border-edge bg-bg px-2 py-1.5 font-mono text-sm text-ink"
            />
          </label>
          <label className="text-xs text-muted">
            Risk tolerance
            <select
              value={params.risk_tolerance}
              onChange={(e) => setParams((p) => ({ ...p, risk_tolerance: e.target.value }))}
              className="mt-1.5 block rounded border border-edge bg-bg px-2 py-1.5 text-sm text-ink"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <button
            onClick={run}
            disabled={state === "running"}
            className="btn-primary px-4 py-2 text-sm disabled:opacity-40"
          >
            {state === "running" ? "Searching" : "Find the plan"}
          </button>
        </div>
      </Panel>

      {state === "running" && <LoadingBlock h="h-56" />}
      {state === "error" && <Panel><p className="text-sm text-muted">The optimizer failed. Run it again.</p></Panel>}
      {state === "done" && result && (
        <Panel
          title={
            result.met_target
              ? `${fmtCad(result.spend_cad)} clears every critical and reaches ${Math.round(result.achieved.service_level_pct)}% service`
              : `The budget runs out at ${Math.round(result.achieved.service_level_pct)}% service with ${result.achieved.critical} criticals left`
          }
          subtitle={`Baseline: ${result.baseline.critical} critical, ${fmtCad(result.baseline.exposure_cad)} exposed, ${Math.round(result.baseline.service_level_pct)}% service. Each dot is one order added to the plan; green dots have no criticals left.`}
        >
          <FrontierChart frontier={result.frontier} />
          <table className="mt-3 w-full text-sm">
            <thead>
              <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
                <th className="py-1.5 font-medium">Order</th>
                <th className="py-1.5 font-medium">Supplier</th>
                <th className="py-1.5 text-right font-medium">Qty</th>
                <th className="py-1.5 text-right font-medium">Cost</th>
              </tr>
            </thead>
            <tbody>
              {result.plan.map((p) => (
                <tr key={p.component_id} className="border-b border-edge/50">
                  <td className="py-1.5">{p.name}</td>
                  <td className="py-1.5 text-muted">{p.supplier}</td>
                  <td className="py-1.5 text-right font-mono">{p.qty.toLocaleString("en-CA")}</td>
                  <td className="py-1.5 text-right font-mono">{fmtCad(p.cost_cad)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <button
            onClick={draftPlan}
            className="btn-primary mt-3 px-4 py-2 text-sm"
          >
            Send {result.plan.length} orders to the procurement queue
          </button>
        </Panel>
      )}
    </div>
  );
}

function Procurement({ refreshKey }) {
  const [drafts, setDrafts] = useState(null);
  const toast = useToast();

  const load = () =>
    fetch("/api/po-drafts").then((r) => r.json()).then((d) => setDrafts(d.drafts)).catch(() => setDrafts([]));
  useEffect(() => {
    load();
  }, [refreshKey]);

  async function act(id, verb) {
    const res = await fetch(`/api/po-drafts/${id}/${verb}`, { method: "POST" });
    if (verb === "approve" && res.ok) {
      const d = await res.json();
      toast(`PO written — arrives the week of ${d.eta_week}. The dashboard has repriced.`, "good");
    } else if (res.ok) {
      toast("Draft rejected");
    }
    load();
  }

  if (!drafts) return <LoadingBlock h="h-56" />;
  const open = drafts.filter((d) => d.status === "draft");
  const closed = drafts.filter((d) => d.status !== "draft");

  return (
    <div className="space-y-4">
      <Panel
        title={
          open.length
            ? `${open.length} draft purchase orders wait for your approval (${fmtCad(open.reduce((s, d) => s + d.cost_cad, 0))})`
            : "The queue is clear"
        }
        subtitle="Drafts come from the analyst, the optimizer, or the inventory plan. Approving one writes a real PO with the supplier's lead time and reprices the whole dashboard."
      >
        {open.length === 0 ? (
          <p className="mt-3 text-sm text-muted">
            Nothing waiting. Ask the analyst to order something, or send the optimizer's plan here.
          </p>
        ) : (
          <table className="mt-3 w-full text-sm">
            <thead>
              <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
                <th className="py-1.5 font-medium">Component</th>
                <th className="py-1.5 font-medium">Supplier</th>
                <th className="py-1.5 text-right font-medium">Qty</th>
                <th className="py-1.5 text-right font-medium">Cost</th>
                <th className="py-1.5 text-right font-medium">Arrives</th>
                <th className="py-1.5 font-medium">Source</th>
                <th className="py-1.5 text-right font-medium">Decision</th>
              </tr>
            </thead>
            <tbody>
              {open.map((d) => (
                <tr key={d.draft_id} className="border-b border-edge/50">
                  <td className="py-1.5">{d.name}</td>
                  <td className="py-1.5 text-muted">{d.supplier}</td>
                  <td className="py-1.5 text-right font-mono">{d.qty.toLocaleString("en-CA")}</td>
                  <td className="py-1.5 text-right font-mono">{fmtCad(d.cost_cad)}</td>
                  <td className="py-1.5 text-right font-mono">{d.lead_time_weeks} wks</td>
                  <td className="py-1.5 text-muted">{d.source}</td>
                  <td className="py-1.5 text-right">
                    <button onClick={() => act(d.draft_id, "approve")}
                      className="btn-good px-2.5 py-1 text-xs">
                      Approve
                    </button>
                    <button onClick={() => act(d.draft_id, "reject")}
                      className="ml-2 rounded border border-edge px-2 py-1 text-xs text-muted hover:text-ink">
                      Reject
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>

      {closed.length > 0 && (
        <Panel title={`${closed.length} decided drafts`} subtitle="Approved drafts became purchase orders; the inventory views already count them.">
          <table className="mt-3 w-full text-sm">
            <tbody>
              {closed.slice(0, 8).map((d) => (
                <tr key={d.draft_id} className="border-b border-edge/50 text-muted">
                  <td className="py-1.5">{d.name}</td>
                  <td className="py-1.5 text-right font-mono">{d.qty.toLocaleString("en-CA")}</td>
                  <td className="py-1.5 text-right font-mono">{fmtCad(d.cost_cad)}</td>
                  <td className={`py-1.5 text-right ${d.status === "approved" ? "text-good" : ""}`}>{d.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      )}
    </div>
  );
}

function AlertFeed() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch("/api/alerts").then((r) => r.json()).then(setData).catch(() => setData({ events: [] }));
  }, []);
  if (!data) return <LoadingBlock h="h-56" />;
  const sevMap = { alert: "alert", warning: "warning", info: "watch" };
  return (
    <div className="space-y-2">
      <p className="text-xs text-muted">
        Standing watchers over the same engine: stockout countdowns, arriving POs, demand
        anomalies against the forecast band, and concentration risk. As of {data.as_of}.
      </p>
      {data.events.length === 0 ? (
        <Panel><p className="text-sm text-muted">No events. The watchers stay armed.</p></Panel>
      ) : (
        data.events.map((e, i) => (
          <SeverityCard key={i} severity={sevMap[e.severity] ?? "watch"} title={e.title} body={`${e.body} (${e.when})`} />
        ))
      )}
    </div>
  );
}

export default function AgentHub({ pins, pin, unpin }) {
  const [tab, setTab] = useState(TABS[0]);
  const [queueRefresh, setQueueRefresh] = useState(0);

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="mb-4 flex gap-2">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-md border px-3 py-1.5 text-sm ${
              t === tab ? "border-accent/60 bg-accent/10 text-accent" : "border-edge text-muted hover:text-ink"
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto">
        {tab === "Analyst desk" && <Desk pins={pins} pin={pin} unpin={unpin} />}
        {tab === "Goal optimizer" && (
          <Optimizer onDrafted={() => { setQueueRefresh((n) => n + 1); setTab("Procurement queue"); }} />
        )}
        {tab === "Procurement queue" && <Procurement refreshKey={queueRefresh} />}
        {tab === "Alert feed" && <AlertFeed />}
      </div>
    </div>
  );
}
