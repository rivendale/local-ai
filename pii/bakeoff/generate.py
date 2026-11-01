#!/usr/bin/env python3
"""Seeded generator for the synthetic financial-services PII dataset.

Standard library only. Every value is synthetic:

- Social Security numbers use area numbers 900-999 with group numbers 01-49.
  The SSA does not issue SSNs with a 9xx area, and those group numbers are
  outside the ITIN ranges, so no value can be a real SSN or ITIN.
- Card numbers come from the public test numbers that card processors publish
  for sandbox use; they are Luhn-valid and carry no account.
- Phone numbers use the 555-0100 to 555-0199 block set aside for fiction.
- Emails use the example.com, example.org and example.net domains (RFC 2606).
- Names, streets, account, routing and EIN values are random combinations.

Output is JSON Lines with ASCII escapes, so the committed file contains no raw
zero-width, bidi or look-alike characters. Offsets are Python string indices
into the decoded text.

Determinism: the only source of randomness is ``random.Random(seed).random()``,
which Python guarantees to reproduce across versions for the same seed. The
choice, integer and shuffle helpers below are built on it instead of on
``randrange`` or ``choice``, whose algorithms are not guaranteed.

    python generate.py                  # write data/synthetic_v1.jsonl
    python generate.py --check          # regenerate and compare with the file
    python generate.py --out other.jsonl --docs 50 --seed 7
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "data" / "synthetic_v1.jsonl"
DEFAULT_SEED = 20261101
DEFAULT_DOCS = 420
DATASET_VERSION = "synthetic_v1"

# Gold entity types (personal information to redact).
GOLD_TYPES = (
    "PERSON", "SSN", "EIN", "ACCOUNT", "ROUTING", "CARD",
    "PHONE", "EMAIL", "ADDRESS", "DOB",
)
# Decoy kinds: text that looks like PII to a pattern but is not personal.
DECOY_KINDS = ("CUSIP", "FORM", "PERCENT", "AMOUNT", "DATE", "YEAR", "FIN_TERM")

# Look-alike characters, written as escapes on purpose.
LOOKALIKE_DASHES = ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015", "\u2212")
LOOKALIKE_SPACES = ("\u00a0", "\u202f", "\u2009")
EN_DASH = "\u2013"
ZERO_WIDTH = ("\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u00ad")

FIRST_NAMES = (
    "Avery", "Blake", "Casey", "Dana", "Elliot", "Frances", "Gale", "Harper",
    "Indira", "Jordan", "Kendall", "Lena", "Morgan", "Noor", "Oren", "Priya",
    "Quinn", "Rosa", "Soren", "Talia", "Umar", "Vera", "Wes", "Ximena",
    "Yusuf", "Zara", "Marisol", "Tobias", "Keiko", "Anders", "Bea", "Desmond",
    "Ingrid", "Luca", "Mireille", "Nikhil", "Odette", "Ravi", "Sanne", "Tomasz",
)
LAST_NAMES = (
    "Abernathy", "Brightwater", "Castellano", "Delacroix", "Eastwood",
    "Fairbanks", "Galloway", "Hollis", "Ibarra", "Jansen", "Kowalczyk",
    "Lindqvist", "Marchetti", "Nakamura", "Okonkwo", "Pemberton", "Quintero",
    "Rasmussen", "Szabo", "Thornbury", "Underhill", "Vasquez", "Whitlock",
    "Yamada", "Zielinski", "Achterberg", "Bianchi", "Draper", "Esposito",
    "Haddad",
)
# Surnames and given names that are also finance words.
FIN_TERM_SURNAMES = ("Roth", "Price", "Bond", "Rich", "Cash", "Banks", "Sterling", "Gold")
FIN_TERM_GIVEN = ("Penny", "Rich", "Sterling", "Bond", "Cash")
# Finance phrases that reuse those words and must not be redacted.
FIN_TERMS = (
    "Roth IRA", "Roth conversion", "backdoor Roth", "bond ladder",
    "Treasury bond", "price target", "strike price", "cash sweep",
    "cash equivalents", "rich valuation", "gold ETF", "sterling exposure",
    "money market", "Banks sector",
)
HONORIFICS = ("Mr.", "Ms.", "Mx.", "Dr.")
STREETS = (
    "Maple", "Cedar", "Willow", "Harbor", "Orchard", "Quarry", "Juniper",
    "Larkspur", "Millbrook", "Sycamore", "Kestrel", "Foxglove",
)
STREET_SUFFIX = ("St", "Street", "Ave", "Avenue", "Ln", "Lane", "Rd", "Road", "Dr", "Ct", "Way", "Blvd")
CITIES = (
    ("Springfield", "IL"), ("Riverton", "WY"), ("Fairview", "OR"),
    ("Greenville", "SC"), ("Franklin", "TN"), ("Madison", "WI"),
    ("Salem", "MA"), ("Oakdale", "MN"), ("Georgetown", "TX"), ("Clinton", "IA"),
)
MONTHS = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)
# Public sandbox card numbers published by card processors for testing.
TEST_CARDS = (
    "4111111111111111", "4012888888881881", "4242424242424242",
    "5555555555554444", "5105105105105100", "2223003122003222",
    "378282246310005", "371449635398431", "6011111111111117",
    "6011000990139424", "3566002020360505",
)
# EIN prefixes the generator treats as unassigned. The IRS publishes the
# assigned list; this set was not checked against it. [unverified]
EIN_PREFIXES = ("07", "08", "09", "17", "18", "19", "28", "29", "49", "69", "70", "78", "79", "89")
FORMS = (
    "Form 1040", "Form 8949", "Schedule D", "Form 1099-B", "1099-DIV",
    "Form 5498", "W-2", "Form 4868", "Form 8606", "Schedule K-1",
)


class Rng:
    """Helpers built only on ``random.random()``, which is stable across Pythons."""

    def __init__(self, seed: int) -> None:
        self._r = random.Random(seed)

    def random(self) -> float:
        return self._r.random()

    def below(self, n: int) -> int:
        return min(int(self._r.random() * n), n - 1)

    def between(self, lo: int, hi: int) -> int:
        """Integer in [lo, hi]."""
        return lo + self.below(hi - lo + 1)

    def pick(self, seq):
        return seq[self.below(len(seq))]

    def chance(self, p: float) -> bool:
        return self._r.random() < p

    def digits(self, n: int) -> str:
        return "".join(str(self.below(10)) for _ in range(n))


# ---------------------------------------------------------------- checksums


def luhn_ok(number: str) -> bool:
    digits = [int(c) for c in number if c.isdigit()]
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def aba_ok(number: str) -> bool:
    d = [int(c) for c in number]
    if len(d) != 9:
        return False
    s = 3 * (d[0] + d[3] + d[6]) + 7 * (d[1] + d[4] + d[7]) + (d[2] + d[5] + d[8])
    return s % 10 == 0


def cusip_check_digit(base8: str) -> str:
    total = 0
    for i, c in enumerate(base8):
        if c.isdigit():
            v = int(c)
        else:
            v = ord(c) - ord("A") + 10
        if i % 2 == 1:
            v *= 2
        total += v // 10 + v % 10
    return str((10 - total % 10) % 10)


# ------------------------------------------------------------- value makers


def make_ssn(rng: Rng) -> str:
    return f"{rng.between(900, 999)}-{rng.between(1, 49):02d}-{rng.between(1, 9999):04d}"


def make_ein(rng: Rng) -> str:
    return f"{rng.pick(EIN_PREFIXES)}-{rng.digits(7)}"


def make_routing(rng: Rng) -> str:
    head = f"{rng.between(1, 12):02d}" + rng.digits(6)
    for last in range(10):
        if aba_ok(head + str(last)):
            return head + str(last)
    raise AssertionError("unreachable: one check digit always fits")


def make_account(rng: Rng) -> str:
    style = rng.below(3)
    if style == 0:
        return rng.digits(rng.between(8, 12))
    if style == 1:
        return f"{rng.pick('XZQ')}{rng.digits(2)}-{rng.digits(6)}"
    return f"{rng.digits(4)}-{rng.digits(4)}-{rng.digits(2)}"


def group_card(number: str, sep: str) -> str:
    if len(number) == 15:
        parts = [number[:4], number[4:10], number[10:]]
    else:
        parts = [number[i:i + 4] for i in range(0, len(number), 4)]
    return sep.join(parts)


def make_card(rng: Rng) -> str:
    return group_card(rng.pick(TEST_CARDS), rng.pick((" ", "-", "")))


def make_phone(rng: Rng) -> str:
    area = rng.between(201, 989)
    line = f"01{rng.digits(2)}"
    style = rng.below(4)
    if style == 0:
        return f"({area}) 555-{line}"
    if style == 1:
        return f"{area}-555-{line}"
    if style == 2:
        return f"{area}.555.{line}"
    return f"+1 {area} 555 {line}"


def make_date(rng: Rng, lo_year: int, hi_year: int) -> str:
    y, m, d = rng.between(lo_year, hi_year), rng.between(1, 12), rng.between(1, 28)
    style = rng.below(3)
    if style == 0:
        return f"{m:02d}/{d:02d}/{y}"
    if style == 1:
        return f"{y}-{m:02d}-{d:02d}"
    return f"{MONTHS[m - 1]} {d}, {y}"


def make_address(rng: Rng, with_city: bool = True) -> str:
    street = f"{rng.between(10, 9899)} {rng.pick(STREETS)} {rng.pick(STREET_SUFFIX)}"
    if rng.chance(0.2):
        street += f", Apt {rng.between(1, 40)}"
    if not with_city:
        return street
    city, state = rng.pick(CITIES)
    return f"{street}, {city}, {state} {rng.digits(5)}"


def make_cusip(rng: Rng) -> str:
    alnum = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    if rng.chance(0.5):
        base = rng.digits(8)  # all-digit CUSIPs look like SSNs or routing numbers
    else:
        base = rng.digits(3) + "".join(rng.pick(alnum) for _ in range(3)) + rng.pick(alnum) + rng.digits(1)
    return base + cusip_check_digit(base)


def make_amount(rng: Rng) -> str:
    style = rng.below(4)
    if style == 0:
        return f"${rng.between(1, 999)},{rng.between(0, 999):03d}"
    if style == 1:
        return f"${rng.between(1, 9)},{rng.between(0, 999):03d},{rng.between(0, 999):03d}"
    if style == 2:
        return f"${rng.between(1, 999)},{rng.between(0, 999):03d}.{rng.between(0, 99):02d}"
    return f"${rng.between(5, 500)}k"


def make_percent(rng: Rng) -> str:
    if rng.chance(0.5):
        return f"{rng.pick((10, 12, 22, 24, 32, 35, 37))}%"
    return f"{rng.between(0, 9)}.{rng.between(0, 99):02d}%"


# ----------------------------------------------------------- hard variants


def to_fullwidth(s: str) -> str:
    return "".join(chr(0xFF10 + int(c)) if c.isdigit() else c for c in s)


def harden(rng: Rng, value: str) -> tuple[str, list[str]]:
    """Apply one hard-case transform to a number-like value."""
    options = []
    if "-" in value:
        options.append("lookalike_dash")
    if " " in value:
        options.append("lookalike_space")
    options += ["zero_width", "fullwidth"]
    kind = rng.pick(options)
    if kind == "lookalike_dash":
        dash = rng.pick(LOOKALIKE_DASHES)
        return value.replace("-", dash), [kind]
    if kind == "lookalike_space":
        space = rng.pick(LOOKALIKE_SPACES)
        return value.replace(" ", space), [kind]
    if kind == "fullwidth":
        return to_fullwidth(value), [kind]
    inner = [i for i in range(1, len(value)) if value[i - 1].isalnum() or value[i].isalnum()]
    pos = rng.pick(inner)
    return value[:pos] + rng.pick(ZERO_WIDTH) + value[pos:], [kind]


# ------------------------------------------------------------ doc builder


class Doc:
    def __init__(self, doc_id: str, template: str) -> None:
        self.id = doc_id
        self.template = template
        self.parts: list[str] = []
        self.length = 0
        self.spans: list[dict] = []
        self.decoys: list[dict] = []
        self.tags: set[str] = set()

    def text(self, s: str) -> None:
        self.parts.append(s)
        self.length += len(s)

    def gold(self, s: str, etype: str, tags=()) -> None:
        assert etype in GOLD_TYPES, etype
        self.spans.append({"start": self.length, "end": self.length + len(s), "type": etype, "tags": sorted(tags)})
        self.tags.update(tags)
        self.text(s)

    def decoy(self, s: str, kind: str, tags=()) -> None:
        assert kind in DECOY_KINDS, kind
        self.decoys.append({"start": self.length, "end": self.length + len(s), "kind": kind, "tags": sorted(tags)})
        self.tags.update(tags)
        self.text(s)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "template": self.template,
            "text": "".join(self.parts),
            "spans": self.spans,
            "decoys": self.decoys,
            "tags": sorted(self.tags),
        }


class Person:
    def __init__(self, rng: Rng, fin_term: bool = False) -> None:
        self.first = rng.pick(FIN_TERM_GIVEN if fin_term and rng.chance(0.3) else FIRST_NAMES)
        self.last = rng.pick(FIN_TERM_SURNAMES if fin_term else LAST_NAMES)
        self.initial = rng.pick("ABCDEFGHJKLMNPRSTW")
        self.fin_term = fin_term

    def tags(self) -> list[str]:
        return ["fin_term_name"] if self.fin_term else []


class Writer:
    """Fills one document. Each method writes text and records spans."""

    def __init__(self, rng: Rng, doc: Doc, hard_rate: float) -> None:
        self.rng = rng
        self.doc = doc
        self.hard_rate = hard_rate

    def number(self, value: str, etype: str, extra_tags=()) -> None:
        tags = list(extra_tags)
        if self.rng.chance(self.hard_rate):
            value, more = harden(self.rng, value)
            tags += more
        self.doc.gold(value, etype, tags)

    def name(self, p: Person, style: str | None = None) -> None:
        style = style or self.rng.pick(("full", "full", "full", "middle", "inverted", "title", "upper"))
        tags = p.tags()
        if style == "title":
            self.doc.text(self.rng.pick(HONORIFICS) + " ")
            self.doc.gold(p.last, "PERSON", tags + ["title_name"])
            return
        if style == "first":
            self.doc.gold(p.first, "PERSON", tags + ["first_name_only"])
            return
        if style == "lower":
            self.doc.gold(f"{p.first} {p.last}".lower(), "PERSON", tags + ["lowercase_name"])
            return
        text = {
            "full": f"{p.first} {p.last}",
            "middle": f"{p.first} {p.initial}. {p.last}",
            "inverted": f"{p.last}, {p.first}",
            "upper": f"{p.first} {p.last}".upper(),
        }[style]
        self.doc.gold(text, "PERSON", tags + (["uppercase_name"] if style == "upper" else []))

    def email(self, p: Person | None) -> None:
        domain = self.rng.pick(("example.com", "example.org", "example.net"))
        if p is not None:
            local = self.rng.pick((f"{p.first}.{p.last}", f"{p.first[0]}{p.last}", f"{p.last}{self.rng.digits(2)}")).lower()
            tags = ["name_in_email"]
        else:
            local = self.rng.pick(("client.services", "ops", "statements")) + self.rng.digits(2)
            tags = []
        value = f"{local}@{domain}"
        if self.rng.chance(self.hard_rate / 2):
            pos = len(local)
            value = value[:pos] + self.rng.pick(ZERO_WIDTH) + value[pos:]
            tags.append("zero_width")
        self.doc.gold(value, "EMAIL", tags)

    def dob(self) -> None:
        self.doc.gold(make_date(self.rng, 1938, 2004), "DOB")

    def address(self, with_city: bool = True) -> None:
        self.doc.gold(make_address(self.rng, with_city), "ADDRESS", [] if with_city else ["street_only"])

    def decoy(self, kind: str) -> None:
        r = self.rng
        if kind == "CUSIP":
            self.doc.decoy(make_cusip(r), "CUSIP")
        elif kind == "FORM":
            self.doc.decoy(r.pick(FORMS), "FORM")
        elif kind == "PERCENT":
            self.doc.decoy(make_percent(r), "PERCENT")
        elif kind == "AMOUNT":
            self.doc.decoy(make_amount(r), "AMOUNT")
        elif kind == "DATE":
            self.doc.decoy(make_date(r, 2024, 2027), "DATE")
        elif kind == "YEAR":
            if r.chance(0.4):
                y = r.between(2026, 2035)
                dash = r.pick(("-", EN_DASH))
                self.doc.decoy(f"{y}{dash}{y + r.between(2, 6)}", "YEAR", ["year_range"])
            else:
                self.doc.decoy(str(r.between(2026, 2045)), "YEAR")
        elif kind == "FIN_TERM":
            self.doc.decoy(r.pick(FIN_TERMS), "FIN_TERM")
        else:
            raise ValueError(kind)


# --------------------------------------------------------------- templates


def t_meeting_note(w: Writer) -> None:
    r, d = w.rng, w.doc
    a, b = Person(r, fin_term=r.chance(0.3)), Person(r)
    d.text("Meeting notes, ")
    w.decoy("DATE")
    d.text(". Attendees: ")
    w.name(a)
    d.text(" and ")
    w.name(b)
    d.text(".\n")
    w.name(a, "first")
    d.text(" asked about a ")
    w.decoy("FIN_TERM")
    d.text(" of ")
    w.decoy("AMOUNT")
    d.text(" before ")
    w.decoy("YEAR")
    d.text("; the marginal bracket is ")
    w.decoy("PERCENT")
    d.text(".\n")
    if r.chance(0.6):
        d.text("DOB ")
        w.dob()
        d.text(", SSN ")
        w.number(make_ssn(r), "SSN")
        d.text(".\n")
    if r.chance(0.5):
        d.text("Mailing address: ")
        w.address()
        d.text(".\n")
    d.text("Follow up by phone at ")
    w.number(make_phone(r), "PHONE")
    d.text(" or email ")
    w.email(a)
    d.text(".\n")


def t_wire(w: Writer) -> None:
    r, d = w.rng, w.doc
    p = Person(r, fin_term=r.chance(0.2))
    d.text("Wire request: send ")
    w.decoy("AMOUNT")
    d.text(" to ")
    w.name(p)
    d.text(", routing ")
    w.number(make_routing(r), "ROUTING")
    d.text(", account ")
    w.number(make_account(r), "ACCOUNT")
    d.text(". Value date ")
    w.decoy("DATE")
    d.text(".\nCallback verified at ")
    w.number(make_phone(r), "PHONE")
    d.text(". Confirmation goes to ")
    w.email(p if r.chance(0.5) else None)
    d.text(".\n")


def t_account_form(w: Writer) -> None:
    r, d = w.rng, w.doc
    p = Person(r, fin_term=r.chance(0.25))
    d.text("NEW ACCOUNT APPLICATION\nName: ")
    w.name(p, r.pick(("full", "upper", "inverted", "middle")))
    d.text("\nDate of birth: ")
    w.dob()
    d.text("\nSocial Security No.: ")
    w.number(make_ssn(r), "SSN")
    d.text("\nResidential address: ")
    w.address()
    d.text("\nPhone: ")
    w.number(make_phone(r), "PHONE")
    d.text("\nEmail: ")
    w.email(p)
    if r.chance(0.5):
        d.text("\nEmployer EIN: ")
        w.number(make_ein(r), "EIN")
    d.text("\nFunding: ACH from routing ")
    w.number(make_routing(r), "ROUTING")
    d.text(" acct ")
    w.number(make_account(r), "ACCOUNT")
    d.text("\n")


def t_transcript(w: Writer) -> None:
    r, d = w.rng, w.doc
    client, adviser = Person(r, fin_term=r.chance(0.35)), Person(r)
    d.text("[Call transcript, auto-generated]\nAdviser (")
    w.name(adviser, "full")
    d.text("): Thanks for calling. Can you confirm your name?\nClient: Sure, it's ")
    w.name(client, r.pick(("lower", "full")))
    d.text(".\nAdviser: And the card on file?\nClient: It's ")
    w.number(make_card(r), "CARD")
    d.text(". I also want to talk about the ")
    w.decoy("FIN_TERM")
    d.text(".\nAdviser: Noted. We'll send ")
    w.decoy("FORM")
    d.text(" in ")
    w.decoy("YEAR")
    d.text(".\n")
    if r.chance(0.5):
        d.text("Client: Mail it to ")
        w.address(with_city=r.chance(0.5))
        d.text(".\n")


def t_trade_note(w: Writer) -> None:
    """Mostly decoys: numbers that are not personal information."""
    r, d = w.rng, w.doc
    d.text("Trade blotter: bought ")
    d.text(str(r.between(10, 900)))
    d.text(" shares, CUSIP ")
    w.decoy("CUSIP")
    d.text(", trade date ")
    w.decoy("DATE")
    d.text(", settles ")
    w.decoy("DATE")
    d.text(". Yield ")
    w.decoy("PERCENT")
    d.text(", cost ")
    w.decoy("AMOUNT")
    d.text(".\nAlso held: ")
    w.decoy("CUSIP")
    d.text(" (")
    w.decoy("FIN_TERM")
    d.text("). Report on ")
    w.decoy("FORM")
    d.text(" and ")
    w.decoy("FORM")
    d.text(".\n")
    if r.chance(0.3):
        d.text("Booked for ")
        w.name(Person(r, fin_term=r.chance(0.5)), "title")
        d.text(".\n")


def t_tax_note(w: Writer) -> None:
    r, d = w.rng, w.doc
    p = Person(r, fin_term=r.chance(0.4))
    w.name(p)
    d.text("'s ")
    w.decoy("FORM")
    d.text(" shows AGI of ")
    w.decoy("AMOUNT")
    d.text(". ")
    w.decoy("FORM")
    d.text(" lists the ")
    w.decoy("FIN_TERM")
    d.text(" at ")
    w.decoy("AMOUNT")
    d.text(", taxed at ")
    w.decoy("PERCENT")
    d.text(".\nTrust EIN ")
    w.number(make_ein(r), "EIN")
    d.text("; trustee ")
    w.name(Person(r), "title")
    d.text(". Planning years ")
    w.doc.decoy(f"{r.between(2026, 2030)}\u2013{r.between(2031, 2036)}", "YEAR", ["year_range", "lookalike_dash"])
    d.text(".\n")


def t_hard_names(w: Writer) -> None:
    """Names that are also finance words, next to the finance words."""
    r, d = w.rng, w.doc
    p = Person(r, fin_term=True)
    w.name(p, r.pick(("full", "title", "inverted")))
    d.text(" wants to know whether the ")
    w.decoy("FIN_TERM")
    d.text(" still makes sense, and whether ")
    w.decoy("FIN_TERM")
    d.text(" changes the plan. ")
    w.name(p, "first")
    d.text(" can be reached at ")
    w.email(p)
    d.text(".\n")


# pw-redact-core regression cases. The separators and hidden characters are the
# ones in its tests/test_unicode_bypass.py (read 2026-11-01, commit c9f44b8);
# the values are this generator's own synthetic ones.
PW_BYPASS_CASES = (
    ("ssn_u2011", "SSN", "\u2011"),
    ("ssn_u2212", "SSN", "\u2212"),
    ("ssn_u2013", "SSN", "\u2013"),
    ("ssn_u2010", "SSN", "\u2010"),
    ("ssn_uff0d", "SSN", "\uff0d"),
    ("ssn_zwsp", "SSN", "zw:\u200b"),
    ("ssn_shy", "SSN", "zw:\u00ad"),
    ("ssn_wj_bom", "SSN", "wjbom"),
    ("card_nbsp", "CARD", "\u00a0"),
    ("card_nnbsp", "CARD", "\u202f"),
    ("card_thin", "CARD", "\u2009"),
    ("email_zwsp", "EMAIL", "zw:\u200b"),
)


def pw_regression_doc(rng: Rng, doc: Doc, case: tuple[str, str, str]) -> None:
    name, etype, sep = case
    tag = f"pw_redact_core:{name}"
    if etype == "SSN":
        v = make_ssn(rng)
        if sep == "wjbom":
            v = v[:2] + "\u2060" + v[2:9] + "\ufeff" + v[9:]
            kind = "zero_width"
        elif sep.startswith("zw:"):
            v = v[:3] + sep[3:] + v[3:]
            kind = "zero_width"
        else:
            v = v.replace("-", sep)
            kind = "lookalike_dash"
        doc.text("SSN ")
        doc.gold(v, "SSN", [kind, tag])
    elif etype == "CARD":
        doc.text("card ")
        doc.gold(group_card(rng.pick(TEST_CARDS[:6]), sep), "CARD", ["lookalike_space", tag])
    else:
        p = Person(rng)
        local = f"{p.first}.{p.last}".lower()
        doc.text("email: ")
        doc.gold(f"{local}\u200b@example.com", "EMAIL", ["zero_width", "name_in_email", tag])
    doc.text(".\n")


def pw_allowlist_doc(rng: Rng, doc: Doc, variant: int) -> None:
    """Finance values pw-redact-core's tests require to survive redaction."""
    tag = "pw_redact_core:allowlist"
    if variant == 0:
        doc.text("AGI is ")
        doc.decoy("$425,000", "AMOUNT", [tag])
        doc.text("\u00a0and the rate is ")
        doc.decoy("24%", "PERCENT", [tag])
        doc.text(" bracket.\n")
    elif variant == 1:
        doc.text("Planning years ")
        doc.decoy("2026\u20132030", "YEAR", [tag, "year_range", "lookalike_dash"])
        doc.text(" at age 65.\n")
    elif variant == 2:
        doc.text("Portfolio worth ")
        doc.decoy("$1,250,000", "AMOUNT", [tag])
        doc.text(" with ")
        doc.decoy("7.5%", "PERCENT", [tag])
        doc.text(" return; loan rate ")
        doc.decoy("6.75%", "PERCENT", [tag])
        doc.text(", target year ")
        doc.decoy("2032", "YEAR", [tag])
        doc.text(".\n")
    elif variant == 3:
        doc.text("Filed on ")
        doc.decoy("03/15/2025", "DATE", [tag, "date_without_dob_context"])
        doc.text("; the year is ")
        doc.decoy("2025", "YEAR", [tag])
        doc.text(". Reference number 411111111111 is twelve digits.\n")
    else:
        doc.text("CUSIP: ")
        doc.decoy("594918104", "CUSIP", [tag])
        doc.text("; the security ")
        doc.decoy("037833100", "CUSIP", [tag])
        doc.text(" is in the portfolio. Roth conversion of ")
        doc.decoy("$50,000", "AMOUNT", [tag])
        doc.text(" planned.\n")


