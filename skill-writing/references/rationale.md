# Why each mechanism exists

Each entry names the observed small-model evasion and the mechanism that closes it. Read this when designing a new enforcement mechanism; routine authoring needs only SKILL.md.

## Narrated compliance

The dominant failure. The model prints "Running the sweep... all clear" without any tool call, or types a plausible checker output by hand. Closed by the proof line: `PASS <checker> v<N> file=<f> sha=<8hex>`. The sha comes from the file bytes; a model that did not run the script cannot produce it. The delivery block demands the line pasted verbatim, and the rule "the run must appear as a tool result" gives the user a one-glance audit.

## Post-check editing

The model runs the checker early (it passes on the half-built file), then keeps editing. Closed by "any edit after the run voids it; checks are the last action before the delivery block", plus the sha in the proof line, which stops matching the delivered file.

## Placeholder artifacts

Gate cards printed with `<the palette you chose>` still inside, or filled from imagination (invented hex that looks plausible). Closed by: placeholders fail the gate mechanically (`<`, `TODO`, `TBD`), and card fields that cite a table must quote the matched row verbatim. Copying is the one operation a small model performs reliably; the protocol converts every judgment into a copy.

## The unopened reference

"Pick a palette from references/typography-color.md" produces an improvised palette, because the model never opens the file. Closed by inverting the layout: binding values live inline in SKILL.md; references hold rationale. Where a file must be opened (starters), the proof is structural: `@keep` sentinels in the starter that the checker requires in the deliverable.

## Judgment it cannot compute

"Saturation under 80%", "spend boldness once", "density follows surface type". A small model has no colour math and no taste. Closed by S3: exact values in IF/THEN tables with ELSE rows. The ELSE row matters as much as the rows above it; without one, inputs that fall between rows produce improvisation.

## Hedges read as options

"Prefer X", "generally avoid Y" parse as advice, and advice loses to the model's defaults. Closed by the language law: MUST or a table row, nothing else, checker-enforced.

## Attention decay and context loss

Fifty tool calls into a build, the contract is gone from working attention; after compaction, it is gone from context entirely. Closed twice: the contract card reprinted at each phase transition (cheap, keeps the protocol in the recent window), and the contract comment embedded in the deliverable file (survives anything, enables resume, and lets the checker cross-validate declared against shipped, which catches silent drift).

## The helpful shortcut

The user says "just build it, skip the process" and the model silently drops every gate, or worse, drops them without being asked. Closed by the gate-skip audit: confirm once, record `GATE N SKIPPED (user)` in the delivery block. Skips become visible and attributable.

## Ceremony tax

If a typo fix triggers six gates, the user stops invoking skills and the whole system dies of friction. Closed by the scope gate at the top of every skill: trivial revisions of already-conforming files run final checks only.

## Fabricated diversity (conversational skills)

Twenty candidates that are four ideas paraphrased; a gauntlet that passes everything "with caveats". No script can check ideas, so the tables carry the enforcement: mechanism/customer/channel columns with quotas (padding becomes visible as duplicate cells), kill quotas (a soft gauntlet is detectable by its survival rate), and tag-distribution rules (all-medium tags are a re-tag instruction).

## Why python3 checkers

The original sweeps used `grep -nP`. BSD grep on macOS has no `-P`; every sweep died on the machine the skills run on, and the models self-attested instead of reporting the crash. python3 is present on macOS, handles unicode sanely, and lets the checker print rule IDs and proof lines. "Missing or crashing checker is a blocking failure to report" is the rule that turns tooling breakage into a signal instead of silence.
