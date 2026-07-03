// One animated number with its unit and baseline. A number without a baseline
// is decoration, so the baseline prop is required.

import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Palette} from './palette';
import {snappy, smooth} from './springs';

export const StatCounter: React.FC<{
  value: number;
  /** e.g. "%", "ms", "$/file". Rendered after the number. */
  unit?: string;
  /** The comparison that makes the number mean something, e.g. "down from 11 days". */
  baseline: string;
  palette: Palette;
  decimals?: number;
  /** Local frame at which the count starts. */
  delay?: number;
  fontFamily?: string;
}> = ({value, unit, baseline, palette, decimals = 0, delay = 0, fontFamily = 'Helvetica, Arial, sans-serif'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const progress = spring({
    frame,
    fps,
    config: snappy,
    delay,
    durationInFrames: Math.round(fps * 1.1),
  });
  const shown = interpolate(progress, [0, 1], [0, value]);
  const baselineIn = spring({frame, fps, config: smooth, delay: delay + Math.round(fps * 0.5)});

  return (
    <div style={{fontFamily, textAlign: 'left'}}>
      <div style={{display: 'flex', alignItems: 'baseline', gap: 12}}>
        <span
          style={{
            color: palette.accent,
            fontSize: 120,
            fontWeight: 700,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {shown.toLocaleString('en-CA', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
          })}
        </span>
        {unit ? (
          <span style={{color: palette.accent, fontSize: 56, fontWeight: 600}}>{unit}</span>
        ) : null}
      </div>
      <div
        style={{
          color: palette.muted,
          fontSize: 30,
          marginTop: 10,
          opacity: baselineIn,
          transform: `translateY(${interpolate(baselineIn, [0, 1], [14, 0])}px)`,
        }}
      >
        {baseline}
      </div>
    </div>
  );
};