TEMPLATES = (
    ("meeting_note", t_meeting_note, 3),
    ("wire", t_wire, 2),
    ("account_form", t_account_form, 2),
    ("transcript", t_transcript, 2),
    ("trade_note", t_trade_note, 2),
    ("tax_note", t_tax_note, 2),
    ("hard_names", t_hard_names, 1),
)


def generate(seed: int = DEFAULT_SEED, n_docs: int = DEFAULT_DOCS, hard_rate: float = 0.3) -> list[dict]:
    rng = Rng(seed)
    docs: list[dict] = []
    # Fixed regression docs first, so their ids do not move when n_docs changes.
    for case in PW_BYPASS_CASES:
        d = Doc(f"pw-{case[0]}", "pw_regression")
        pw_regression_doc(rng, d, case)
        docs.append(d.to_json())
    for v in range(5):
        d = Doc(f"pw-allowlist-{v}", "pw_allowlist")
        pw_allowlist_doc(rng, d, v)
        docs.append(d.to_json())
    weighted = [t for t in TEMPLATES for _ in range(t[2])]
    i = 0
    while len(docs) < n_docs:
        name, fn, _ = rng.pick(weighted)
        d = Doc(f"d{i:04d}", name)
        fn(Writer(rng, d, hard_rate))
        docs.append(d.to_json())
        i += 1
    for doc in docs:
        validate_doc(doc)
    return docs


