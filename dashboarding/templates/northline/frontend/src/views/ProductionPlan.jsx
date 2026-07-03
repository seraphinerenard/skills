import { useEffect, useState } from "react";
import { Panel, StatTile, LoadingBlock, fmtCad } from "../components/ui.jsx";

/* The S&OP view: constrained build schedule for the committed horizon.
   Bars are buildable buses per week against the demand line; the gating
   component is named on every constrained week. */
function ScheduleChart({ weeks }) {
  const W = 860;
  const H = 240;
  const PAD = { l: 42, r: 16, t: 14, b: 40 };
  const maxD = Math.max(...weeks.map((w) => w.demand)) * 1.08;
  const bw = (W - PAD.l - PAD.r) / weeks.length;
  const y = (v) => PAD.t + (1 - v / maxD) * (H - PAD.t - PAD.b);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="mt-2 w-full">
      {[0, 0.5, 1].map((f) => (
        <g key={f}>
          <line x1={PAD.l} x2={W - PAD.r} y1={y(f * maxD)} y2={y(f * maxD)}
            style={{ stroke: "var(--color-edge)" }} />
          <text x={PAD.l - 5} y={y(f * maxD) + 3} textAnchor="end" fontSize="10"
            style={{ fill: "var(--color-muted)" }}>
            {Math.round(f * maxD)}
          </text>
        </g>
      ))}
      {weeks.map((w, i) => {
        const x0 = PAD.l + i * bw + bw * 0.18;
        const constrained = w.fill_pct < 99.5;
        return (
          <g key={w.week_offset}>
            <rect
              x={x0} width={bw * 0.64} rx="5"
              y={y(w.buildable)} height={Math.max(1, y(0) - y(w.buildable))}
              className="grow-bar glow"
              style={{
                fill: constrained ? "var(--color-warn-vivid)" : "var(--color-good-vivid)",
                "--i": i,
                "--glow": constrained ? "var(--color-warn-vivid)" : "var(--color-good-vivid)",
              }}
            >
              <title>{`week ${w.week_offset}: build ${w.buildable} of ${w.demand}${w.gating_component ? `, gated by ${w.gating_component}` : ""}`}</title>
            </rect>
            {constrained && (
              <rect
                x={x0} width={bw * 0.64}
                y={y(w.demand)} height={Math.max(0, y(w.buildable) - y(w.demand))}
                className="fade-late"
                style={{ fill: "var(--color-alert-vivid)", "--target-opacity": 0.3 }}
              />
            )}
            <text x={x0 + bw * 0.32} y={y(w.buildable) - 5} textAnchor="middle" fontSize="9"
              className="fade-late display" style={{ fill: "var(--color-muted)" }}>
              {Math.round(w.buildable)}
            </text>
            <text x={x0 + bw * 0.32} y={H - PAD.b + 13} textAnchor="middle" fontSize="9.5"
              style={{ fill: "var(--color-muted)" }}>
              wk {w.week_offset}
            </text>
            {constrained && (
              <text x={x0 + bw * 0.32} y={H - PAD.b + 25} textAnchor="middle" fontSize="8.5"
                style={{ fill: "var(--color-alert)" }}>
                {Math.round(w.fill_pct)}%
              </text>
            )}
          </g>
        );
      })}
      {/* demand line on top of the bars */}
      <path
        d={weeks.map((w, i) => `${i ? "L" : "M"}${PAD.l + i * bw + bw / 2},${y(w.demand)}`).join("")}
        fill="none" style={{ stroke: "var(--color-ink)" }} strokeWidth="1.4"
      />
      <text x={W - PAD.r} y={y(weeks[weeks.length - 1].demand) - 6} textAnchor="end" fontSize="10"
        style={{ fill: "var(--color-ink)" }}>
        demand
      </text>
    </svg>
  );
}

export default function ProductionPlan() {
  const [plan, setPlan] = useState(null);

  useEffect(() => {
    fetch("/api/production-plan").then((r) => r.json()).then(setPlan).catch(() => {});
  }, []);

  if (!plan) return <LoadingBlock h="h-96" />;
  const constrained = plan.weeks.filter((w) => w.fill_pct < 99.5);

  return (
    <div className="stagger space-y-4">
      <section>
        <h1 className="text-lg font-semibold tracking-tight">
          {plan.buses_lost > 0
            ? `Current stock and POs leave ${plan.buses_lost} buses unbuildable over the committed horizon`
            : "Current stock and POs cover the full 13-week schedule"}
        </h1>
        <p className="mt-0.5 text-xs text-muted">
          Week-by-week build simulation: stock, open POs as they arrive, and rolling replenishment
          that lands only after each supplier's lead time. What happens inside a lead window is
          already committed; nothing ordered today changes it.
        </p>
      </section>

      <div className="grid grid-cols-4 gap-3">
        <StatTile label="Buses lost" value={plan.buses_lost} note="over 13 weeks, committed horizon"
          tone={plan.buses_lost > 0 ? "alert" : "good"} />
        <StatTile label="Revenue lost" value={plan.revenue_lost_cad} format={fmtCad} note="at list prices"
          tone={plan.revenue_lost_cad > 0 ? "alert" : "good"} />
        <StatTile label="Worst week" value={`wk ${plan.worst_week}`}
          note={`${plan.weeks[plan.worst_week - 1].fill_pct}% fill`} tone="warn" />
        <StatTile label="Constrained weeks" value={constrained.length} note="of 13 simulated" />
      </div>

      <Panel
        title={
          constrained.length
            ? `${constrained[0].gating_component ?? "A component"} gates the schedule until its replenishment lands`
            : "Every week builds to demand"
        }
        subtitle="Bars are buildable buses (amber while constrained); the line is forecast demand; the red band is lost production."
      >
        <ScheduleChart weeks={plan.weeks} />
      </Panel>

      <Panel title="The gate moves as POs arrive and lead times expire" subtitle="Per-model build against demand, with each week's binding constraint.">
        <table className="mt-3 w-full text-sm">
          <thead>
            <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
              <th className="py-1.5 font-medium">Week</th>
              {Object.keys(plan.weeks[0].by_model).map((m) => (
                <th key={m} className="py-1.5 text-right font-medium">{m}</th>
              ))}
              <th className="py-1.5 text-right font-medium">Fill</th>
              <th className="py-1.5 pl-6 font-medium">Gating component</th>
            </tr>
          </thead>
          <tbody>
            {plan.weeks.map((w) => (
              <tr key={w.week_offset} className="border-b border-edge/50">
                <td className="py-1.5 font-mono">wk {w.week_offset}</td>
                {Object.entries(w.by_model).map(([m, v]) => (
                  <td key={m} className="py-1.5 text-right font-mono">
                    {v}
                    <span className="text-muted"> / {w.demand_by_model[m]}</span>
                  </td>
                ))}
                <td className={`py-1.5 text-right font-mono ${
                  w.fill_pct < 90 ? "text-alert" : w.fill_pct < 99.5 ? "text-warn" : "text-good"
                }`}>
                  {w.fill_pct}%
                </td>
                <td className="py-1.5 pl-6 text-muted">{w.gating_component ?? "–"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}
