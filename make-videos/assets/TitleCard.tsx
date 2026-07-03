// Full-screen title scene: kicker rises first, title follows one beat later.
// Entrances only; exits belong to the TransitionSeries wrapping the scene.

import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Palette} from './palette';
import {smooth} from './springs';

export const TitleCard: React.FC<{
  title: string;
  kicker?: string;
  palette: Palette;
  fontFamily?: string;
}> = ({title, kicker, palette, fontFamily = 'Helvetica, Arial, sans-serif'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const kickerIn = spring({frame, fps, config: smooth, durationInFrames: Math.round(fps * 0.6)});
  const titleIn = spring({
    frame,
    fps,
    config: smooth,
    delay: Math.round(fps * 0.25),
    durationInFrames: Math.round(fps * 0.8),
  });
  const ruleIn = spring({frame, fps, config: smooth, delay: Math.round(fps * 0.55)});

  return (
    <AbsoluteFill
      style={{
        backgroundColor: palette.bg,
        justifyContent: 'center',
        padding: '0 12%',
        fontFamily,
      }}
    >
      {kicker ? (
        <div
          style={{
            color: palette.muted,
            fontSize: 34,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            opacity: kickerIn,
            transform: `translateY(${interpolate(kickerIn, [0, 1], [24, 0])}px)`,
            marginBottom: 28,
          }}
        >
          {kicker}
        </div>
      ) : null}
      <h1
        style={{
          color: palette.text,
          fontSize: 92,
          lineHeight: 1.08,
          fontWeight: 700,
          margin: 0,
          maxWidth: '18ch',
          opacity: titleIn,
          transform: `translateY(${interpolate(titleIn, [0, 1], [40, 0])}px)`,
        }}
      >
        {title}
      </h1>
      <div
        style={{
          height: 6,
          width: 180,
          backgroundColor: palette.accent,
          marginTop: 40,
          transform: `scaleX(${ruleIn})`,
          transformOrigin: 'left',
        }}
      />
    </AbsoluteFill>
  );
};
