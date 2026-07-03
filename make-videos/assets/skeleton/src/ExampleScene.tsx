// Copy this skeleton; replace scenes, keep the wiring.
// One component per storyboard line. This example renders every scene as a
// TitleCard; a real video swaps in StatCounter, ScreenFrame, KineticText,
// or LogoReveal per the storyboard's visual column.

import React from 'react';
import {TitleCard} from './assets/TitleCard';
import {brandNeutralSlate} from './assets/palette';
import type {Scene} from './scenes';

export const SceneCard: React.FC<{scene: Scene}> = ({scene}) => {
  return (
    <TitleCard
      title={scene.claim}
      kicker={scene.kicker}
      palette={brandNeutralSlate}
    />
  );
};
