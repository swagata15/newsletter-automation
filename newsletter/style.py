"""Keep the writing from reading like AI slop.

1. `remove_dashes` deterministically strips em dashes, en dashes and double
   hyphens from prose (code blocks, inline code and URLs are left alone).
2. `find_slop` flags stock AI phrases so the pipeline can ask Claude to rewrite
   those sentences.
"""

from __future__ import annotations

import re

_PROTECTED = re.compile(r"(`[^`\n]*`|\]\([^)\s]*(?:\s+\"[^\"]*\")?\)|https?://\S+|\[\[VISUAL:[^\]]+\]\])")
_HR = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")


def _fix_prose(text: str, line_start: bool = True) -> str:
    text = re.sub(r"(?<=\d)\s*[–—]\s*(?=\d)", "-", text)       # 2020–2024 -> 2020-2024
    if line_start:  # a dash opening a line (e.g. an attribution) is simply dropped
        text = re.sub(r"^\s*[—–]\s*", "", text)
    text = re.sub(r"\s*(?:[—–―‒]|(?<![-!<])--+(?![->]))\s*", ", ", text)
    text = re.sub(r",\s*([,.;:!?)])", r"\1", text)                       # tidy ", ." etc.
    text = re.sub(r"\(\s*,\s*", "(", text)
    if line_start:  # only a comma at the very start of a line is an artifact; after a link it is real
        text = re.sub(r"^,\s*", "", text)
    return text


def remove_dashes(markdown: str) -> str:
    out, in_code = [], False
    for line in markdown.split("\n"):
        if _FENCE.match(line):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or _HR.match(line):
            out.append(line)
            continue
        # keep list markers ("- item") intact, fix the rest
        m = re.match(r"^(\s*(?:[-*+]|\d+\.)\s+)?(.*)$", line)
        prefix, body = m.group(1) or "", m.group(2)
        parts = _PROTECTED.split(body)
        body = "".join(p if i % 2 else _fix_prose(p, line_start=(i == 0)) for i, p in enumerate(parts))
        out.append(prefix + body)
    return "\n".join(out)


SLOP_PATTERNS = [
    r"\bdelv(e|es|ing)\b", r"\btapestry\b", r"\btestament to\b", r"\bever[- ]evolving\b",
    r"\bfast[- ]paced\b", r"\bgame[- ]?changer\b", r"\brevolutioni[sz]", r"\bunleash", r"\bunlock(s|ing)? the\b",
    r"\bharness(ing)? the power\b", r"\bin today'?s\b", r"\bnavigat(e|ing) the\b", r"\blandscape\b",
    r"\brealm\b", r"\bseamless(ly)?\b", r"\bcutting[- ]edge\b", r"\bparadigm shift\b", r"\blet'?s dive\b",
    r"\bdive (in|into)\b", r"\bbuckle up\b", r"\bin conclusion\b", r"\bit'?s (important|worth) (to note|noting)\b",
    r"\bit is (important|worth) (to note|noting)\b", r"\bat the end of the day\b", r"\bnot (just|only|merely) [^.\n]{1,60}?,? but\b",
    r"\b(it'?s|this is|isn'?t) not just\b", r"\bisn'?t just\b", r"\bsupercharg", r"\bpivotal\b", r"\bembark",
    r"\ba myriad of\b", r"\bmoreover\b", r"\bfurthermore\b", r"\bplays? a (crucial|vital|key) role\b",
    r"\bin the world of\b", r"\bdeep dive\b", r"\bunderscore(s|d)?\b", r"\bresonate", r"\bmeticulous",
    r"\bboast(s|ing)?\b", r"\belevate", r"\bstands? as\b", r"\bgroundbreaking\b",
]
_SLOP = [re.compile(p, re.IGNORECASE) for p in SLOP_PATTERNS]


def _prose_only(markdown: str) -> str:
    keep, in_code = [], False
    for line in markdown.split("\n"):
        if _FENCE.match(line):
            in_code = not in_code
            continue
        if not in_code:
            keep.append(re.sub(r"`[^`]*`|\]\([^)]*\)", "", line))
    return "\n".join(keep)


def find_slop(markdown: str) -> list[str]:
    """Return the distinct stock phrases found in prose (not code)."""
    prose = _prose_only(markdown)
    found = []
    for rx in _SLOP:
        for m in rx.finditer(prose):
            phrase = m.group(0)
            if phrase.lower() not in (f.lower() for f in found):
                found.append(phrase)
    return found


STYLE_GUIDE = """Writing style (non-negotiable, the reader must never think "an AI wrote this"):
- NEVER use em dashes (—), en dashes (–) or double hyphens (--) in prose. Use commas, periods, colons or parentheses instead. Hyphens inside compound words are fine.
- Never use these words or patterns: delve, tapestry, testament, ever-evolving, fast-paced, game-changer, revolutionize, unleash, unlock, harness the power, in today's world, navigate the, landscape, realm, seamless, cutting-edge, paradigm shift, let's dive in, deep dive, buckle up, in conclusion, it's important to note, at the end of the day, moreover, furthermore, pivotal, embark, myriad, underscore, resonate, meticulous, boast, elevate, groundbreaking, "plays a crucial role", and the "it's not just X, it's Y" / "not only X but Y" construction.
- No emoji. No rhetorical-question headlines stacked in a row. No "Here's the thing:" style throat clearing.
- Vary sentence length. Short sentences are good. Lead with the concrete fact, number or example, then the point.
- Write like a smart friend explaining something over coffee: specific, a bit opinionated, never breathless.
- Don't summarise what you just said at the end of each section."""
