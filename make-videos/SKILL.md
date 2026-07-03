---
name: make-videos
description: |
  Create go-to-market and instructional videos. Trigger on: "make a video", "GTM video",
  "product video", "launch video", "explainer", "tutorial video", "/make-videos".
  TWO MODES chosen at the first gate: (A) Remotion MP4 for anything posted, shared, or
  narrated; (B) a self-contained GSAP motion page for silent in-browser animation.
  Begin at GATE V-1 of THE CONTRACT: print the mode-and-palette gate card, then the
  storyboard artifact, before any code. scripts/check_video.py and the writing sweep
  MUST pass before delivery. Mode A implementation follows the remotion-best-practices
  skill. Prerequisites inlined below; the full skills win on conflict.
---

# Make videos

A video built here tells one story, one claim per scene, on one palette, with motion only when a claim enters or leaves. The machine default (logo intro, ambient particles, six claims per scene, a music bed that ducks nothing) is what these gates prevent. Every deliverable starts from a shipped starter, the storyboard is approved before the first component exists, and two checkers gate delivery.

Set `SKILL_DIR=$HOME/.claude/skills/make-videos` (fallback: `/path/to/skills/make-videos`).

## Scope gate

IF the request edits an existing file that already contains a `CONTRACT skill=make-videos` comment: make the edit, run both checks (below), paste the proof lines, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE V-1** | Pick the mode from the mode table and the palette from the palette table | V-1 gate card (template below) | Card printed; mode row and palette row cited verbatim; no `<`, `TODO`, `TBD` |
| **GATE V-2** | GTM video: run the ideation skill's story phase (candidate stories, the user chooses by AskUserQuestion; if that tool is unavailable, present options as text and STOP). Instructional video: skip ideation. Then write the storyboard | STORYBOARD table (template below) with its arithmetic line, approved by the user | Every claim at most 12 words; scene seconds sum inside the arc budget; user approval recorded |
| **GATE V-3** | Write the full script (every on-screen word and every VO line) to a file; run the writing sweep on it | Sweep proof line on the script file | `PASS sweep` as a tool result; fixes applied |
| **GATE V-4** | Build per mode (Values below). Mode A: scaffold from `$SKILL_DIR/assets/skeleton/`, components per storyboard line, VO per remotion-best-practices. Mode B: `cp $SKILL_DIR/demos/motion-page.html <name>.html`, replace scenes on the labelled timeline | The scene sources on disk with their CONTRACT comment | One claim per scene; frame-driven only (A) or transform-and-opacity only (B); one palette throughout |
| **GATE V-5** | Run `check_video.py` AND `sweep.py` on the sources; watch the deliverable start to finish at 1x | Both proof lines as tool results, plus one line: "watched at 1x, <m:ss> total" | Zero FAILs, or each `allow:` justified in one line |
| **GATE V-6** | Deliver | DELIVERY block | Proof lines pasted; block ends the message |

Restated because they are the three most-violated rules, binding during V-2 and V-4: every scene makes exactly one claim of at most 12 on-screen words (V10); mode A animates only from `useCurrentFrame()`, CSS transitions and keyframes do not render (V3); mode B tweens only `transform` and `opacity` (V4); one palette for the whole video, at most one accent element on screen at a time (V11).

## Values

**Mode table.**

| IF the deliverable | THEN |
|---|---|
| Will be posted, shared as a file, or carries narration or music | Mode A: Remotion MP4 |
| Is a silent animation living inside a web page | Mode B: GSAP motion page |
| Needs both | Mode A first; the page embeds the MP4 |
| ELSE | Ask the user, then stop until answered |

Never record a browser as the "video file": wall-clock capture drops frames and cannot mix audio.

**Palettes.** Pick ONE row; the gate card quotes it verbatim. Usage notes per palette are in `references/palettes.md`; the values here are the authority.

| Name | bg | surface | text | muted | accent | accent2 |
|---|---|---|---|---|---|---|
| broadcast-dark | #0B0E13 | #151A22 | #E9EDF2 | #8B95A5 | #E0483E | #E5B84B |
| paper-light | #F4F5F7 | #FFFFFF | #1F242C | #667085 | #2B59C3 | #B0492C |
| terminal-green | #0C1210 | #141C17 | #D9E5DE | #7E8F85 | #46C97E | #D9B44A |
| midnight-editorial | #101624 | #1B2334 | #ECE9E1 | #8E97AB | #E36756 | #7FA8C9 |
| brand-neutral-slate | #17191E | #22252C | #E7E9ED | #9AA1AC | #1B8A7D | #C86A2C |
| ELSE (client brand) | Map darkest neutral to bg, next step to surface, lightest to text, mid neutral to muted, primary to accent, secondary to accent2. Text-on-bg contrast MUST be at least 7:1; never purple and blue paired across accent and accent2. Record as `palette=brand-<name>` in the gate card with the mapping | | | | | |

