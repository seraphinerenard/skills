/* The wordmark bus at empty-state size, drawing itself in stroke by stroke. */
export default function BusMark({ size = 96 }) {
  const strokes = [
    { d: "M8 18 h64 a8 8 0 0 1 8 8 v22 a8 8 0 0 1 -8 8 h-64 a8 8 0 0 1 -8 -8 v-22 a8 8 0 0 1 8 -8 z", len: 230 },
    { d: "M0 38 h80", len: 80 },
    { d: "M14 18 v20", len: 20 },
    { d: "M34 18 v20", len: 20 },
    { d: "M54 18 v20", len: 20 },
  ];
  return (
    <svg
      width={size}
      height={size * 0.9}
      viewBox="-4 8 92 66"
      fill="none"
      aria-hidden="true"
      className="mx-auto"
    >
      {strokes.map((s, i) => (
        <path
          key={i}
          d={s.d}
          stroke="var(--color-accent)"
          strokeWidth="2.5"
          strokeLinecap="round"
          className="draw-line"
          style={{ "--path-len": s.len, animationDelay: `${150 + i * 180}ms` }}
        />
      ))}
      <circle cx="20" cy="62" r="6" stroke="var(--color-accent)" strokeWidth="2.5"
        className="fade-late" style={{ animationDelay: "950ms" }} />
      <circle cx="60" cy="62" r="6" stroke="var(--color-accent)" strokeWidth="2.5"
        className="fade-late" style={{ animationDelay: "1050ms" }} />
    </svg>
  );
}
