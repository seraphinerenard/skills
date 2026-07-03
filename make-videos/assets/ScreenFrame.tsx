// Browser-style frame for product footage or screenshots. Pass the screen
// content (Img, OffthreadVideo, or a live component) as children.

import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Palette} from './palette';
import {heavy} from './springs';

export const ScreenFrame: React.FC<{
  palette: Palette;
  /** Address-bar text, e.g. the product URL. Fictional domains only. */
  url?: string;
  children: React.ReactNode;
  widthPct?: number;
}> = ({palette, url, children, widthPct = 74}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const enter = spring({frame, fps, config: heavy, durationInFrames: Math.round(fps * 1.2)});

  return (
    <div
      style={{
        width: `${widthPct}%`,
        margin: '0 auto',
        opacity: enter,
        transform: `translateY(${interpolate(enter, [0, 1], [70, 0])}px) scale(${interpolate(
          enter,
          [0, 1],
          [0.96, 1]
        )})`,
        borderRadius: 12,
        overflow: 'hidden',
        border: `1px solid ${palette.surface}`,
        boxShadow: '0 30px 80px rgba(0, 0, 0, 0.35)',
      }}
    >
      <div
        style={{
          backgroundColor: palette.surface,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '14px 18px',
        }}
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: 12,
              height: 12,
              borderRadius: 6,
              backgroundColor: palette.muted,
              opacity: 0.5,
            }}
          />
        ))}
        {url ? (
          <div
            style={{
              marginLeft: 14,
              color: palette.muted,
              fontSize: 20,
              fontFamily: 'Menlo, Consolas, monospace',
            }}
          >
            {url}
          </div>
        ) : null}
      </div>
      <div style={{backgroundColor: palette.bg}}>{children}</div>
    </div>
  );
};