Defaults when the brief names no palette: GTM for a technical or financial audience = broadcast-dark; instructional or bright-office viewing = paper-light; developer tools = terminal-green; executive brand film = midnight-editorial; brand hexes arriving later = brand-neutral-slate.

**Pacing budgets (binding).**

| Measure | Budget |
|---|---|
| VO pace | at most 2.5 words per second (150 words per minute) |
| VO script for a 60 s video | at most 150 words |
| Silence | at least 15% of runtime carries no VO |
| Words on screen at once | at most 12 outside UI screenshots |
| Hold time per claim | reading time x 1.5, minimum 2 s (reading = 3 words per second) |
| Type size | titles at least 8% of frame height, body at least 5% |
| Claim or stat card | 2 to 5 s |
| Product footage | 4 to 8 s per workflow moment |
| Any single static frame | 6 s maximum before something moves or cuts |

**Arcs.**

| GTM beat (45 to 90 s total) | Seconds | Content |
|---|---|---|
| Hook | 2 to 4 | One claim or number, full screen. No logo, no intro |
| Problem | 8 to 15 | The cost of the status quo in numbers the viewer recognizes |
| Turn | 10 to 25 | Real interface in a ScreenFrame, one workflow. Product on screen by second 15 |
| Proof | 8 to 15 | StatCounters with baselines, or a named fictional customer result |
| CTA | 4 to 8 | LogoReveal plus ONE action |

| Instructional beat (60 to 180 s total) | Seconds | Content |
|---|---|---|
| Objective | 4 to 8 | "By the end you can X", plus any prerequisite |
| Setup | 5 to 10 | The starting state, one screen, labelled |
| Steps | 10 to 20 each | One step per scene; result shown before the next step; failure mode scripted |
| Recap | 6 to 10 | The steps as one list, plus where to go when it breaks |

**Scene-count arithmetic.** A 60-second GTM video is 7 to 10 scenes. IF the storyboard exceeds 15 scenes: cut claims, never seconds per scene. Past 90 seconds a GTM video becomes two videos; past 180 seconds an instructional video becomes a chaptered series.

**Springs (mode A).** Every entrance uses a named preset from `assets/springs.ts`: `smooth` (damping 200) for text that lands and holds; `snappy` (damping 20, stiffness 200) for UI and counters; `heavy` (damping 15, stiffness 80, mass 2) for full-screen panels. Ad-hoc spring configs are banned.

**Components (mode A).** `assets/` ships drop-in Remotion 4 components, all frame-driven, all palette-typed: TitleCard (claim scene), StatCounter (number with required unit and baseline props), KineticText (word-stagger for one sentence), LowerThird (name and role), ScreenFrame (browser frame for product footage), LogoReveal (closing wordmark), palette.ts, springs.ts.

