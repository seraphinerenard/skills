#!/usr/bin/env python3
"""check_skill.py v1 - protocol conformance checker for SKILL.md files.

Usage: python3 check_skill.py SKILL.md [more SKILL.md paths...]

Checks (rule IDs from skill-writing/SKILL.md):
  S6  line cap (420), required sections present and in order, contract <= 40 lines,
      frontmatter has name/description, description mentions a gate
  S7  hedge words outside code fences and ban lists
  S2  gate-card and delivery-block fenced templates present
  S9  emoji and em dashes outside code fences

Escape marker (inside any comment/table cell): allow:<RULE-ID> <reason>
Proof line per clean file: PASS check_skill v1 file=<name> sha=<8hex>
Exit 0 only when every file passes.
"""
import hashlib
import re
import sys
from pathlib import Path

CHECKER = "check_skill"
VERSION = "v1"

REQUIRED_SECTIONS = [
    "## Scope gate",
    "## The contract",
    "## Values",
    "## Artifact templates",
    "## Rules",
    "## Checks",
    "## Delivery block",
]

PREFIXES = {
    "W": "writing-instructions", "D": "design", "C": "make-charts",
    "V": "make-videos", "I": "ideation",
    "DB": "dashboarding", "E": "ai-engagements", "S": "skill-writing",
    "P": "write-proposals", "DOC": "make-documents", "CC": "client-comms",
    "AD": "analyze-data", "R": "review-deliverables", "DI": "discovery",
    "BK": "brand-kit", "DR": "demo-reframe", "M": "publish-mcp-tools",
    "AA": "accessibility-audit", "BG": "backtest-gauntlet",
    "PM": "post-mortems", "DO": "daemon-ops", "DP": "data-pipelines",
    "WP": "write-papers", "RF": "realtime-feeds",
}

HEDGES = re.compile(
    r"\b(prefer(s|red|ably)?|consider(ing|ed)?|generally|ideally|"
    r"where possible|try to|aim for|as appropriate|if possible)\b",
    re.IGNORECASE,
)
BAN_CONTEXT = re.compile(r"[Bb]anned|[Bb]an\b|[Aa]void|[Nn]ever|kill list", )
ALLOW = re.compile(r"allow:([A-Z]+\d*)\s+(.{3,})")
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]"
)


def check_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"FAIL S6 {path}:0 unreadable ({e})")
        return False
    lines = text.splitlines()
    fails, allows = [], []

    # collect allow markers
    allowed_ids = set()
    for i, ln in enumerate(lines, 1):
        for m in ALLOW.finditer(ln):
            allowed_ids.add((m.group(1), i))
            allows.append(f"ALLOW {m.group(1)} {path}:{i} {m.group(2).strip()}")

    def fail(rule, lineno, msg):
        if any(r == rule and abs(l - lineno) <= 1 for r, l in allowed_ids):
            return
        fails.append(f"FAIL {rule} {path}:{lineno} {msg}")

    # --- S6: line cap ---
    if len(lines) > 420:
        fail("S6", len(lines), f"file is {len(lines)} lines; cap is 420")

    # --- S6: frontmatter ---
    if not lines or lines[0].strip() != "---":
        fail("S6", 1, "missing frontmatter")
    else:
        try:
            end = lines[1:].index("---") + 1
        except ValueError:
            end = 0
            fail("S6", 1, "unterminated frontmatter")
        fm = "\n".join(lines[1:end])
        if "name:" not in fm:
            fail("S6", 1, "frontmatter missing name:")
        if "description:" not in fm:
            fail("S6", 1, "frontmatter missing description:")
        if not re.search(r"gate", fm, re.IGNORECASE):
            fail("S6", 1, "description does not mention the first gate")

    # --- S6: section order ---
    positions = []
    for sec in REQUIRED_SECTIONS:
        idx = next((i for i, ln in enumerate(lines, 1)
                    if ln.strip() == sec), None)
        if idx is None:
            fail("S6", 0, f"missing required section '{sec}'")
        positions.append((sec, idx))
    present = [(s, i) for s, i in positions if i is not None]
    if [i for _, i in present] != sorted(i for _, i in present):
        fail("S6", 0, "required sections out of order "
                      f"({', '.join(f'{s}@{i}' for s, i in present)})")

    # --- S6: contract length ---
    cidx = next((i for i, ln in enumerate(lines)
                 if ln.strip() == "## The contract"), None)
    if cidx is not None:
        nxt = next((j for j in range(cidx + 1, len(lines))
                    if lines[j].startswith("## ")), len(lines))
        span = nxt - cidx - 1
        if span > 40:
            fail("S6", cidx + 1, f"contract section is {span} lines; cap is 40")

    # --- fence-aware line scans ---
    in_fence = False
    saw_gate_card = saw_delivery = False
    for i, ln in enumerate(lines, 1):
        stripped = ln.strip()
        if stripped.startswith("```"):
            info = stripped.lstrip("`").strip()
            if info == "gate-card":
                saw_gate_card = True
            if info == "delivery-block":
                saw_delivery = True
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # S7 hedges (skip ban-list context and inline code spans)
        scan = re.sub(r"`[^`]*`", "", ln)
        if HEDGES.search(scan) and not BAN_CONTEXT.search(scan):
            fail("S7", i, f"hedge word: {HEDGES.search(scan).group(0)!r}")
        # S9 emoji / em dash
        if EMOJI.search(scan):
            fail("S9", i, "emoji codepoint in skill text")
        if "—" in scan:
            fail("S9", i, "em dash in skill text (write it as words or use a comma)")

    if not saw_gate_card:
        fail("S2", 0, "no ```gate-card fenced template found")
    if not saw_delivery:
        fail("S2", 0, "no ```delivery-block fenced template found")

    # --- prefix registered ---
    m = re.search(r"GATE ([A-Z]+)-?\d", text)
    if m and m.group(1) not in PREFIXES:
        fail("S6", 0, f"gate prefix {m.group(1)!r} not in the registry")

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
        print("usage: check_skill.py SKILL.md [...]")
        return 2
    ok = True
    for p in argv:
        ok = check_file(Path(p)) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
