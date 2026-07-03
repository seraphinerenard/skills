#!/usr/bin/env python3
"""sweep.py v1 - house-style sweep for written deliverables.

Usage: python3 sweep.py FILE [FILE...]

Scans prose (markdown, text, and the visible text of HTML) for the banned
patterns catalogued in writing-instructions. Rule IDs match SKILL.md and
references/ai-tells.md. Fenced code blocks, inline code spans, <script> and
<style> bodies, and HTML tags are exempt.

D2 numberless intensifiers are flagged only on lines without a digit.
Escape marker near the line, any comment syntax: allow:<ID> <reason>
Proof line per clean file: PASS sweep v1 file=<name> sha=<8hex>
Exit 0 only when every file passes. A5 (rule of three) is not machine-checkable;
apply it manually.
"""
import hashlib
import re
import sys
from pathlib import Path

CHECKER, VERSION = "sweep", "v5"

# (rule id, compiled regex, description, digit_exempt)
P = []


def add(rule, pattern, desc, digit_exempt=False, flags=re.IGNORECASE):
    P.append((rule, re.compile(pattern, flags), desc, digit_exempt))


add("A1", r"\b(not just|isn'?t just|not merely|not simply|more than just|"
          r"isn'?t about|it'?s not about|it'?s about more|"
          r"the (real )?question is(n'?t)?|the real (story|issue|point)|"
          r"not only .{1,60} but (also )?)\b", "contrast framing")
add("A1", r"\b(rather than|instead of|as opposed to)\b",
    "contrastive definition: state what it IS and cut the shadow alternative")
add("A1", r",\s+not\s+\w+", "appositive contrast ', not X'")
add("A9", r"\b(That( i|')s why|This is why|Which is why|That is the reason|"
          r"This is the reason)\b",
    "causal capstone: earn the chain with because/so, delete the announcement")
add("B9", r"\b(makes? sure|ensur(e|es|ing)( that)?|guarantee(s|d)?)\b",
    "assurance voice: state what happens and the mechanism")
add("B10", r"(?:^|[:;]\s+|,\s+and\s+)(?:each|every)\s+\w+\s+with(?:out)?\s+"
           r"(?:its|their|a|an|one)\b",
    "verbless catalogue cadence: restore the verb (write 'every rule HAS its gate')")
add("B10", r"\b(?:each|every)\s+\w+,\s+\w+(?:ed|en)\b[.;]",
    "verbless catalogue cadence: 'Every X, verbed.' gets its verb back")
add("B10", r"\bNo\s+\w+\.\s+No\s+\w+\.",
    "trailer anaphora: 'No X. No Y.' becomes one sentence with a verb")
add("A11", r"\b(One|Two|Three|Four|Five|Six|Seven)\s+\w+\s+"
           r"(crossed|collided|converged|aligned|broke|shifted|arrived|"
           r"ended together|changed everything)\b",
    "withheld-referent opener: name the things you count, in this sentence",
    flags=0)
add("B11", r"\b(funds the rest|pays the bill|foots the bill|does the rest|"
           r"does the heavy lifting|carries the day|moves the needle|"
           r"tells the story|drives the (result|results|outcome)|"
           r"closes the loop|seals the deal|wins the day|makes the difference|"
           r"owns the (outcome|result)|sets the (bill|pace)|sells the idea|"
           r"pays for itself|does the talking)\b",
    "punch-idiom clause tail: end on the fact, with its number")
add("B12", r"^\s*(?:#{1,6}\s+)?[A-Z][\w']{1,20},\s+\w+(?:ed|en)[.!]?\s*$",
    "aphorism title: cadence with no proposition; write what the thing says")
add("C1", r"\bnamed owners?\b|\b(key|main|value|growth|core)\s+drivers?\b|"
          r"\bdrivers?\s+of\s+(growth|value|change|success|performance)\b",
    "process jargon or driver-as-buzzword in deliverable prose")
add("C1", r"\bship(s|ped|ping)?\b",
    "software-jargon 'ship': write deliver, release, send, or the dated event")
add("E1", r"^\s*\*\*[^*]{2,80}\*\*[.:]?\s+\S",
    "bold-lead paragraph: use a real heading or start the paragraph in regular type",
    flags=0)
add("E1", r"<p[^>]*>\s*<(b|strong)\b",
    "bold-lead paragraph in HTML: use a real heading or plain prose")
add("A2", r"(The (result|catch|problem|kicker|twist)\?|Here'?s the thing)",
    "manufactured pivot")
add("A6", r"\b(no (approach|solution|tool) is perfect|challenges remain|"
          r"it'?s a balance|pros and cons)\b", "both-sidesing")
add("A7", r"\b(pivotal|testament to|paradigm shift|marks a (new|significant)|"
          r"ever-?evolving|fast-?paced|sets the stage|watershed moment)\b",
    "significance inflation")
add("A8", r"\b(the future (belongs|looks|is bright)|in today'?s world|"
          r"in today'?s fast|only time will tell|one thing is certain)\b",
    "portentous closer or empty opener")
add("B2", r",\s+(highlighting|underscoring|showcasing|reflecting|emphasizing|"
          r"demonstrating|cementing|solidifying|signalling|signaling|"
          r"illustrating|reinforcing)\b", "trailing -ing analysis clause")
add("B3", r"\b(serves as|stands as|functions as|acts as a|boasts)\b",
    "copula avoidance")
add("B5", r"\b(could potentially|may possibly|might potentially|"
          r"it could be argued|arguably)\b", "hedging stack")