**Starters (copy, don't create).**

| Mode | Command |
|---|---|
| A | `cp -r $SKILL_DIR/assets/skeleton <project>` then `mkdir -p <project>/src/assets && cp $SKILL_DIR/assets/*.tsx $SKILL_DIR/assets/*.ts <project>/src/assets/` |
| B | `cp $SKILL_DIR/demos/motion-page.html <name>.html` |
| ELSE | IF a `cp` fails: stop and report the path; starting from an empty file is a failed gate |

Mode A build order after copying: edit `src/scenes.ts` (the manifest: id, seconds, claim per storyboard line), one component per scene, `npx remotion studio` to iterate, VO via ElevenLabs per remotion-best-practices (ask the user for `ELEVENLABS_API_KEY`; a silent fallback to another TTS is a failed gate), MP3s to `public/voiceover/`, scene lengths derive from measured audio through `calculateMetadata`, render with `npx remotion render Main out/<name>.mp4`. Mode B build order: replace scene markup, append tweens under that scene's label on the one master timeline, keep the stage scaling, replay control, and reduced-motion machinery.

## Artifact templates

```gate-card
GATE V-1 - mode and palette
mode: <A | B>    [row: "<the mode table row, pasted verbatim>"]
palette: <name>    [row: "<the palette row, pasted verbatim>"]
arc: <GTM | instructional>
runtime target: <seconds>
audience: <who watches this and where>
end-of-card
```

```storyboard
STORYBOARD - <deliverable name>
| # | claim (max 12 words) | visual | seconds |
|---|---|---|---|
| 1 | <claim> | <number, product view, or diagram> | <s> |
arithmetic: <n> scenes, <sum> s total, budget <45-90 GTM | 60-180 instructional>: <PASS | FAIL>
approval: <the user's approving words, quoted>
end-of-card
```

The CONTRACT comment, written into the deliverable at GATE V-4 (mode B: after the doctype; mode A: first line of `src/Root.tsx` and `src/Video.tsx`):

```
<!-- CONTRACT skill=make-videos mode=B palette=broadcast-dark scenes=5 -->
// CONTRACT skill=make-videos mode=A palette=brand-neutral-slate scenes=3
```

### Inlined from writing-instructions (full skill wins on conflict)

Every on-screen sentence and VO line: no contrast framing ("it's not X, it's Y"), no em dashes, no emoji, sentence case. Numbers carry units and baselines ("closes in 4 hours, down from 11"); a number without a baseline is decoration, and StatCounter makes the baseline a required prop for this reason. Kill list: delve, robust, seamless, leverage, streamline, unlock, elevate, empower, holistic, synergy, actionable, transformative, journey, landscape (figurative), AI-powered, game-changer. Canadian spelling. Fictional companies and uneven numbers only.

## Rules

Mechanical rules (checker-enforced):

| ID | Rule |
|---|---|
| V1 | No gradients (linear, radial, conic), no glow effects, no particle fields, in any frame or style. |
| V2 | No pure #000000 or #000 backgrounds; the palette's near-black is the stage. |
| V3 | Mode A: all animation derives from `useCurrentFrame()`. No CSS `transition:`, no `@keyframes`, no `animation:`, no Tailwind `animate-*` classes in scene sources; a scene that animates without `useCurrentFrame` fails. |
| V4 | Mode B: tweens touch `transform` and `opacity` only. Tweening width, height, top, left, margin, padding, or fontSize fails. |
| V5 | Mode B: a `prefers-reduced-motion` handler lands on the final composed frame, and a keyboard-reachable replay control exists. No autolooping. |
| V6 | Mode B: GSAP loads from a pinned-version URL (`gsap@<x.y.z>`); everything else lives in the one file. |
| V7 | No emoji; no em or en dashes in copy or code. |
| V8 | CONTRACT comment present (mode, palette, scenes); the palette name is one of the five or `brand-<name>`. |
| V9 | Mode B: `@keep:tokens` on the palette block and `@keep:eof` at the end (proof the starter was copied). |

Build rules (MUST, verified at V-4 and V-5):

| ID | Rule |
|---|---|
| V10 | One claim per scene, at most 12 on-screen words. A second sentence is a second scene. |
| V11 | One palette for the whole video; at most one accent element on screen at a time; `accent2` only for a second data series. |
| V12 | The hook is a claim, never a logo; the logo closes (LogoReveal), never opens. |
| V13 | Every element enters and exits; nothing pops between frames. Mode A exits belong to `@remotion/transitions` (budget for the overlap); mode B exits are timeline tweens. At most one signature move per scene; stillness between entrances. |
| V14 | Numbers on screen carry a unit and a baseline. |
| V15 | Mode A audio: music ducks at least 12 dB under VO; scene lengths derive from measured audio, never hand-timed; no typewriter effects (word-stagger via KineticText, one sentence only). |
| V16 | No stock icons, clip art, or synthetic product mocks passed as real; the product itself, a number, or nothing. Fictional names only. |
| V17 | Text below 5% of frame height is unreadable at phone size; cut words, never shrink type. |
| V18 | ELSE: a situation these rows do not cover follows `references/html-motion.md` (mode B) or the remotion-best-practices skill (mode A); when neither answers it, ask the user. |

## Checks

```
python3 $SKILL_DIR/scripts/check_video.py <files: .html and scene .tsx/.ts sources>
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <script file and .html>
```

Both MUST pass, as tool results, after the last edit, plus the 1x watch attestation with the runtime. `check_video.py` prints `FAIL V<n> file:line` per violation, honours `allow:V<n> <reason>` markers (counted), and ends `PASS check_video v1 file=<name> sha=<8hex>`. A missing or crashing checker is a blocking failure to report, never a licence to self-attest.

## Delivery block

```delivery-block
DELIVERY make-videos
files:
  <path>  (<size> B)
gates: <V-1..V-6 status, skips recorded>
checks:
  <check_video proof line(s), pasted>
  <sweep proof line(s), pasted>
  watched at 1x: <m:ss>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- `references/palettes.md`: per-palette usage rules and the brand-swap procedure (hex values above are the authority).
- `references/story-structures.md`: the arcs in depth, VO scripting notes, scene-count worked examples.
- `references/html-motion.md`: the full mode B doctrine (one master timeline, autoplay vs scroll-driven, performance rules).
- The remotion-best-practices skill: mode A implementation detail (springs, sequences, transitions, fonts, audio, captions, rendering).
- `demos/motion-page.html`: the mode B starter and quality target. `assets/skeleton/`: the mode A starter.
