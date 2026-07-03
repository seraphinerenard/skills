#!/usr/bin/env python3
"""smell_check.py v1 - proposal and SOW smell checker for ai-engagements.

Usage: python3 smell_check.py FILE [FILE...]

Flags soft commitments and unmeasured claims before they reach a client:
  E-SMELL  soft-commitment phrases (AI-powered, best-in-class, up to N%, ...)
  E-DENOM  a percentage quality claim with no denominator on the line

Scans prose only: markdown fences are skipped, HTML tags and script/style
bodies are stripped. Escape marker in a comment near the line:
allow:E-SMELL <reason>  or  allow:E-DENOM <reason>
Proof line per clean file: PASS smell_check v1 file=<name> sha=<8hex>
Exit 0 only when every file passes.
"""
import hashlib
import re
import sys
from pathlib import Path

CHECKER, VERSION = "smell_check", "v1"

SMELL = [
    (re.compile(r"subject to data availability", re.I), "soft commitment"),
    (re.compile(r"up to \d+(\.\d+)?\s*%", re.I), "one-sided range promise"),
    (re.compile(r"\bAI-powered\b", re.I), "advertising filler"),
    (re.compile(r"\bbest-in-class\b", re.I), "unmeasured superlative"),
    (re.compile(r"\bstate[- ]of[- ]the[- ]art\b", re.I), "unmeasured superlative"),
    (re.compile(r"\bhuman-level\b", re.I), "unmeasured claim"),
    (re.compile(r"\bindustry-leading\b", re.I), "unmeasured superlative"),
    (re.compile(r"\bworld-class\b", re.I), "unmeasured superlative"),
    (re.compile(r"\bturnkey\b", re.I), "soft commitment"),
    (re.compile(r"phase \d+ will explore", re.I), "unscoped future promise"),
    (re.compile(r"accuracy to be determined", re.I), "unpriced unknown"),
    (re.compile(r"\bfully automated\b", re.I),
     "automation claim; name the review queue or mark allow:E-SMELL"),
]
# conditional smells
INSIGHT = re.compile(r"\binsights?\b", re.I)
DECISION_NEARBY = re.compile(r"\b(decision|decide|act|action|reorder|approve|"
                             r"route|escalat)\w*\b", re.I)
SCALABLE = re.compile(r"\bscalab(le|ility)\b", re.I)
PCT_CLAIM = re.compile(r"\d+(\.\d+)?\s*%\s*(accuracy|precision|recall|"
                       r"pass rate|success|coverage)", re.I)
DENOM = re.compile(r"(of\s+\d|n\s*=\s*\d|\d+\s+cases|\d+\s+of\s+\d|frozen set)",
                   re.I)
ALLOW = re.compile(r"allow:(E-[A-Z]+)\s+(.{3,})")


def visible_lines(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    is_html = path.suffix.lower() in (".html", ".htm")
    in_fence = in_script = in_style = False
    for i, ln in enumerate(text.splitlines(), 1):
        raw = ln
        if not is_html:
            if ln.strip().startswith("```"):
                in_fence = not in_fence
                yield i, "", raw
                continue
            yield i, ("" if in_fence else re.sub(r"`[^`]*`", "", ln)), raw
        else:
            low = ln.lower()
            if "<script" in low:
                in_script = True
            if "<style" in low:
                in_style = True
            drop = in_script or in_style
            if "</script>" in low:
                in_script = False
            if "</style>" in low:
                in_style = False
            yield i, ("" if drop else re.sub(r"<[^>]*>", " ", ln)), raw


def check_file(path: Path) -> bool:
    fails, allows, allow_map = [], [], []
    rows = list(visible_lines(path))
    for i, _, raw in rows:
        for m in ALLOW.finditer(raw):
            allow_map.append((m.group(1), i))
            allows.append(f"ALLOW {m.group(1)} {path}:{i} {m.group(2).strip()}")

    def allowed(rule, lineno):
        return any(r == rule and abs(l - lineno) <= 2 for r, l in allow_map)

    for i, prose, _ in rows:
        if not prose.strip():
            continue
        if not allowed("E-SMELL", i):
            for rx, why in SMELL:
                m = rx.search(prose)
                if m:
                    fails.append(f"FAIL E-SMELL {path}:{i} {why}: {m.group(0)!r}")
            if INSIGHT.search(prose) and not DECISION_NEARBY.search(prose):
                fails.append(f"FAIL E-SMELL {path}:{i} 'insights' without a "
                             f"named decision on the line")
            if SCALABLE.search(prose) and not any(c.isdigit() for c in prose):
                fails.append(f"FAIL E-SMELL {path}:{i} 'scalable' without a "
                             f"load number on the line")
        if not allowed("E-DENOM", i):
            if PCT_CLAIM.search(prose) and not DENOM.search(prose):
                fails.append(f"FAIL E-DENOM {path}:{i} percentage claim with "
                             f"no denominator: {PCT_CLAIM.search(prose).group(0)!r}")

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
