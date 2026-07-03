#!/usr/bin/env python3
"""check_design.py v1 - mechanical design gate for HTML deliverables.

Usage: python3 check_design.py FILE.html [...]

Enforces rules D1-D16 from design/SKILL.md. Colour literals of any syntax may
exist only inside :root rules (D2). Cross-validates the CONTRACT comment
against the shipped CSS (D16). Escape marker in a comment near the line:
allow:D<n> <reason>. Proof line per clean file:
PASS check_design v1 file=<name> sha=<8hex>. Exit 0 only when all files pass.
"""
import hashlib
import re
import sys
from pathlib import Path

CHECKER, VERSION = "check_design", "v1"

PALETTES = {
    "mono-pop":         {"accent": "#1f4ed8"},
    "cold-luxury":      {"accent": "#2f4156"},
    "forest":           {"accent": "#2d5a3d"},
    "cobalt-cream":     {"accent": "#1f4ed8"},
    "terracotta-slate": {"accent": "#b4553c"},
    "olive-brick":      {"accent": "#6b6b33"},
    "black-tan":        {"accent": "#c8a26a"},
    "graphite-dark":    {"accent": "#6d8aff"},
    "vivid-enterprise": {"accent": "#1a73e8"},
}

BANNED_HEX = {
    "#f5f1ea", "#f7f5f1", "#fbf8f1", "#efeae0", "#ece6db", "#faf7f1",
    "#e8dfcb", "#b08947", "#b6553a", "#9a2436", "#9c6e2a", "#bc7c3a",
    "#7d5621", "#1a1714", "#1a1814", "#1b1814",
}
BANNED_FIRST_FONTS = {"inter", "fraunces", "instrument serif", "poppins", "roboto"}
NAMED_COLOURS = (
    r"white|black|red|blue|green|purple|violet|indigo|pink|orange|yellow|"
    r"teal|cyan|magenta|grey|gray|silver|gold|crimson|salmon|navy"
)
COLOUR_PROPS = (
    r"color|background(?:-color)?|border[\w-]*|fill|stroke|outline[\w-]*|"
    r"caret-color|text-decoration-color|box-shadow|text-shadow|column-rule"
)

ALLOW = re.compile(r"allow:(D\d+)\s+(.{3,})")
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")
CONTRACT = re.compile(r"CONTRACT\s+skill=design\s+(.*?)(?:-->|\*/|$)")


