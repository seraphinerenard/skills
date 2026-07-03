# The Northline app is the shipped exemplar of the expressive tier

The Northline Coachworks app (`/path/to/skills/dashboarding/templates/northline`, a Vite + React + Tailwind v4 build) is the reference for what "stunning" means under this skill: saturated without slop, animated without noise, and colourful with meaning. Three weaker directions were built and discarded before it, and those are recorded at the end because they teach as much as the result. Screenshots: `northline-light.png` (Overview, light) and `northline-dark.png` (Production plan, dark).

## The decisions to imitate

1. **Vivid means full-strength fills, not brighter hues.** The first saturation pass swapped hexes and still read as pastel because bars ran at 55 to 80% opacity. Opacity-washing is what makes a palette depressing; the fix was dedicated fill tokens at 100% with text tones one step darker for contrast.
2. **Colour with meaning only.** Blue is the single brand colour (nav, selection, forecasts). Red, yellow, and green appear only as critical, warning, and healthy. Because every colour is semantic, the page can be saturated without turning carnival.
3. **Tonal surfaces carry the energy.** Insight banners and KPI tiles sit on Google 50-shade faces in light mode and on `color-mix(fill 14-16%, panel)` chips over near-black in dark mode. The tint does the emotional work; the type stays calm.
4. **The shell sells it before any chart loads.** A floating sidebar card on a tinted canvas, one icon per view each owning a primary (Hugeicons stroke icons inlined in `src/components/icons.jsx` per D23; the original build used duotone Phosphor), a rounded tonal chip for the active view, and a live ticker scrolling every below-band component across the top. The app reads as alive at first paint.
5. **One hero number at poster size.** The Overview leads with a bento grid whose double cell shows the service level at 64px Space Grotesk over a live area chart, with status pills beneath. Everything else stays quiet; the hierarchy is unmissable.
6. **Motion tells the data's story once.** Cards rise with a 60ms stagger, the demand line draws itself over its gradient area, bars grow from the baseline in sequence, numbers count up, the drawer slides, toasts rise. One easing curve, everything on entry only, and the lone loop (the attention dot) breathes slowly.
7. **Dark mode earns its keep with glow.** Chart bars, icons, and hero numerals cast soft halos mixed from their own colour over a #09090b canvas. Glow is confined to data marks and icons; surfaces never glow.

## The post-mortems behind rules D25 to D28

- **The strobe (D25).** With macOS Reduce Motion on, a blanket `animation-duration: 0.01ms` clamp turned the infinite ticker into a strobe restarting thousands of times a second. The reduced-motion block always sets `animation-iteration-count: 1` as well.
- **The flickering ticker (D26).** A CSS keyframe on the ticker promoted an ~11,000-physical-pixel track to one GPU texture, past compositor limits on Retina, and sub-pixel motion shimmered the text. Tickers are rAF integer-pixel scrollers with a measured-width wrap and hover-pause on the stationary wrapper.
- **The solid blob (D27).** A generic fade-in keyframe ending at `opacity: 1` overrode the forecast band's 0.14 opacity and rendered it as a solid shape. Fade keyframes end at `var(--target-opacity)`.
- **The flying bars (D28).** SVG rects animated with `scaleY` scale against the viewport unless `transform-box: fill-box` is set.

## Directions that were rejected

- A restrained dark cockpit: competent and inert. Restraint is not the same as quality when the surface is meant to carry energy.
- Desaturated cobalt, olive, and clay: muted palettes read as pastel beside the fully saturated tools people use all day.
- Token swaps sold as redesigns: until the shell changed (floating rail, ticker, bento hero, icons), every palette change still looked like "the same app, recoloured". Structure changes the look; tokens change the shade.
