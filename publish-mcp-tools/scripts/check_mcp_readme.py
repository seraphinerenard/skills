#!/usr/bin/env python3
"""check_mcp_readme.py v1 - honesty gate for MCP server READMEs.

Usage: python3 check_mcp_readme.py README.md [...]

Enforces rules M1-M4 from publish-mcp-tools/SKILL.md:
  M1  a "## Limitations" section exists
  M2  overclaim phrases outside the Limitations section, unless the same line
      carries a scoping digit ("covers 34 of 41 endpoints"); "100%" always flags
  M3  the H1 title matches mcp-<action>-<domain>
  M4  no emoji

Escape marker in any comment or table cell: allow:M<n> <reason>
Proof line per clean file: PASS check_mcp_readme v1 file=<name> sha=<8hex>
Exit 0 only when every file passes.
"""
import hashlib
import re
import sys
from pathlib import Path

CHECKER, VERSION = "check_mcp_readme", "v1"

OVERCLAIMS = re.compile(
    r"\b(complete coverage|comprehensive coverage|"
    r"all (endpoints|apis|routes|methods)|"
    r"every (endpoint|api|route|field|method|resource|use case)|"
    r"fully support(s|ed)?|guaranteed|production-ready|enterprise-grade|"
    r"blazing(ly)? fast)\b",
    re.IGNORECASE,
)
HUNDRED = re.compile(r"\b100%")
NAME_PATTERN = re.compile(r"^mcp-[a-z0-9]+(-[a-z0-9]+)+$")
ALLOW = re.compile(r"allow:(M\d+)\s+(.{3,})")
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")


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

    # --- locate the Limitations section span ---
    lim_start = lim_end = None
    for i, ln in enumerate(lines, 1):
        s = ln.strip().lower()
        if lim_start is None and s.startswith("## limitations"):
            lim_start = i
            continue
        if lim_start is not None and lim_end is None and ln.strip().startswith("## "):
            lim_end = i
    if lim_start is not None and lim_end is None:
        lim_end = len(lines) + 1

    # --- M1 ---
    if lim_start is None:
        fail("M1", 0, 'missing "## Limitations" section')

    def in_limitations(lineno):
        return lim_start is not None and lim_start <= lineno < lim_end

    # --- M3: H1 title ---
    h1 = next(((i, ln) for i, ln in enumerate(lines, 1)
               if ln.startswith("# ")), None)
    if h1 is None:
        fail("M3", 0, "no H1 title to check the name against")
    else:
        title = h1[1][2:].strip().split()[0].strip("`")
        if not NAME_PATTERN.match(title):
            fail("M3", h1[0],
                 f"title {title!r} does not match mcp-<action>-<domain>")

    # --- fence-aware line scan for M2/M4 ---
    in_fence = False
    for i, ln in enumerate(lines, 1):
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if EMOJI.search(ln):
            fail("M4", i, "emoji")
        if in_fence or in_limitations(i):
            continue
        scan = re.sub(r"`[^`]*`", "", ln)
        # digits belonging to "100%" itself do not count as a scoping number
        has_digit = any(c.isdigit() for c in HUNDRED.sub("", scan))
        if not has_digit:
            seen = set()
            for m in OVERCLAIMS.finditer(scan):
                hit = m.group(0).lower()
                if hit not in seen:
                    seen.add(hit)
                    fail("M2", i, f"overclaim outside Limitations: {m.group(0)!r}")
        if HUNDRED.search(scan):
            fail("M2", i, 'unscoped "100%" claim outside Limitations')

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