def check_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    fails, allows, allow_map = [], [], []

    for i, ln in enumerate(lines, 1):
        for m in ALLOW.finditer(ln):
            allow_map.append((m.group(1), i))
            allows.append(f"ALLOW {m.group(1)} {path}:{i} {m.group(2).strip()}")

    def fail(rule, lineno, msg):
        if any(r == rule and abs(l - lineno) <= 2 for r, l in allow_map):
            return
        fails.append(f"FAIL {rule} {path}:{lineno} {msg}")

    # ---- pass 1: state-tracked line scan ----
    in_style = in_script = False
    depth = 0
    root_stack = []          # depths at which a :root rule opened
    root_accent = None
    body_rule_buf, in_body_rule = "", False

    for i, ln in enumerate(lines, 1):
        low = ln.lower()
        if "<style" in low:
            in_style = True
        if "<script" in low:
            in_script = True
        css_ctx = in_style and not in_script
        in_root = bool(root_stack)

        stripped_comment = re.sub(r"<!--.*?-->", "", ln)
        no_comment = re.sub(r"/\*.*?\*/", "", stripped_comment)

        # D1 gradients / mesh / glow
        if re.search(r"(linear|radial|conic)-gradient", no_comment, re.I):
            fail("D1", i, "gradient")
        # D3 blur / glass
        if re.search(r"backdrop-filter|filter\s*:[^;}]*blur\(", no_comment, re.I):
            fail("D3", i, "blur or glass effect")
        # D4 pure black
        if re.search(r"#000000\b|#000\b", no_comment):
            fail("D4", i, "pure #000 black")
        # D5 banned hex families
        for h in re.findall(r"#[0-9a-fA-F]{6}\b", no_comment):
            if h.lower() in BANNED_HEX:
                fail("D5", i, f"banned hex family value {h}")
        # D6 emoji (whole raw line)
        if EMOJI.search(ln):
            fail("D6", i, "emoji")
        # D9 tailwind slop classes
        if re.search(r"\b(from|to|via)-(purple|violet|indigo|blue|fuchsia|pink)-\d+"
                     r"|backdrop-blur|blur-3xl|bg-gradient", no_comment):
            fail("D9", i, "banned utility class")
        # D10 cursor
        if re.search(r"cursor\s*:\s*(none|url\()", no_comment, re.I):
            fail("D10", i, "custom cursor")
        # D11 infinite animation
        if re.search(r"animation-iteration-count\s*:\s*infinite"
                     r"|animation\s*:[^;}]*\binfinite\b", no_comment, re.I):
            fail("D11", i, "infinite animation")
        # D12 scroll listener
        if re.search(r"addEventListener\(\s*['\"](scroll|wheel)", no_comment):
            fail("D12", i, "scroll listener driving style")
        # D13 external resources
        if re.search(r"(src|srcset)\s*=\s*[\"']https?://", no_comment, re.I) or \
           re.search(r"<link[^>]*href\s*=\s*[\"']https?://", no_comment, re.I) or \
           re.search(r"url\(\s*[\"']?https?://", no_comment, re.I):
            fail("D13", i, "external resource load")
        # D14 banned first font
        for m in re.finditer(r"font-family\s*:\s*([^;}{]+)", no_comment, re.I):
            first = m.group(1).split(",")[0].strip().strip("\"'").lower()
            if first in BANNED_FIRST_FONTS:
                fail("D14", i, f"banned face {first!r} as chosen font")
        # D8 font-size floor
        for m in re.finditer(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", no_comment, re.I):
            if float(m.group(1)) < 12:
                fail("D8", i, f"font-size {m.group(1)}px under the 12px floor")
        for m in re.finditer(r"font\s*:\s*[^;}{]*?(\d+(?:\.\d+)?)px\s*/", no_comment, re.I):
            if float(m.group(1)) < 12:
                fail("D8", i, f"font shorthand {m.group(1)}px under the 12px floor")

        # D2 colour literals outside :root (CSS context, inline styles, svg attrs)
        segments = []
        if css_ctx and not in_root:
            segments.append(no_comment)
        for m in re.finditer(r"style\s*=\s*\"([^\"]*)\"", no_comment):
            segments.append(m.group(1))
        for m in re.finditer(r"\b(fill|stroke)\s*=\s*\"([^\"]*)\"", no_comment):
            if not m.group(2).startswith(("var(", "currentColor", "none", "url(")):
                segments.append(f"{m.group(1)}:{m.group(2)}")
        for seg in segments:
            seg_nourl = re.sub(r"url\([^)]*\)", "", seg)
            if re.search(r"#[0-9a-fA-F]{3,8}\b", seg_nourl):
                fail("D2", i, "colour literal outside :root")
            elif re.search(r"\b(rgba?|hsla?|oklch)\(", seg_nourl):
                fail("D2", i, "functional colour outside :root")
            elif re.search(rf"(?:{COLOUR_PROPS})\s*:\s*[^;}}{{]*\b(?:{NAMED_COLOURS})\b",
                           seg_nourl, re.I):
                fail("D2", i, "named colour value outside :root")

        # track :root and body rules, capture --accent
        if css_ctx:
            if re.search(r":root[^{}]*\{", ln):
                root_stack.append(depth)
            if re.search(r"(^|[}\s])body\s*[,{]", ln):
                in_body_rule = True
            if in_body_rule:
                body_rule_buf += ln + "\n"
                if "}" in ln:
                    in_body_rule = False
            if root_stack:
                m = re.search(r"--accent\s*:\s*(#[0-9a-fA-F]{3,8})", ln)
                if m and root_accent is None:
                    root_accent = m.group(1).lower()
            depth += ln.count("{") - ln.count("}")
            while root_stack and depth <= root_stack[-1]:
                root_stack.pop()
        if "</style>" in low:
            in_style = False
            depth = 0
            root_stack.clear()
        if "</script>" in low:
            in_script = False

    # ---- D15 sentinels ----
    if "@keep:tokens" not in text:
        fail("D15", 0, "missing @keep:tokens sentinel (deliverable not copied from a starter)")
    if "@keep:eof" not in text:
        fail("D15", 0, "missing @keep:eof sentinel")

    # ---- D16 contract comment cross-validation ----
    cm = CONTRACT.search(text)
    if not cm:
        fail("D16", 0, "missing CONTRACT comment")
    else:
        kv = dict(re.findall(r"(\w+)=([^\s]+)", cm.group(1)))
        pal, accent, body = kv.get("palette"), kv.get("accent", "").lower(), kv.get("body")
        if not pal or not accent or not body:
            fail("D16", 0, f"CONTRACT missing keys (need palette, accent, body): {kv}")
        else:
            if pal in PALETTES and PALETTES[pal]["accent"] != accent:
                fail("D16", 0, f"CONTRACT accent {accent} is not palette {pal}'s "
                               f"accent {PALETTES[pal]['accent']}")
            if pal not in PALETTES and not pal.startswith("brand-"):
                fail("D16", 0, f"unknown palette {pal!r} (use a named palette or brand-<name>)")
            if root_accent and root_accent != accent:
                fail("D16", 0, f"shipped --accent {root_accent} != CONTRACT accent {accent}")
            if body and body_rule_buf and body.replace("px", "") not in body_rule_buf:
                fail("D16", 0, f"declared body={body} not found in the body rule")

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
