import { useEffect, useState } from "react";
import {
  Package, WarningCircle, Warning, Timer, CurrencyDollar, Gauge,
} from "../components/icons.jsx";
import { Panel, SeverityCard, StatTile, LoadingBlock, fmtCad } from "../components/ui.jsx";
import CountUp from "../components/CountUp.jsx";

/* Hero cell: the number an executive checks first, at poster size, over a
   live area chart of total weekly intake. */
function HeroCell({ kpis, demand }) {
  const weeks = {};
  for (const m of demand ?? []) {
    for (const p of m.series.slice(-26)) weeks[p.week] = (weeks[p.week] ?? 0) + p.orders;
  }
  const series = Object.entries(weeks).sort(([a], [b]) => (a < b ? -1 : 1)).map(([, v]) => v);
  const W = 320;
  const H = 84;
  const min = Math.min(...series, 1);
  const max = Math.max(...series, 2);
  const x = (i) => (i / Math.max(series.length - 1, 1)) * W;
  const y = (v) => 6 + (1 - (v - min) / (max - min || 1)) * (H - 12);
  const line = series.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join("");
  const area = line ? `${line}L${W},${H}L0,${H}Z` : "";

  return (
    <div
      className="panel relative col-span-2 row-span-2 overflow-hidden p-5"
      style={{ background: "var(--tint-accent)", borderColor: "transparent" }}
    >
      <div className="flex items-start justify-between">
        <div className="text-[11px] uppercase tracking-wide text-muted">Service level</div>
        <Gauge size={22} color="var(--color-accent-vivid)"
          className="glow" style={{ "--glow": "var(--color-accent-vivid)" }} />
      </div>
      <div className="display glow-text mt-2 text-[64px] font-semibold leading-none tracking-tight text-accent">
        {kpis ? <CountUp value={kpis.service_level_pct} format={(v) => `${Math.round(v)}%`} /> : "–"}
      </div>
      <div className="mt-1.5 text-[13px] text-muted">
        of the next 13 weeks' planned buses are buildable with current stock and POs
      </div>
      <div className="mt-3 flex gap-2">
        <span className="rounded-full px-2.5 py-1 text-[11px] font-medium text-alert"
          style={{ background: "var(--tint-alert)" }}>
          {kpis?.critical ?? "–"} critical
        </span>
        <span className="rounded-full px-2.5 py-1 text-[11px] font-medium text-warn"
          style={{ background: "var(--tint-warn)" }}>
          {kpis?.warning ?? "–"} warning
        </span>
        <span className="rounded-full px-2.5 py-1 text-[11px] font-medium text-good"
          style={{ background: "var(--tint-good)" }}>
          {kpis ? 26 - kpis.critical - kpis.warning : "–"} healthy
        </span>
      </div>
      {area && (
        <svg viewBox={`0 0 ${W} ${H}`} className="absolute bottom-0 left-0 w-full" preserveAspectRatio="none" height="84">
          <defs>
            <linearGradient id="heroFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="var(--color-accent-vivid)" stopOpacity="0.35" />
              <stop offset="1" stopColor="var(--color-accent-vivid)" stopOpacity="0.02" />
            </linearGradient>
          </defs>
          <path d={area} fill="url(#heroFill)" className="fade-late" />
          <path d={line} fill="none" stroke="var(--color-accent-vivid)" strokeWidth="2" className="glow"
            style={{ "--glow": "var(--color-accent-vivid)" }} />
        </svg>
      )}
    </div>
  );
}

function CategoryBars({ components }) {
  const cats = {};
  for (const c of components) {
    const e = (cats[c.category] ??= { critical: 0, warning: 0, ok: 0 });
    e[c.status] += 1;
  }
  const entries = Object.entries(cats).sort((a, b) => b[1].critical - a[1].critical);
  const max = Math.max(...entries.map(([, v]) => v.critical + v.warning + v.ok));
  return (
    <div className="mt-3 space-y-2.5">
      {entries.map(([cat, v]) => {
        const total = v.critical + v.warning + v.ok;
        return (
          <div key={cat} className="flex items-center gap-2 text-xs">
            <span className="w-20 shrink-0 text-muted">{cat}</span>
            <div className="flex h-3.5 flex-1 gap-px overflow-hidden rounded-full">
              {["critical", "warning", "ok"].map((k) =>
                v[k] ? (
                  <div
                    key={k}
                    className={
                      k === "critical" ? "bg-alert-vivid" : k === "warning" ? "bg-warn-vivid" : "bg-good-vivid"
                    }
                    style={{ width: `${(v[k] / max) * 100}%` }}
                    title={`${v[k]} ${k}`}
                  />
                ) : null,
              )}
            </div>
            <span className="w-24 shrink-0 text-right font-mono text-muted">
              {v.critical > 0 ? `${v.critical} critical` : `${total} tracked`}
            </span>
          </div>
        );
      })}
      <div className="flex gap-4 pt-1 text-[11px] text-muted">
        <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-alert-vivid" />critical</span>
        <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-warn-vivid" />warning</span>
        <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-good-vivid" />ok</span>
      </div>
    </div>
  );
}

