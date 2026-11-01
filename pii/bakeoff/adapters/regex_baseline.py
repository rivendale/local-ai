"""Regex baseline, written for this bake-off. Standard library only.

Detection runs on a canonical copy of the text: look-alike dashes become
``-``, look-alike spaces become a space, full-width digits become ASCII
digits, and zero-width, soft-hyphen and bidi control characters are dropped. Offsets are
mapped back to the caller's text, so a span covers any hidden characters
inside it. This follows the fix described in pw-redact-core's CHANGELOG
(Unreleased, 2026-09-21).

Checksums: cards must pass Luhn, routing numbers the ABA check. Routing,
account, birth-date and SSN-without-dashes patterns need a context word.

Names are found only after an honorific or in a ``Name:`` field. This baseline
does no general name recognition, on purpose: it shows what patterns alone
catch. It was written by the same author as the generator, so its scores on
this dataset are optimistic.
"""

from __future__ import annotations

import re

DASHES = frozenset("\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe58\ufe63\uff0d")
SPACES = frozenset("\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u202f\u205f\u3000")
INVISIBLE = frozenset("\u00ad\u200b\u200c\u200d\u200e\u200f\u2060\u2061\u2062\u2063\u2064\ufeff\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")


def canonicalize(text: str) -> tuple[str, list[int]]:
    """Return canonical text and, for each canonical char, its offset in ``text``."""
    out: list[str] = []
    index: list[int] = []
    for i, ch in enumerate(text):
        if ch in INVISIBLE:
            continue
        if ch in DASHES:
            ch = "-"
        elif ch in SPACES:
            ch = " "
        elif "\uff10" <= ch <= "\uff19":
            ch = chr(ord(ch) - 0xFF10 + ord("0"))
        out.append(ch)
        index.append(i)
    return "".join(out), index


def luhn_ok(digits: str) -> bool:
    total = 0
    for i, c in enumerate(reversed(digits)):
        d = int(c)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def aba_ok(digits: str) -> bool:
    d = [int(c) for c in digits]
    return len(d) == 9 and (3 * (d[0] + d[3] + d[6]) + 7 * (d[1] + d[4] + d[7]) + d[2] + d[5] + d[8]) % 10 == 0


_DATE = r"(?:\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})"
_SUFFIX = r"(?:St|Street|Ave|Avenue|Ln|Lane|Rd|Road|Dr|Drive|Ct|Court|Way|Blvd)"

# (type, compiled pattern, group to keep, validator)
PATTERNS = [
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), 0, None),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), 0, None),
    ("SSN", re.compile(r"\b\d{3} \d{2} \d{4}\b"), 0, None),
    ("SSN", re.compile(r"(?i)\b(?:ssn|social security(?: no\.?| number)?)[:#\s]*(\d{9})\b"), 1, None),
    ("EIN", re.compile(r"\b\d{2}-\d{7}\b"), 0, None),
    ("CARD", re.compile(r"\b\d(?:[ -]?\d){12,18}\b"), 0, lambda s: 13 <= len(re.sub(r"\D", "", s)) <= 19 and luhn_ok(re.sub(r"\D", "", s))),
    ("PHONE", re.compile(r"(?:\+1[ .-]?)?(?:\(\d{3}\) ?|\b\d{3}[ .-])\d{3}[ .-]\d{4}\b"), 0, None),
    ("ROUTING", re.compile(r"(?i)\b(?:routing|aba|rtn)(?: number| no\.?| #)?[:#\s]*(\d{9})\b"), 1, aba_ok),
    ("ACCOUNT", re.compile(r"(?i)\b(?:acct|account)(?: number| no\.?)?[:#\s]*([A-Z]?\d[\d-]{5,18}\d)\b"), 1, None),
    ("DOB", re.compile(r"(?i)\b(?:dob|date of birth|born(?: on)?|birth ?date)[:\s]*(" + _DATE + ")"), 1, None),
    ("ADDRESS", re.compile(r"\b\d{1,5} (?:[A-Z][a-z]+ ){1,3}" + _SUFFIX + r"\b(?:, Apt \d+)?(?:, [A-Z][a-z]+(?: [A-Z][a-z]+)?, [A-Z]{2} \d{5})?"), 0, None),
    ("PERSON", re.compile(r"\b(?:Mr|Ms|Mrs|Mx|Dr)\. ([A-Z][a-z]+(?: [A-Z][a-z]+)?)"), 1, None),
    ("PERSON", re.compile(r"(?m)^Name: ([^\n]+)$"), 1, None),
]


class RegexBaseline:
    name = "regex"

    def info(self) -> dict:
        return {"adapter": self.name, "version": "1", "dependencies": "Python standard library only"}

    def predict(self, text: str) -> list[dict]:
        canon, index = canonicalize(text)
        found = []
        for etype, pat, group, check in PATTERNS:
            for m in pat.finditer(canon):
                s, e = m.span(group)
                if e <= s or (check and not check(m.group(group))):
                    continue
                found.append({"start": index[s], "end": index[e - 1] + 1, "type": etype, "score": 1.0})
        return found


def load(**_options) -> RegexBaseline:
    return RegexBaseline()
