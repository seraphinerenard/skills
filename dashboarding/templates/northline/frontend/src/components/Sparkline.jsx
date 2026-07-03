/* Inline table sparkline: 96x22, no axes, last point marked. */
export default function Sparkline({ values, width = 96, height = 22 }) {
  if (!values || values.length < 2) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const x = (i) => (i / (values.length - 1)) * (width - 4) + 2;
  const y = (v) => 2 + (1 - (v - min) / (max - min || 1)) * (height - 6);
  const d = values.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join("");
  return (
    <svg width={width} height={height} className="inline-block align-middle">
      <path d={d} fill="none" style={{ stroke: "var(--color-muted)" }} strokeWidth="1.2" />
      <circle cx={x(values.length - 1)} cy={y(values[values.length - 1])} r="2"
        style={{ fill: "var(--color-accent-vivid)" }} />
    </svg>
  );
}