export default function Overview({ kpis }) {
  const [findings, setFindings] = useState(null);
  const [inv, setInv] = useState(null);
  const [demand, setDemand] = useState(null);

  useEffect(() => {
    fetch("/api/insights").then((r) => r.json()).then((d) => setFindings(d.findings)).catch(() => setFindings([]));
    fetch("/api/inventory").then((r) => r.json()).then(setInv).catch(() => {});
    fetch("/api/demand").then((r) => r.json()).then((d) => setDemand(d.models)).catch(() => {});
  }, []);

  return (
    <div className="stagger space-y-4">
      <section>
        <h1 className="text-[26px] font-semibold tracking-tight">
          {kpis
            ? kpis.critical > 0
              ? `${kpis.critical} components need action before the production plan breaks`
              : "The production plan is covered at current stock levels"
            : "Overview"}
        </h1>
        <p className="mt-0.5 text-[13px] text-muted">
          Computed from demand forecasts, stock, open purchase orders, and supplier lead times.
        </p>
      </section>

      <div className="stagger grid grid-cols-4 grid-rows-2 gap-3">
        <HeroCell kpis={kpis} demand={demand} />
        <StatTile label="Critical" value={kpis?.critical} note="immediate action"
          tone={kpis?.critical ? "alert" : "good"} Icon={WarningCircle} />
        <StatTile label="Warning" value={kpis?.warning} note="monitor closely"
          tone={kpis?.warning ? "warn" : undefined} Icon={Warning} />
        <StatTile label="At-risk value" value={kpis?.at_risk_cad} format={fmtCad}
          note="production exposure" tone={kpis?.at_risk_cad > 0 ? "alert" : "good"} Icon={CurrencyDollar} />
        <StatTile label="Avg cover" value={kpis?.avg_cover_weeks}
          format={(v) => `${v.toFixed(1)} wks`} note="effective, incl. POs" Icon={Timer} />
      </div>

      {findings === null ? (
        <LoadingBlock h="h-48" />
      ) : (
        <div className="stagger space-y-2">
          {findings.map((f, i) => (
            <SeverityCard key={i} severity={f.severity} title={f.title} body={f.body} />
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <Panel
          title={
            inv
              ? `${inv.counts.critical + inv.counts.warning} of ${inv.components.length} components sit below their safety band`
              : "Inventory status by category"
          }
          subtitle="Component status by category; length is the number of tracked SKUs."
        >
          {inv ? <CategoryBars components={inv.components} /> : <LoadingBlock h="h-44" />}
        </Panel>

        <Panel
          title={
            demand
              ? `Order intake runs ${demand.reduce((s, m) => s + m.weekly_avg_13w, 0).toFixed(0)} buses/week across three models`
              : "Demand snapshot"
          }
          subtitle="13-week average against the same weeks last year. Detail on the Demand forecast page."
        >
          {demand ? (
            <table className="mt-3 w-full text-sm">
              <thead>
                <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
                  <th className="py-1.5 font-medium">Model</th>
                  <th className="py-1.5 font-medium">Category</th>
                  <th className="py-1.5 text-right font-medium">Orders/wk</th>
                  <th className="py-1.5 text-right font-medium">vs last year</th>
                  <th className="py-1.5 text-right font-medium">List price</th>
                </tr>
              </thead>
              <tbody>
                {demand.map((m) => (
                  <tr key={m.model_id} className="border-b border-edge/50">
                    <td className="py-1.5">{m.name}</td>
                    <td className="py-1.5 text-muted">{m.category}</td>
                    <td className="py-1.5 text-right font-mono">{m.weekly_avg_13w}</td>
                    <td className={`py-1.5 text-right font-mono ${m.yoy_pct > 5 ? "text-good" : m.yoy_pct < -5 ? "text-alert" : ""}`}>
                      {m.yoy_pct > 0 ? "+" : ""}{m.yoy_pct}%
                    </td>
                    <td className="py-1.5 text-right font-mono">{fmtCad(m.price_cad)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <LoadingBlock h="h-44" />
          )}
        </Panel>
      </div>
    </div>
  );
}
