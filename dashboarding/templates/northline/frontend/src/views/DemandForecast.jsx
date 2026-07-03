import { useEffect, useState } from "react";
import LineChart from "../components/LineChart.jsx";
import { Panel, Tabs, LoadingBlock, ErrorBlock, fmtCad } from "../components/ui.jsx";
import Sparkline from "../components/Sparkline.jsx";

const HORIZONS = [13, 26];
const TABS = ["Forecast", "Seasonality"];

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function SeasonalityTab({ models, modelId }) {
  const m = models?.find((x) => x.model_id === modelId);
  if (!m) return <LoadingBlock h="h-64" />;
  const byMonth = Array.from({ length: 12 }, () => []);
  for (const p of m.series) byMonth[Number(p.week.slice(5, 7)) - 1].push(p.orders);
  const avg = byMonth.map((v) => (v.length ? v.reduce((s, x) => s + x, 0) / v.length : 0));
  const max = Math.max(...avg);
  const peak = MONTHS[avg.indexOf(max)];
  const trough = MONTHS[avg.indexOf(Math.min(...avg.filter(Boolean)))];
  return (
    <Panel
      title={`${m.name} orders peak in ${peak} and trough in ${trough} — the school procurement cycle`}
      subtitle="Average weekly orders by calendar month over the last two years."
    >
      <div className="mt-4 flex h-44 items-end gap-2">
        {avg.map((v, i) => (
          <div key={i} className="flex flex-1 flex-col items-center gap-1">
            <span className="font-mono text-[10px] text-muted">{v.toFixed(0)}</span>
            <div
              className={`grow-bar w-full rounded-t-sm ${v === max ? "bg-accent-vivid" : "bg-accent-soft"}`}
              style={{ height: `${(v / max) * 130}px`, "--i": i }}
            />
            <span className="text-[10px] text-muted">{MONTHS[i]}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

export default function DemandForecast() {
  const [models, setModels] = useState(null);
  const [modelId, setModelId] = useState(3); // the electric line is the story
  const [weeks, setWeeks] = useState(13);
  const [fc, setFc] = useState(null);
  const [state, setState] = useState("loading");
  const [tab, setTab] = useState(TABS[0]);

  useEffect(() => {
    fetch("/api/demand").then((r) => r.json()).then((d) => setModels(d.models)).catch(() => {});
  }, []);

  useEffect(() => {
    setState("loading");
    fetch(`/api/demand-forecast?model_id=${modelId}&weeks=${weeks}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        setFc(d);
        setState("ready");
      })
      .catch(() => setState("error"));
  }, [modelId, weeks]);

  const last13 = fc ? fc.history.slice(-13).reduce((s, d) => s + d.orders, 0) / 13 : 0;
  const next = fc ? fc.forecast.reduce((s, d) => s + d.mean, 0) / fc.forecast.length : 0;
  const pct = last13 ? (100 * (next - last13)) / last13 : 0;
  const dir = pct <= -2 ? "softens" : pct >= 2 ? "builds" : "holds";

  return (
    <div className="stagger space-y-4">
      <section className="flex items-end justify-between">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">
            Weekly order intake, history and forecast by bus model
          </h1>
          <p className="mt-0.5 text-xs text-muted">
            The forecast feeds component consumption on the Inventory health page.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="seg">
            {models?.map((m) => (
              <button key={m.model_id} onClick={() => setModelId(m.model_id)}
                className={m.model_id === modelId ? "on" : ""}>
                {m.name}
              </button>
            ))}
          </div>
          <div className="seg">
            {HORIZONS.map((h) => (
              <button key={h} onClick={() => setWeeks(h)} className={h === weeks ? "on" : ""}>
                {h} wks
              </button>
            ))}
          </div>
        </div>
      </section>

      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === "Seasonality" ? (
        <SeasonalityTab models={models} modelId={modelId} />
      ) : state === "error" ? (
        <ErrorBlock>Could not load the forecast. Retry from the model buttons above.</ErrorBlock>
      ) : state === "loading" || !fc ? (
        <LoadingBlock h="h-[320px]" />
      ) : (
        <Panel
          title={`${fc.name} averages ${last13.toFixed(0)} orders/week and the forecast ${dir} (${pct > 0 ? "+" : ""}${pct.toFixed(1)}% over ${weeks} weeks)`}
          subtitle={`${fc.model === "holt_winters" ? "Holt-Winters" : "Seasonal-naive"} forecast, 80% interval; MAPE ${fc.backtest_mape}% on the last ${fc.holdout_weeks} held-out weeks (seasonal-naive baseline ${fc.baseline_mape}%).`}
        >
          <LineChart
            history={fc.history.map((d) => ({ week: d.week, value: d.orders }))}
            forecast={fc.forecast}
            yLabel="orders/week"
            annotations={[{ week: "2024-09-02", label: "chassis shortage" }]}
          />
        </Panel>
      )}

      {models && (
        <Panel
          title="The order book concentrates in the diesel lines while the electric line grows fastest"
          subtitle="13-week averages; growth against the same 13 weeks last year."
        >
          <table className="mt-3 w-full text-sm">
            <thead>
              <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
                <th className="py-1.5 font-medium">Model</th>
                <th className="py-1.5 font-medium">Category</th>
                <th className="py-1.5 text-right font-medium">Last 26 wks</th>
                <th className="py-1.5 text-right font-medium">Orders/wk, 13w</th>
                <th className="py-1.5 text-right font-medium">vs last year</th>
                <th className="py-1.5 text-right font-medium">Weekly revenue run rate</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr
                  key={m.model_id}
                  onClick={() => setModelId(m.model_id)}
                  className={`row-hover cursor-pointer border-b border-edge/50 hover:bg-ink/[0.03] ${
                    m.model_id === modelId ? "bg-ink/[0.05]" : ""
                  }`}
                >
                  <td className="py-1.5">{m.name}</td>
                  <td className="py-1.5 text-muted">{m.category}</td>
                  <td className="py-1.5 text-right">
                    <Sparkline values={m.series.slice(-26).map((p) => p.orders)} />
                  </td>
                  <td className="py-1.5 text-right font-mono">{m.weekly_avg_13w}</td>
                  <td className={`py-1.5 text-right font-mono ${m.yoy_pct > 5 ? "text-good" : m.yoy_pct < -5 ? "text-alert" : ""}`}>
                    {m.yoy_pct > 0 ? "+" : ""}{m.yoy_pct}%
                  </td>
                  <td className="py-1.5 text-right font-mono">{fmtCad(m.weekly_avg_13w * m.price_cad)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      )}
    </div>
  );
}
