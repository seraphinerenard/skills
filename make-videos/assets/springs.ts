// Named spring presets. Every entrance in a video uses one of these three;
// mixing ad-hoc spring configs across scenes is what makes motion feel unplanned.
// Configs match the remotion-best-practices skill (rules/animations.md).

import type {SpringConfig} from 'remotion';

/** No overshoot. Titles, body text, anything that must land and hold still. */
export const smooth: Partial<SpringConfig> = {damping: 200};

/** Fast with a small settle. UI elements, counters, lower thirds. */
export const snappy: Partial<SpringConfig> = {damping: 20, stiffness: 200};

/** Slow and weighty. Full-screen panels, hero images, closing cards. */
export const heavy: Partial<SpringConfig> = {damping: 15, stiffness: 80, mass: 2};

export const springs = {smooth, snappy, heavy} as const;

export type SpringName = keyof typeof springs;
