import { useId, useLayoutEffect, useRef, useState } from "react";

const W = 720;
const H = 230;
const PAD = { l: 40, r: 84, t: 12, b: 22 };

/* Weekly series with an optional forecast tail: history solid over a faint area,
   forecast dashed, interval as a low-opacity band, direct labels instead of a
   legend, hover tooltip, optional event annotations. Colours come from the theme
   variables so both themes render correctly. */
export default function LineChart({ history, forecast = [], yLabel = "", annotations = [] }) {
  const [hover, setHover] = useState(null);
  const [pathLen, setPathLen] = useState(null);
  const svgRef = useRef(null);
  const histRef = useRef(null);
  const gradId = useId();

  const points = [
    ...history.map((d) => ({ week: d.week, value: d.value, kind: "history" })),
    ...forecast.map((d) => ({ week: d.week, value: d.mean, lo: d.lo, hi: d.hi, kind: "forecast" })),
  ];
  const values = [
    ...history.map((d) => d.value),
    ...forecast.flatMap((d) => [d.lo, d.hi]),
  ];
  const yMin = Math.min(...values) * 0.9;
  const yMax = Math.max(...values) * 1.06;
  const x = (i) => PAD.l + (i / Math.max(points.length - 1, 1)) * (W - PAD.l - PAD.r);
  const y = (v) => PAD.t + (1 - (v - yMin) / (yMax - yMin || 1)) * (H - PAD.t - PAD.b);

  const n0 = history.length;
  const histPath = history.map((d, i) => `${i ? "L" : "M"}${x(i)},${y(d.value)}`).join("");
  const areaPath = histPath
    ? histPath + `L${x(n0 - 1)},${H - PAD.b}L${x(0)},${H - PAD.b}Z`
    : "";
  const fcPath = forecast.map((d, i) => `${i ? "L" : "M"}${x(n0 + i)},${y(d.mean)}`).join("");
  const band = forecast.length
    ? forecast.map((d, i) => `${i ? "L" : "M"}${x(n0 + i)},${y(d.hi)}`).join("") +
      forecast
        .map((d, i) => `L${x(n0 + forecast.length - 1 - i)},${y(forecast[forecast.length - 1 - i].lo)}`)
        .join("") +
      "Z"
    : "";

  const ticks = [0, 0.5, 1].map((f) => Math.round(yMin + f * (yMax - yMin)));

  // Measure the history path so it can draw itself in at the right speed.
  useLayoutEffect(() => {
    setPathLen(null);
    const raf = requestAnimationFrame(() => {
      if (histRef.current) setPathLen(histRef.current.getTotalLength());
    });
    return () => cancelAnimationFrame(raf);
  }, [histPath]);

  function onMove(e) {
    const rect = svgRef.current.getBoundingClientRect();
    const px = ((e.clientX - rect.left) / rect.width) * W;
    const i = Math.max(0, Math.min(points.length - 1,
      Math.round(((px - PAD.l) / (W - PAD.l - PAD.r)) * (points.length - 1))));
    setHover({ i, left: (x(i) / W) * 100, top: (y(points[i].value) / H) * 100 });
  }

  return (
    <div className="relative">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${W} ${H}`}
        className="mt-2 w-full"
        onMouseMove={onMove}
        onMouseLeave={() => setHover(null)}
      >
        {ticks.map((t) => (
          <g key={t}>
            <line x1={PAD.l} x2={W - PAD.r} y1={y(t)} y2={y(t)}
              style={{ stroke: "var(--color-edge)" }} strokeWidth="1" />
            <text x={PAD.l - 6} y={y(t) + 3} textAnchor="end" fontSize="10"
              style={{ fill: "var(--color-muted)" }}>
              {t.toLocaleString("en-CA")}
            </text>
          </g>
        ))}
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="var(--color-accent-vivid)" stopOpacity="0.28" />
            <stop offset="1" stopColor="var(--color-accent-vivid)" stopOpacity="0.02" />
          </linearGradient>
        </defs>
        {areaPath && (
          <path d={areaPath} fill={`url(#${gradId})`} className="fade-late" />
        )}
        {band && (
          <path d={band} className="fade-late"
            style={{ fill: "var(--color-accent-vivid)", "--target-opacity": 0.2 }} />
        )}
        <path
          ref={histRef}
          d={histPath}
          fill="none"
          style={pathLen ? { stroke: "var(--color-ink)", "--path-len": pathLen } : { stroke: "var(--color-ink)", opacity: 0 }}
          className={pathLen ? "draw-line" : ""}
          strokeWidth="1.5"
        />
        {fcPath && (
          <path d={fcPath} fill="none" className="fade-late"
            style={{ stroke: "var(--color-accent)" }}
            strokeWidth="2" strokeDasharray="4 3" />
        )}
        {annotations.map((a) => {
          const i = points.findIndex((p) => p.week >= a.week);
          if (i < 0) return null;
          return (
            <g key={a.week}>
              <line x1={x(i)} x2={x(i)} y1={PAD.t} y2={H - PAD.b}
                style={{ stroke: "var(--color-muted)" }} strokeWidth="1" strokeDasharray="2 3" opacity="0.7" />
              <text x={x(i) + 4} y={PAD.t + 9} fontSize="9.5" style={{ fill: "var(--color-muted)" }}>
                {a.label}
              </text>
            </g>
          );
        })}
        {history.length > 0 && (
          <text x={x(n0 - 1) + 4} y={y(history[n0 - 1].value) - 6} fontSize="10"
            className="fade-late" style={{ fill: "var(--color-ink)" }}>
            history
          </text>
        )}
        {forecast.length > 0 && (
          <text x={x(points.length - 1) + 4} y={y(forecast[forecast.length - 1].mean)}
            fontSize="10" className="fade-late" style={{ fill: "var(--color-accent)" }}>
            forecast
          </text>
        )}
        {hover && (
          <>
            <line x1={x(hover.i)} x2={x(hover.i)} y1={PAD.t} y2={H - PAD.b}
              style={{ stroke: "var(--color-muted)" }} strokeWidth="1" opacity="0.5" />
            <circle cx={x(hover.i)} cy={y(points[hover.i].value)} r="3"
              style={{ fill: points[hover.i].kind === "forecast" ? "var(--color-accent)" : "var(--color-ink)" }} />
          </>
        )}
        <text x={PAD.l} y={H - 6} fontSize="10" style={{ fill: "var(--color-muted)" }}>
          {points[0]?.week}
        </text>
        <text x={W - PAD.r} y={H - 6} textAnchor="end" fontSize="10" style={{ fill: "var(--color-muted)" }}>
          {points[points.length - 1]?.week}
        </text>
        {yLabel && (
          <text x={PAD.l} y={PAD.t - 2} fontSize="10" style={{ fill: "var(--color-muted)" }}>
            {yLabel}
          </text>
        )}
      </svg>
      {hover && (
        <div
          className="panel pointer-events-none absolute z-10 px-2 py-1 font-mono text-[11px]"
          style={{
            left: `${hover.left}%`, top: `${hover.top}%`,
            transform: `translate(${hover.left > 70 ? "-110%" : "10px"}, -120%)`,
          }}
        >
          <span className="text-muted">{points[hover.i].week}</span>{" "}
          {Math.round(points[hover.i].value).toLocaleString("en-CA")}
          {points[hover.i].kind === "forecast" && (
            <span className="text-muted">
              {" "}({Math.round(points[hover.i].lo)} to {Math.round(points[hover.i].hi)})
            </span>
          )}
        </div>
      )}
    </div>
  );
}
