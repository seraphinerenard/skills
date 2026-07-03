// Lower third: accent rule expands, then name and role slide in behind it.
// Positioned bottom-left inside title-safe margins.

import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Palette} from './palette';
import {snappy, smooth} from './springs';

export const LowerThird: React.FC<{
  name: string;
  role?: string;
  palette: Palette;
  fontFamily?: string;
}> = ({name, role, palette, fontFamily = 'Helvetica, Arial, sans-serif'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const ruleIn = spring({frame, fps, config: snappy, durationInFrames: Math.round(fps * 0.5)});
  const textIn = spring({
    frame,
    fps,
    config: smooth,
    delay: Math.round(fps * 0.2),
    durationInFrames: Math.round(fps * 0.6),
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: '6%',
        bottom: '8%',
        display: 'flex',
        alignItems: 'stretch',
        gap: 18,
        fontFamily,
      }}
    >
      <div
        style={{
          width: 8,
          backgroundColor: palette.accent,
          transform: `scaleY(${ruleIn})`,
          transformOrigin: 'bottom',
        }}
      />
      <div
        style={{
          backgroundColor: palette.surface,
          padding: '18px 28px',
          opacity: textIn,
          transform: `translateX(${interpolate(textIn, [0, 1], [-24, 0])}px)`,
        }}
      >
        <div style={{color: palette.text, fontSize: 38, fontWeight: 700}}>{name}</div>
        {role ? <div style={{color: palette.muted, fontSize: 26, marginTop: 4}}>{role}</div> : null}
      </div>
    </div>
  );
};
