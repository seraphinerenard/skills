#!/usr/bin/env python3
"""check_video.py v1 - mechanical gate for video deliverables.

Usage: python3 check_video.py FILE [...]

Mode A sources (.tsx/.ts/.jsx/.js) and mode B pages (.html/.htm) get
mode-specific rules; V1/V2/V7 apply to both. Rule IDs match make-videos/SKILL.md.
Escape marker in a comment near the line: allow:V<n> <reason>.
Proof line per clean file: PASS check_video v1 file=<name> sha=<8hex>.
Exit 0 only when every file passes.
"""
import hashlib
import re
import sys
from pathlib import Path

CHECKER, VERSION = "check_video", "v1"

PALETTES = {
    "broadcast-dark", "paper-light", "terminal-green",
    "midnight-editorial", "brand-neutral-slate",
}

ALLOW = re.compile(r"allow:(V\d+)\s+(.{3,})")
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")
CONTRACT = re.compile(r"CONTRACT\s+skill=make-videos\s+([^\n]*)")
TWEEN = re.compile(r"\.(?:to|from|fromTo)\(")
LAYOUT_PROP = re.compile(
    r"\b(width|height|top|left|right|bottom|margin\w*|padding\w*|fontSize)\s*:")
MODE_A_EXT = {".tsx", ".ts", ".jsx", ".js"}
MODE_B_EXT = {".html", ".htm"}


def check_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    ext = path.suffix.lower()
    mode_a = ext in MODE_A_EXT
    mode_b = ext in MODE_B_EXT
    fails, allows, allow_map = [], [], []

    for i, ln in enumerate(lines, 1):
        for m in ALLOW.finditer(ln):
            allow_map.append((m.group(1), i))
            allows.append(f"ALLOW {m.group(1)} {path}:{i} {m.group(2).strip()}")

    def fail(rule, lineno, msg):
        if any(r == rule and abs(l - lineno) <= 2 for r, l in allow_map):
            return
        fails.append(f"FAIL {rule} {path}:{lineno} {msg}")

    for i, ln in enumerate(lines, 1):
        # V1 gradients / glow / particles (both modes)
        if re.search(r"(linear|radial|conic)-gradient", ln, re.I):
            fail("V1", i, "gradient")
        if re.search(r"\b(glow|particle)\b", ln, re.I) and "allow:" not in ln:
            fail("V1", i, "glow or particle effect")
        # V2 pure black (both modes)
        if re.search(r"#000000\b|#000\b", ln):
            fail("V2", i, "pure #000 background value")
        # V7 emoji / em or en dash (both modes)
        if EMOJI.search(ln):
            fail("V7", i, "emoji")
        if ("—" in ln or "–" in ln):
            fail("V7", i, "em or en dash")

        if mode_a:
            # V3 frame-driven only
            if re.search(r"\banimate-(pulse|spin|bounce|ping)\b", ln):
                fail("V3", i, "Tailwind animation class in a scene source")
            if re.search(r"\btransition\s*:", ln):
                fail("V3", i, "CSS transition in a scene source")
            if re.search(r"@keyframes|\banimation\s*:", ln):
                fail("V3", i, "CSS keyframe animation in a scene source")

        if mode_b:
            # V4 tween targets: transform and opacity only
            if TWEEN.search(ln):
                seg = ln[TWEEN.search(ln).start():]
                m = LAYOUT_PROP.search(seg)
                if m:
                    fail("V4", i, f"tween touches layout property {m.group(1)!r}")
            # V6 pinned GSAP
            if re.search(r"<script[^>]*src=[\"'][^\"']*gsap", ln, re.I):
                if not re.search(r"gsap@\d+\.\d+\.\d+", ln):
                    fail("V6", i, "GSAP script tag is not version-pinned")

    # file-level checks
    if mode_a and re.search(r"\bspring\(|\binterpolate\(", text) \
            and "useCurrentFrame" not in text:
        fail("V3", 0, "scene animates (spring/interpolate) without useCurrentFrame")

    if mode_b:
        if "prefers-reduced-motion" not in text:
            fail("V5", 0, "no prefers-reduced-motion handler")
        if not re.search(r"replay", text, re.I):
            fail("V5", 0, "no replay control")
        if "@keep:tokens" not in text:
            fail("V9", 0, "missing @keep:tokens sentinel on the palette block")
        if "@keep:eof" not in text:
            fail("V9", 0, "missing @keep:eof sentinel")

    needs_contract = mode_b or path.name in ("Root.tsx", "Video.tsx")
    cm = CONTRACT.search(text)
    if needs_contract and not cm:
        fail("V8", 0, "missing CONTRACT comment (skill=make-videos mode=.. palette=.. scenes=..)")
    elif cm:
        kv = {k: v.rstrip("-")
              for k, v in re.findall(r"(\w+)=([\w-]+)", cm.group(1))}
        mode, pal, scenes = kv.get("mode"), kv.get("palette"), kv.get("scenes")
        if mode not in ("A", "B"):
            fail("V8", 0, f"CONTRACT mode must be A or B, got {mode!r}")
        if not pal or (pal not in PALETTES and not pal.startswith("brand-")):
            fail("V8", 0, f"CONTRACT palette {pal!r} is not a named palette or brand-<name>")
        if not scenes or not scenes.isdigit():
            fail("V8", 0, f"CONTRACT scenes must be a count, got {scenes!r}")
        if mode_b and mode == "A":
            fail("V8", 0, "an .html deliverable declares mode=A")

    for a in allows:
        print(a)
    for f in fails:
        print(f)
    if fails:
        return False
    sha = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    print(f"PASS {CHECKER} {VERSION} file={path.name} sha={sha}")
    return True


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    ok = True
    for p in argv:
        ok = check_file(Path(p)) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
