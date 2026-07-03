// Closing card: wordmark rises out of a clipped line, accent underline expands,
// tagline fades in last. Use as the final scene with the CTA.

import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Palette} from './palette';
import {smooth, heavy} from './springs';

export const LogoReveal: React.FC<{
  name: string;
  tagline?: string;
  palette: Palette;
  fontFamily?: string;
}> = ({name, tagline, palette, fontFamily = 'Helvetica, Arial, sans-serif'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const rise = spring({frame, fps, config: heavy, durationInFrames: Math.round(fps * 1.0)});
  const underline = spring({frame, fps, config: smooth, delay: Math.round(fps * 0.5)});
  const taglineIn = spring({frame, fps, config: smooth, delay: Math.round(fps * 0.8)});

  return (
    <AbsoluteFill
      style={{
        backgroundColor: palette.bg,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily,
      }}
    >
      <div style={{overflow: 'hidden', paddingBottom: 6}}>
        <div
          style={{
            color: palette.text,
            fontSize: 110,
            fontWeight: 800,
            letterSpacing: '-0.02em',
            transform: `translateY(${interpolate(rise, [0, 1], [130, 0])}px)`,
          }}
        >
          {name}
        </div>
      </div>
      <div
        style={{
          height: 6,
          width: 240,
          backgroundColor: palette.accent,
          marginTop: 18,
          transform: `scaleX(${underline})`,
        }}
      />
      {tagline ? (
        <div
          style={{
            color: palette.muted,
            fontSize: 34,
            marginTop: 26,
            opacity: taglineIn,
            transform: `translateY(${interpolate(taglineIn, [0, 1], [16, 0])}px)`,
          }}
        >
          {tagline}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
