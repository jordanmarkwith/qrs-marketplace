#!/usr/bin/env python3
"""
extract_figures.py  --  pull every checkable claim out of a document.

Optional helper for the `grounded` skill. The skill is prompt-driven; this script
just improves *recall* so no figure slips through. It does NOT judge whether a
figure is sourced or correct -- it only finds candidates and the sentence each one
sits in. Classification (sourced / unsourced / illustrative / internally-derived)
is the skill's job.

Catches: currency ($1.2M, USD 4 billion), percentages (37%, 3x), plain
counts/large numbers, years and dates, and superlative / uniqueness claims
("largest", "first", "only", "#1", "world-leading", "fastest", "best-in-class").

Usage:
  python extract_figures.py --file report.md
  python extract_figures.py --file report.txt --json
  cat report.txt | python extract_figures.py

Dependencies: none (standard library).
"""

import argparse
import json
import re
import sys

SUPERLATIVES = [
    r"largest", r"smallest", r"biggest", r"first", r"only", r"best(?:-in-class)?",
    r"leading", r"world-?class", r"world-?leading", r"fastest", r"slowest",
    r"highest", r"lowest", r"most\b", r"#\s?1\b", r"number one", r"unprecedented",
    r"unique", r"never before", r"industry-?leading", r"state-of-the-art",
    r"cutting-?edge", r"revolutionary", r"guaranteed", r"proven", r"validated",
    r"certified",
]

PATTERNS = [
    ("currency", re.compile(
        r"(?:USD|US\$|\$|€|£)\s?\d[\d,]*(?:\.\d+)?\s?"
        r"(?:k|m|bn|tn|thousand|million|billion|trillion)?", re.I)),
    ("percentage", re.compile(r"\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s?percent\b", re.I)),
    ("multiplier", re.compile(r"\b\d+(?:\.\d+)?\s?x\b", re.I)),
    ("date", re.compile(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s?\d{0,4}"
        r"|\b(?:19|20)\d{2}\b", re.I)),
    ("count", re.compile(r"(?<![\w$€£%])\d[\d,]*(?:\.\d+)?(?![\w%])")),
    ("superlative", re.compile(r"\b(?:" + "|".join(SUPERLATIVES) + r")\b", re.I)),
]


def split_sentences(text):
    # lightweight sentence splitter; keeps offsets approximate but readable
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def extract(text):
    found = []
    seen = set()
    for sent in split_sentences(text):
        for kind, pat in PATTERNS:
            for m in pat.finditer(sent):
                token = m.group(0).strip()
                if not token:
                    continue
                key = (kind, token, sent[:60])
                if key in seen:
                    continue
                seen.add(key)
                found.append({"type": kind, "text": token, "sentence": sent})
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=None, help="path to text/markdown file")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    text = open(args.file, encoding="utf-8", errors="replace").read() \
        if args.file else sys.stdin.read()

    items = extract(text)
    if args.json:
        print(json.dumps(items, indent=2, ensure_ascii=False))
        return
    if not items:
        print("No figures or superlatives detected.")
        return
    print(f"{len(items)} candidate claim(s) found "
          "(classify each as sourced / unsourced / illustrative / internally-derived):\n")
    width = max(len(i["type"]) for i in items)
    for i, it in enumerate(items, 1):
        s = it["sentence"]
        s = (s[:96] + "…") if len(s) > 97 else s
        print(f"{i:>3}. [{it['type']:<{width}}] {it['text']}")
        print(f"     ↳ {s}")


if __name__ == "__main__":
    main()
