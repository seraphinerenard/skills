// Video palettes. One palette per video, chosen before the first scene is built.
// Full usage rules live in references/palettes.md.

export type Palette = {
  name: string;
  /** Stage background. Never pure black (rule V2). */
  bg: string;
  /** Cards, frames, lower-third bars. */
  surface: string;
  /** Primary type. */
  text: string;
  /** Secondary type: kickers, baselines, captions. */
  muted: string;
  /** The single emphasis colour. Numbers, underlines, the CTA. */
  accent: string;
  /** Support colour for a second data series or a secondary highlight. */
  accent2: string;
};

export const broadcastDark: Palette = {
  name: 'Broadcast Dark',
  bg: '#0B0E13',
  surface: '#151A22',
  text: '#E9EDF2',
  muted: '#8B95A5',
  accent: '#E0483E',
  accent2: '#E5B84B',
};

export const paperLight: Palette = {
  name: 'Paper Light',
  bg: '#F4F5F7',
  surface: '#FFFFFF',
  text: '#1F242C',
  muted: '#667085',
  accent: '#2B59C3',
  accent2: '#B0492C',
};

export const terminalGreen: Palette = {
  name: 'Terminal Green',
  bg: '#0C1210',
  surface: '#141C17',
  text: '#D9E5DE',
  muted: '#7E8F85',
  accent: '#46C97E',
  accent2: '#D9B44A',
};

export const midnightEditorial: Palette = {
  name: 'Midnight Editorial',
  bg: '#101624',
  surface: '#1B2334',
  text: '#ECE9E1',
  muted: '#8E97AB',
  accent: '#E36756',
  accent2: '#7FA8C9',
};

export const brandNeutralSlate: Palette = {
  name: 'Brand-Neutral Slate',
  bg: '#17191E',
  surface: '#22252C',
  text: '#E7E9ED',
  muted: '#9AA1AC',
  accent: '#1B8A7D',
  accent2: '#C86A2C',
};

export const palettes = {
  broadcastDark,
  paperLight,
  terminalGreen,
  midnightEditorial,
  brandNeutralSlate,
} as const;

export type PaletteName = keyof typeof palettes;
