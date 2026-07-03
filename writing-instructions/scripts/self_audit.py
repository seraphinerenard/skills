#!/usr/bin/env python3
"""self_audit.py v2 - prove a skill file follows the writing rules it teaches.

Usage: python3 self_audit.py [SKILL.md ...]   (default: writing-instructions/SKILL.md)

Runs sweep.py over each file and sorts every hit into two piles. Specimen
zones hold the teaching material and are expected to trip the sweep:
double-quoted spans, blockquote demonstrations, the first column of any
table row (the banned-pattern column by repo convention), and the two
ban-list tables in writing-instructions itself. Everything else is the
instructional voice, and a hit there means the file violates its own rules
and primes the model with the register it bans.

Exit 0 with a proof line per clean file; exit 1 listing each voice violation.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

CHECKER, VERSION = "self_audit", "v2"


def in_ban_table(src, lineno):
    line = src[lineno - 1]
    if not line.lstrip().startswith("|"):
        return False
    for j in range(lineno - 1, max(0, lineno - 40), -1):
        s = src[j].strip()
        if s.startswith("### ") or s.startswith("## ") or s.startswith("**"):
            return "Canadian English" in s or "kill list" in s
    return False


def in_first_column(line, snippet):
    if not line.lstrip().startswith("|"):
        return False
    cells = line.split("|")
    return len(cells) > 1 and snippet in cells[1]


def audit_file(path: Path, sweep: Path) -> bool:
    src = path.read_text(encoding="utf-8").splitlines()
    out = subprocess.run([sys.executable, str(sweep), str(path)],
                         capture_output=True, text=True).stdout
    fails = [l for l in out.splitlines() if l.startswith("FAIL")]
    voice = []
    for f in fails:
        m = re.match(r"FAIL \S+ \S+:(\d+) ", f)
        if not m:
            voice.append((0, f))
            continue
        lineno = int(m.group(1))
        snippet = f.rsplit(": ", 1)[-1].strip("'\"")
        line = src[lineno - 1]
        quoted = any(snippet in q for q in re.findall(r'"([^"]*)"', line))
        blockquote = line.lstrip().startswith(">")
        if not (quoted or blockquote or in_first_column(line, snippet)
                or in_ban_table(src, lineno)):
            voice.append((lineno, f))
    print(f"{path}: {len(fails)} hits, {len(fails) - len(voice)} in specimen "
          f"zones, {len(voice)} in the instructional voice")
    if voice:
        for ln, f in voice:
            print(f"VOICE {f}")
            if ln:
                print(f"    {src[ln - 1][:170]}")
        return False
    sha = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    print(f"PASS {CHECKER} {VERSION} file={path.name} sha={sha}")
    return True


def main(argv):
    sweep = Path(__file__).with_name("sweep.py")
    paths = [Path(a) for a in argv] or [Path(__file__).resolve().parents[1] / "SKILL.md"]
    ok = True
    for p in paths:
        ok = audit_file(p, sweep) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
