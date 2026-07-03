// CONTRACT skill=make-videos mode=A palette=brand-neutral-slate scenes=3
// Copy this skeleton; replace scenes, keep the wiring.
// One TransitionSeries over the manifest; every scene premounts so springs
// never start late. Exits belong to the transitions, never to the scenes.

import React from 'react';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {SCENES, FPS, TRANSITION_FRAMES} from './scenes';
import {SceneCard} from './ExampleScene';

export const MainVideo: React.FC = () => {
  const items: React.ReactNode[] = [];
  SCENES.forEach((scene, i) => {
    items.push(
      <TransitionSeries.Sequence
        key={scene.id}
        durationInFrames={Math.round(scene.seconds * FPS)}
        premountFor={TRANSITION_FRAMES}
      >
        <SceneCard scene={scene} />
      </TransitionSeries.Sequence>,
    );
    if (i < SCENES.length - 1) {
      items.push(
        <TransitionSeries.Transition
          key={`${scene.id}-fade`}
          presentation={fade()}
          timing={linearTiming({durationInFrames: TRANSITION_FRAMES})}
        />,
      );
    }
  });
  return <TransitionSeries>{items}</TransitionSeries>;
};