def validate_doc(doc: dict) -> None:
    text = doc["text"]
    ranges = sorted([(s["start"], s["end"]) for s in doc["spans"]] + [(s["start"], s["end"]) for s in doc["decoys"]])
    for (a0, a1), (b0, _) in zip(ranges, ranges[1:]):
        assert a1 <= b0, f"{doc['id']}: overlapping annotations"
    for s in doc["spans"]:
        value = text[s["start"]:s["end"]]
        assert value.strip() == value and value, f"{doc['id']}: bad span {value!r}"
        plain = "".join(chr(ord(c) - 0xFF10 + 48) if "\uff10" <= c <= "\uff19" else c for c in value)
        digits = "".join(c for c in plain if c.isdigit())
        if s["type"] == "CARD":
            assert luhn_ok(digits), f"{doc['id']}: card fails Luhn"
        if s["type"] == "ROUTING":
            assert aba_ok(digits), f"{doc['id']}: routing fails ABA check"
        if s["type"] == "SSN":
            assert digits[0] == "9" and 1 <= int(digits[3:5]) <= 49, f"{doc['id']}: SSN outside synthetic range"
        if s["type"] == "EMAIL":
            assert value.split("@")[1] in ("example.com", "example.org", "example.net")


def dumps(docs: list[dict]) -> str:
    return "".join(json.dumps(d, ensure_ascii=True, sort_keys=True) + "\n" for d in docs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--docs", type=int, default=DEFAULT_DOCS)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true", help="fail if --out differs from a fresh run")
    args = ap.parse_args(argv)
    content = dumps(generate(args.seed, args.docs))
    if args.check:
        current = args.out.read_text(encoding="ascii") if args.out.exists() else ""
        if current != content:
            print(f"{args.out} differs from a fresh run with seed {args.seed}", file=sys.stderr)
            return 1
        print(f"{args.out}: matches seed {args.seed}, {args.docs} docs")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(content, encoding="ascii")
    print(f"wrote {args.out} ({args.docs} docs, seed {args.seed})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
