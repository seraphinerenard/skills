import { useEffect, useRef, useState } from "react";
import { Panel, LoadingBlock, fmtCad } from "../components/ui.jsx";

function Delta({ label, base, scen, fmt = (v) => v, downIsGood = false }) {
  const changed = base !== scen;
  const better = downIsGood ? scen < base : scen > base;
  return (
    <div className="rounded-md border border-edge bg-panel p-4">
      <div className="text-[11px] uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 flex items-baseline gap-2">
        <span className={`font-mono text-2xl ${changed ? (better ? "text-good" : "text-alert") : ""}`}>
          {fmt(scen)}
        </span>
        {changed && <span className="font-mono text-xs text-muted">from {fmt(base)}</span>}
      </div>
    </div>
  );
}

const DEFAULTS = {
  demand_pct: 0,
  lead_delta_weeks: 0,
  service_level: "95",
  risk_tolerance: "medium",
  budget_cad: 2500000,
  demand_pct_by_model: {},
  lead_delta_by_supplier: {},
};

export default function WhatIf() {
  const [params, setParams] = useState(DEFAULTS);
  const [models, setModels] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const timer = useRef(null);

  useEffect(() => {
    fetch("/api/demand").then((r) => r.json()).then((d) => setModels(d.models)).catch(() => {});
    fetch("/api/inventory").then((r) => r.json())
      .then((d) => setSuppliers((d.suppliers ?? []).slice(0, 6)))
      .catch(() => {});
  }, []);

  const setGranular = (key, id) => (e) =>
    setParams((p) => {
      const next = { ...p[key] };
      const v = Number(e.target.value);
      if (v === 0) delete next[id];
      else next[id] = v;
      return { ...p, [key]: next };
    });
  const dirtyGranular =
    Object.keys(params.demand_pct_by_model).length + Object.keys(params.lead_delta_by_supplier).length;

  // Debounced recompute: the sliders fire continuously, the API call does not need to.
  useEffect(() => {
    clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      setBusy(true);
      try {
        const res = await fetch("/api/whatif", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(params),
        });
        setResult(await res.json());
      } finally {
        setBusy(false);
      }
    }, 350);
    return () => clearTimeout(timer.current);
  }, [params]);

  const set = (k) => (e) =>
    setParams((p) => ({ ...p, [k]: e.target.type === "range" || e.target.type === "number" ? Number(e.target.value) : e.target.value }));

  const b = result?.baseline;
  const s = result?.scenario;
  const funded = result?.order_plan?.filter((p) => p.funded !== false) ?? [];
  const deferred = result?.order_plan?.filter((p) => p.funded === false) ?? [];

  return (
    <div className="stagger space-y-4">
      <section>
        <h1 className="text-lg font-semibold tracking-tight">
          Move demand, lead times, or the budget and watch the stock position reprice
        </h1>
        <p className="mt-0.5 text-xs text-muted">
          Elasticity-free stress test: the engine reruns the full cover, exposure, and order-plan
          maths under your assumptions. Baseline stays at today's parameters.
        </p>
      </section>

      <Panel>
        <div className="grid grid-cols-5 gap-6">
          <label className="text-xs text-muted">
            Demand {params.demand_pct > 0 ? "+" : ""}{params.demand_pct}%
            <input type="range" min="-30" max="30" step="5" value={params.demand_pct}
              onChange={set("demand_pct")} className="mt-2 w-full"
              style={{ accentColor: "var(--color-accent)" }} />
          </label>
          <label className="text-xs text-muted">
            Lead times {params.lead_delta_weeks > 0 ? "+" : ""}{params.lead_delta_weeks} wks
            <input type="range" min="-2" max="6" step="1" value={params.lead_delta_weeks}
              onChange={set("lead_delta_weeks")} className="mt-2 w-full"
              style={{ accentColor: "var(--color-accent)" }} />
          </label>
          <label className="text-xs text-muted">
            Service level target
            <select value={params.service_level} onChange={set("service_level")}
              className="mt-2 w-full rounded border border-edge bg-bg px-2 py-1.5 text-sm text-ink">
              <option value="90">90% (1 wk safety)</option>
              <option value="95">95% (2 wks safety)</option>
              <option value="98">98% (3 wks safety)</option>
            </select>
          </label>
          <label className="text-xs text-muted">
            Risk tolerance
            <select value={params.risk_tolerance} onChange={set("risk_tolerance")}
              className="mt-2 w-full rounded border border-edge bg-bg px-2 py-1.5 text-sm text-ink">
              <option value="low">Low (warn under 1.75x lead)</option>
              <option value="medium">Medium (1.5x)</option>
              <option value="high">High (1.25x)</option>
            </select>
          </label>
          <label className="text-xs text-muted">
            Order budget, CAD
            <input type="number" step="250000" min="0" value={params.budget_cad}
              onChange={set("budget_cad")}
              className="mt-2 w-full rounded border border-edge bg-bg px-2 py-1.5 font-mono text-sm text-ink" />
          </label>
        </div>
      </Panel>

      <Panel
        title="Granular levers: shock one product line or one supplier instead of the whole book"
        subtitle={`Per-model demand and per-supplier lead-time changes stack with the global levers above.${dirtyGranular ? "" : " Everything at zero: the scenario matches the global levers."}`}
      >
        <div className="mt-3 grid grid-cols-2 gap-8">
          <div className="space-y-3">
            <div className="text-[11px] uppercase tracking-wide text-muted">Demand by model</div>
            {models.map((m) => {
              const v = params.demand_pct_by_model[m.model_id] ?? 0;
              return (
                <label key={m.model_id} className="flex items-center gap-3 text-xs">
                  <span className="w-24 shrink-0 text-muted">{m.name}</span>
                  <input type="range" min="-40" max="40" step="5" value={v}
                    onChange={setGranular("demand_pct_by_model", m.model_id)}
                    className="flex-1" style={{ accentColor: "var(--color-accent)" }} />
                  <span className={`w-12 shrink-0 text-right font-mono ${v ? "text-accent" : "text-muted"}`}>
                    {v > 0 ? "+" : ""}{v}%
                  </span>
                </label>
              );
            })}
          </div>
          <div className="space-y-3">
            <div className="text-[11px] uppercase tracking-wide text-muted">Lead time by supplier</div>
            {suppliers.map((s2) => {
              const v = params.lead_delta_by_supplier[s2.supplier_id] ?? 0;
              return (
                <label key={s2.supplier_id} className="flex items-center gap-3 text-xs">
                  <span className="w-40 shrink-0 truncate text-muted">{s2.supplier}</span>
                  <input type="range" min="-2" max="8" step="1" value={v}
                    onChange={setGranular("lead_delta_by_supplier", s2.supplier_id)}
                    className="flex-1" style={{ accentColor: "var(--color-accent)" }} />
                  <span className={`w-14 shrink-0 text-right font-mono ${v ? "text-accent" : "text-muted"}`}>
                    {v > 0 ? "+" : ""}{v} wks
                  </span>
                </label>
              );
            })}
          </div>
        </div>
        <button
          onClick={() => setParams(DEFAULTS)}
          className="mt-4 rounded border border-edge px-3 py-1.5 text-xs text-muted hover:text-ink"
        >
          Reset all levers
        </button>
      </Panel>

      {!result ? (
        <LoadingBlock h="h-40" />
      ) : (
        <>
          <div className={`stagger grid grid-cols-5 gap-3 ${busy ? "opacity-60" : ""}`}>
            <Delta label="Critical components" base={b.counts.critical} scen={s.counts.critical} downIsGood />
            <Delta label="Warnings" base={b.counts.warning} scen={s.counts.warning} downIsGood />
            <Delta label="At-risk value" base={b.exposure_cad} scen={s.exposure_cad} fmt={fmtCad} downIsGood />
            <Delta label="Service level" base={b.service_level_pct} scen={s.service_level_pct} fmt={(v) => `${Math.round(v)}%`} />
            <Delta label="Order plan cost" base={b.order_plan_cost} scen={s.order_plan_cost} fmt={fmtCad} downIsGood />
          </div>

          <Panel
            title={
              deferred.length
                ? `The budget funds ${funded.length} of ${result.order_plan.length} recommended orders; ${deferred.length} wait`
                : `The budget covers all ${funded.length} recommended orders under this scenario`
            }
            subtitle="Critical priority first, then largest exposure removed per dollar."
          >
            <table className="mt-3 w-full text-sm">
              <thead>
                <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
                  <th className="py-1.5 font-medium">Component</th>
                  <th className="py-1.5 font-medium">Supplier</th>
                  <th className="py-1.5 text-right font-medium">Qty</th>
                  <th className="py-1.5 text-right font-medium">Cost</th>
                  <th className="py-1.5 text-right font-medium">Priority</th>
                  <th className="py-1.5 text-right font-medium">Funded</th>
                </tr>
              </thead>
              <tbody>
                {result.order_plan.map((p) => (
                  <tr key={p.component_id} className={`border-b border-edge/50 ${p.funded === false ? "opacity-50" : ""}`}>
                    <td className="py-1.5">{p.name}</td>
                    <td className="py-1.5 text-muted">{p.supplier}</td>
                    <td className="py-1.5 text-right font-mono">{p.qty.toLocaleString("en-CA")}</td>
                    <td className="py-1.5 text-right font-mono">{fmtCad(p.cost_cad)}</td>
                    <td className={`py-1.5 text-right ${p.priority === "critical" ? "text-alert" : "text-muted"}`}>
                      {p.priority}
                    </td>
                    <td className="py-1.5 text-right font-mono">{p.funded === false ? "deferred" : "yes"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        </>
      )}
    </div>
  );
}