add("B6", r"\b(Crucially,|Importantly,|Notably,|Interestingly,|"
          r"It'?s worth noting|It is worth noting|Let'?s break)\b",
    "throat-clearing", flags=0)
add("C1", r"\b(delve|delving|leverag(e|es|ing)|utiliz\w+|facilitat\w+|"
          r"streamlin\w+|foster(s|ing)?|tapestry|unlock(s|ing)?|unleash\w*|"
          r"elevat(e|es|ing)|empower\w*|supercharge\w*|cutting-edge|"
          r"state-of-the-art|best-in-class|game-?chang\w+|transformative|"
          r"holistic|synerg\w+|actionable insight\w*|stakeholder\w*|"
          r"meticulous\w*|multifaceted|seamless\w*|robust\w*|vibrant)\b",
    "kill-list vocabulary")
add("C1", r"\b(navigate|navigating) the\b", "figurative navigate")
add("C1", r"\b(journey|landscape|ecosystem)\b(?! map)", "figurative noun",
    digit_exempt=False)
add("D1", r"\b(experts (say|argue|agree|believe)|observers (have )?not\w*|"
          r"industry reports?|studies (show|suggest|indicate)|"
          r"research (shows|suggests|indicates))\b", "vague authority")
add("D2", r"\b(significant(ly)?|substantial(ly)?|notabl[ey]|vast majority|"
          r"dramatic(ally)?|massive(ly)?|huge(ly)?)\b",
    "numberless intensifier", digit_exempt=True)
add("F3", r"\b(In conclusion|In summary, we|Ultimately,|"
          r"(this|the) (document|report|memo) will (explore|examine)|"
          r"we will explore)\b", "essay shell")
add("CAN", r"\b(color(s|ed|ful)?|behavior(s|al)?|favor(s|ed|ite|ites)?|"
           r"honor(s|ed)?|labor(s|ed)?|neighbor(s|hood|hoods)?|"
           r"center(s|ed|ing)?|meter(s)?|fiber(s)?|theater(s)?|liter(s)?|"
           r"organis(e|es|ed|ing|ation\w*)|recognis\w+|analys(e|es|ed|ing)|"
           r"optimis(e|es|ed|ing|ation\w*)|"
           r"traveled|labeled|modeling|canceled|signaling|"
           r"defense|offense|gray|catalog(s|ed|ing)?|tyre(s)?|kerb(s)?|"
           r"aluminium|favorite(s)?|checkbook)\b", "non-Canadian spelling")

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")
ALLOW = re.compile(r"allow:([A-Z]+\d*)\s+(.{3,})")
HEADING = re.compile(r"^(#{1,6})\s+(.*)")


def visible_lines(path: Path):
    """Yield (lineno, prose_text) with code and markup removed, lines kept."""
    text = path.read_text(encoding="utf-8", errors="replace")
    is_html = path.suffix.lower() in (".html", ".htm", ".svg")
    lines = text.splitlines()
    in_fence = in_script = in_style = False
    for i, ln in enumerate(lines, 1):
        raw = ln
        if not is_html:
            if ln.strip().startswith("```"):
                in_fence = not in_fence
                yield i, "", raw
                continue
            if in_fence:
                yield i, "", raw
                continue
            prose = re.sub(r"`[^`]*`", "", ln)
            yield i, prose, raw
        else:
            s = ln
            low = s.lower()
            if "<script" in low:
                in_script = True
            if "<style" in low:
                in_style = True
            drop = in_script or in_style
            if "</script>" in low:
                in_script = False
            if "</style>" in low:
                in_style = False
            if drop:
                yield i, "", raw
                continue
            prose = re.sub(r"<[^>]*>", " ", s)
            yield i, prose, raw


def check_file(path: Path) -> bool:
    rows = list(visible_lines(path))
    allows, fails = [], []
    allow_map = []
    for i, _, raw in rows:
        for m in ALLOW.finditer(raw):
            allow_map.append((m.group(1), i))
            allows.append(f"ALLOW {m.group(1)} {path}:{i} {m.group(2).strip()}")

    def allowed(rule, lineno):
        return any(r == rule and abs(l - lineno) <= 2 for r, l in allow_map)

    for i, prose, raw in rows:
        if not prose.strip():
            continue
        has_digit = any(c.isdigit() for c in prose)
        for rule, rx, desc, digit_exempt in P:
            if digit_exempt and has_digit:
                continue
            if allowed(rule, i):
                continue
            seen = set()
            for m in rx.finditer(prose):
                hit = m.group(0)
                if hit.lower() in seen:
                    continue
                seen.add(hit.lower())
                fails.append(f"FAIL {rule} {path}:{i} {desc}: {hit!r}")
        if ("—" in prose or "–" in prose) and not allowed("E4", i):
            fails.append(f"FAIL E4 {path}:{i} em/en dash in copy")
        if EMOJI.search(prose) and not allowed("E5", i):
            fails.append(f"FAIL E5 {path}:{i} emoji")
        h = HEADING.match(prose) if not path.suffix.lower().startswith(".ht") else None
        if h:
            body = h.group(2).strip()
            if ":" in body and not allowed("E3", i):
                fails.append(f"FAIL E3 {path}:{i} colon in heading: {body!r}")
            words = [w for w in body.split() if w.isalpha() and len(w) >= 4]
            if (len(body.split()) >= 3 and len(words) >= 2
                    and all(w[0].isupper() for w in words)
                    and not allowed("E2", i)):
                fails.append(f"FAIL E2 {path}:{i} title-case heading: {body!r}")

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
