#!/usr/bin/env python3
"""check_chart.py v1 - mechanical chart gate for HTML chart deliverables.

Usage: python3 check_chart.py FILE.html [...]

Enforces rules C1-C8 from make-charts/SKILL.md:
  C1 title text contains a digit (a finding, not a topic label)
  C2 a "Source:" line exists
  C3 no gradients or glow/blur filters (allow:C3 for a sequential data scale)
  C4 no pie or donut charts
  C5 no emoji, no em/en dash in visible text
  C6 no #000000 / #000
  C7 @keep sentinels and CONTRACT comment (skill=make-charts form=... source=yes)
  C8 no legend markup under 4 series (label lines directly)

Escape marker in a comment within 2 lines: allow:C<n> <reason>
Proof line per clean file: PASS check_chart v1 file=<name> sha=<8hex>
Exit 0 only when every file passes.
"""
import hashlib
import re
import sys
from pathlib import Path

CHECKER, VERSION = "check_chart", "v1"

ALLOW = re.compile(r"allow:(C\d+)\s+(.{3,})")
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")
CONTRACT = re.compile(r"CONTRACT\s+skill=make-charts\s+(.*?)(?:-->|\*/|$)")
TITLE_RX = re.compile(
    r"<text[^>]*class=\"[^\"]*title[^\"]*\"[^>]*>(.*?)</text>"
    r"|<h1[^>]*>(.*?)</h1>|<h2[^>]*>(.*?)</h2>|<title[^>]*>(.*?)</title>",
    re.IGNORECASE | re.DOTALL,
)


def visible(line: str) -> str:
    return re.sub(r"<[^>]*>", " ", line)


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

    # C1 title heuristic: first title-ish element must contain a digit
    tm = TITLE_RX.search(text)
    if tm:
        title = next(g for g in tm.groups() if g is not None)
        title_plain = re.sub(r"<[^>]*>", "", title).strip()
        lineno = text[: tm.start()].count("\n") + 1
        if not any(c.isdigit() for c in title_plain):
            fail("C1", lineno,
                 f"title has no number (topic label, not a finding): {title_plain[:60]!r}")
    else:
        fail("C1", 0, "no title element found (<text class=title>, <h1>, <h2>, or <title>)")

    # C2 source line
    if "Source:" not in text:
        fail("C2", 0, "no 'Source:' line")

    in_script = in_style = False
    for i, ln in enumerate(lines, 1):
        low = ln.lower()
        if "<script" in low:
            in_script = True
        if "<style" in low:
            in_style = True
        no_comment = re.sub(r"<!--.*?-->", "", ln)
        no_comment = re.sub(r"/\*.*?\*/", "", no_comment)

        # C3 gradients and glow
        if re.search(r"(linear|radial|conic)-gradient|<(linear|radial)Gradient"
                     r"|feGaussianBlur|filter\s*:[^;}]*blur\(", no_comment, re.I):
            fail("C3", i, "gradient or glow/blur filter")
        # C4 pie / donut
        if re.search(r"\b(pie|donut|doughnut)\b", no_comment, re.I):
            fail("C4", i, "pie/donut chart marker")
        # C6 pure black
        if re.search(r"#000000\b|#000\b", no_comment):
            fail("C6", i, "pure #000 black")
        # C5 visible-text scan
        if not in_script and not in_style:
            vis = visible(no_comment)
            if EMOJI.search(vis):
                fail("C5", i, "emoji")
            if "—" in vis or "–" in vis:
                fail("C5", i, "em/en dash in visible text")

        if "</script>" in low:
            in_script = False
        if "</style>" in low:
            in_style = False

    # C7 sentinels + contract
    if "@keep:tokens" not in text:
        fail("C7", 0, "missing @keep:tokens sentinel (not copied from a starter)")
    if "@keep:eof" not in text:
        fail("C7", 0, "missing @keep:eof sentinel")
    cm = CONTRACT.search(text)
    if not cm:
        fail("C7", 0, "missing CONTRACT comment (skill=make-charts)")
    else:
        kv = dict(re.findall(r"(\w+)=([^\s]+)", cm.group(1)))
        if "form" not in kv:
            fail("C7", 0, "CONTRACT missing form=")
        if kv.get("source") != "yes":
            fail("C7", 0, "CONTRACT missing source=yes")

    # C8 legend heuristic
    legend_m = re.search(r"class=\"[^\"]*legend|id=\"legend", text, re.I)
    if legend_m:
        series = max(
            len(re.findall(r"class=\"[^\"]*series", text, re.I)),
            len(re.findall(r"data-series", text, re.I)),
            len(re.findall(r"<polyline", text, re.I)),
        )
        if series < 4:
            lineno = text[: legend_m.start()].count("\n") + 1
            fail("C8", lineno,
                 f"legend markup with only {series} detected series; label lines directly")

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
