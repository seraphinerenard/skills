// Copy this skeleton; replace scenes, keep the wiring.
// The manifest is the storyboard made executable: one entry per storyboard line.
// Root.tsx computes total duration from these seconds minus transition overlaps,
// so editing this file is the ONLY place scene timing changes.
// Note: this skeleton ships untested-by-compiler; run `npx remotion studio`
// after `npm install` and fix any surface errors before building scenes.

export const FPS = 30;

// 0.5 s crossfade between scenes. TransitionSeries SHORTENS total duration by
// this overlap per transition; the arithmetic in Root.tsx accounts for it.
export const TRANSITION_FRAMES = 15;

export type Scene = {
  id: string;
  seconds: number;
  claim: string; // max 12 words, rule V10
  kicker?: string;
};

export const SCENES: Scene[] = [
  {
    id: 'hook',
    seconds: 3,
    claim: 'The 7:40 left riders at the curb',
    kicker: 'Skylark for transit operators',
  },
  {
    id: 'problem',
    seconds: 4,
    claim: 'A route replan takes 11 days by hand',
    kicker: 'The planning gap',
  },
  {
    id: 'cta',
    seconds: 4,
    claim: 'Book a demo at skylark.example/demo',
    kicker: 'Skylark',
  },
];
