#!/usr/bin/env python3
"""check_contrast.py v1 - WCAG 2.1 contrast validator for brand-kit pairs.

Usage: python3 check_contrast.py FG BG [FG BG ...]

Arguments are hex pairs, foreground then background, with or without '#'.
One line per pair:
  PAIR #fg on #bg ratio=N.NN AA-body=PASS/FAIL AA-large=PASS/FAIL
AA-body passes at 4.5:1; AA-large at 3:1. Video text pairs must show a ratio
of 7.00 or higher (rule BK3; read the printed ratio). Any AA-body failure
prints a FAIL BK3 line and the script exits 1.
Proof line on success: PASS check_contrast v1 pairs=N sha=<8hex>
"""
import hashlib
import sys

CHECKER, VERSION = "check_contrast", "v1"


def luminance(hexstr: str) -> float:
    h = hexstr.lstrip("#").strip()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6 or any(c not in "0123456789abcdefABCDEF" for c in h):
        raise ValueError(f"bad hex {hexstr!r}")

    def chan(v: int) -> float:
        c = v / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (chan(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def main(argv):
    if not argv or len(argv) % 2 != 0:
        print(__doc__)
        return 2
    ok = True
    for i in range(0, len(argv), 2):
        fg, bg = argv[i], argv[i + 1]
        try:
            l1, l2 = luminance(fg), luminance(bg)
        except ValueError as e:
            print(f"FAIL BK3 pair {i // 2 + 1}: {e}")
            ok = False
            continue
        hi, lo = max(l1, l2), min(l1, l2)
        ratio = (hi + 0.05) / (lo + 0.05)
        body = "PASS" if ratio >= 4.5 else "FAIL"
        large = "PASS" if ratio >= 3.0 else "FAIL"
        f = fg if fg.startswith("#") else "#" + fg
        b = bg if bg.startswith("#") else "#" + bg
        print(f"PAIR {f} on {b} ratio={ratio:.2f} AA-body={body} AA-large={large}")
        if body == "FAIL":
            print(f"FAIL BK3 pair {f} on {b} ratio {ratio:.2f} under 4.5")
            ok = False
    if not ok:
        return 1
    sha = hashlib.sha256(" ".join(argv).encode()).hexdigest()[:8]
    print(f"PASS {CHECKER} {VERSION} pairs={len(argv) // 2} sha={sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
