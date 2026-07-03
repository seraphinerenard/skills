// CONTRACT skill=make-videos mode=A palette=brand-neutral-slate scenes=3
// Copy this skeleton; replace scenes, keep the wiring.
// Duration is COMPUTED from the manifest: sum of scene frames minus one
// transition overlap per crossfade. Hand-timing durations is a failed gate;
// when VO exists, scene seconds in scenes.ts come from the measured MP3s.

import React from 'react';
import {Composition} from 'remotion';
import {MainVideo} from './Video';
import {SCENES, FPS, TRANSITION_FRAMES} from './scenes';

const totalFrames = (): number => {
  const sceneFrames = SCENES.reduce(
    (sum, s) => sum + Math.round(s.seconds * FPS),
    0,
  );
  return sceneFrames - (SCENES.length - 1) * TRANSITION_FRAMES;
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Main"
      component={MainVideo}
      width={1920}
      height={1080}
      fps={FPS}
      durationInFrames={totalFrames()}
      calculateMetadata={async () => {
        // Recomputed here so edits to scenes.ts (or audio-measured seconds
        // written into it) always win over any stale prop.
        return {durationInFrames: totalFrames()};
      }}
    />
  );
};
