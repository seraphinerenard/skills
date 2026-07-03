# Mode B: the HTML motion page

A mode B deliverable is one self-contained HTML file that plays a scripted motion sequence in the browser: no build step, no node toolchain, no audio track. It is the right mode when the animation lives on a web page (an embedded product demo, a launch-page hero sequence, an internal explainer). When the deliverable needs narration or will be posted as a file, stop and switch to mode A.

The shipped template is `demos/motion-page.html`. Copy it, replace the scenes, keep the machinery.

## One master timeline

All motion hangs off a single GSAP timeline. Scenes are labelled positions on that timeline, never independent `setTimeout` chains or CSS keyframe animations racing each other.

```js
const tl = gsap.timeline({paused: true, defaults: {ease: 'power3.out'}});

tl.addLabel('hook')
  .to('#hook .line', {y: 0, opacity: 1, duration: 0.7, stagger: 0.12})
  .to('#hook', {opacity: 0, duration: 0.4}, '+=2.2')
  .addLabel('problem')
  .fromTo('#problem', {opacity: 0}, {opacity: 1, duration: 0.4});
```

Why one timeline: scrubbing, replaying, and total-duration math all come free, and scene timing changes are one-line edits instead of a cascade of retuned delays. The labels are the storyboard's scene names; a reviewer should be able to read the timeline top to bottom against the storyboard.

## Autoplay or scroll-driven

Decide once, at storyboard time:

- **Autoplay** for a framed 16:9 stage that behaves like a video: play on load (after fonts settle), show a replay control at the end. This is the template's behaviour.
- **Scroll-driven** (GSAP ScrollTrigger with `scrub`) when the sequence annotates a long page rather than sitting in a frame. Never mix the two in one deliverable, and never hijack scroll for a framed stage.

Start autoplay only after `document.fonts.ready` resolves; text animating in a fallback font and swapping mid-tween is the most common visible defect in motion pages.

## Replay control

The end of the timeline reveals a plain replay button that calls `tl.play(0)`. No autolooping: a looping GTM page competes with the page's own content forever. The button is part of the stage, styled from the palette, and reachable by keyboard.

## Reduced motion

Respect `prefers-reduced-motion` before the timeline starts:

```js
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  tl.progress(1).pause();   // land on the final composed frame, fully readable
} else {
  document.fonts.ready.then(() => tl.play());
}
```

The final frame must therefore work as a static page: every claim readable, the CTA visible. Build scenes so the end state is the summary, not an empty stage.

## Performance rules

- Animate `transform` and `opacity` only. Animating `width`, `height`, `top`, `left`, `margin`, or `font-size` forces layout every frame and stutters on mid-range laptops.
- Set initial hidden states in CSS (`opacity: 0; transform: translateY(30px)`) so there is no flash of unanimated content before the script runs.
- `will-change: transform` on the two or three heaviest movers only; applying it broadly costs memory and helps nothing.
- One stage, absolutely positioned scenes, `overflow: hidden`. Scenes outside the current label sit at `opacity: 0` and `pointer-events: none`.
- The stage is a fixed 16:9 box scaled to fit its container with a CSS `aspect-ratio`; type sizes in the stage use container-relative units (`cqw`) or a root scale factor so the composition holds at any embed width.
- GSAP loads from a pinned-version CDN script tag; everything else (styles, markup, script) lives in the one file.

## What mode B never does

| Never | Because | Instead |
|---|---|---|
| CSS keyframe loops running alongside the timeline | Two clocks drift; scenes desynchronize | Everything on the GSAP timeline |
| Autoplaying audio | Browsers block it and users close the tab | Mode A carries narration |
| Scroll hijacking a framed stage | The page stops belonging to the reader | Autoplay in the frame, or true scroll-driven annotation |
| Infinite ambient motion (floating shapes, drifting gradients) | Decoration that costs battery and attention | Motion only when a claim enters or exits |
| Recording the page as the "video deliverable" | Wall-clock capture drops frames and cannot mix audio | Rebuild in mode A; the storyboard transfers directly |
