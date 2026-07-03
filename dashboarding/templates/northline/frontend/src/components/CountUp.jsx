import { useEffect, useRef, useState } from "react";

/* Animated number: counts from 0 to value once on mount, ~700ms, ease-out.
   Formatting stays the caller's job via the format prop. Respects
   prefers-reduced-motion by jumping straight to the value. */
export default function CountUp({ value, format = (v) => Math.round(v).toLocaleString("en-CA") }) {
  const [shown, setShown] = useState(0);
  const raf = useRef(null);

  useEffect(() => {
    if (typeof value !== "number" || !isFinite(value)) return;
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setShown(value);
      return;
    }
    const t0 = performance.now();
    const dur = 700;
    const tick = (t) => {
      const p = Math.min(1, (t - t0) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setShown(value * eased);
      if (p < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [value]);

  if (typeof value !== "number" || !isFinite(value)) return <>{value ?? "–"}</>;
  return <>{format(shown)}</>;
}
