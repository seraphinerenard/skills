// Word-by-word reveal for a single sentence. Frame-driven stagger; each word
// gets its own spring. Use for one sentence per scene, never for paragraphs.

import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Palette} from './palette';
import {smooth} from './springs';

export const KineticText: React.FC<{
  text: string;
  palette: Palette;
  /** Frames between word starts. Default is a third of a second. */
  staggerFrames?: number;
  fontSize?: number;
  /** Words to render in the accent colour, matched case-insensitively. */
  accentWords?: string[];
  fontFamily?: string;
}> = ({text, palette, staggerFrames, fontSize = 72, accentWords = [], fontFamily = 'Helvetica, Arial, sans-serif'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const stagger = staggerFrames ?? Math.max(2, Math.round(fps / 10));
  const words = text.split(' ');
  const accents = accentWords.map((w) => w.toLowerCase());

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        columnGap: '0.28em',
        rowGap: '0.1em',
        maxWidth: '20ch',
        fontFamily,
        fontSize,
        fontWeight: 700,
        lineHeight: 1.12,
      }}
    >
      {words.map((word, i) => {
        const progress = spring({
          frame,
          fps,
          config: smooth,
          delay: i * stagger,
          durationInFrames: Math.round(fps * 0.6),
        });
        const isAccent = accents.includes(word.toLowerCase().replace(/[.,;:!?]$/, ''));
        return (
          <span
            key={`${word}-${i}`}
            style={{
              display: 'inline-block',
              color: isAccent ? palette.accent : palette.text,
              opacity: progress,
              transform: `translateY(${interpolate(progress, [0, 1], [30, 0])}px)`,
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
