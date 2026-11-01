"""Offline checks for the PII bake-off. Standard library only.

    python -m unittest discover -s pii/bakeoff/tests -v
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

BAKEOFF = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BAKEOFF))

import generate  # noqa: E402
import score  # noqa: E402
from adapters import AdapterUnavailable, local_llm, regex_baseline  # noqa: E402

DATA = BAKEOFF / "data" / "synthetic_v1.jsonl"

# Characters that must never appear raw in committed files: zero-width,
# bidi controls, look-alike dashes and spaces, full-width digits.
FORBIDDEN = set("\u200b\u200c\u200d\u200e\u200f\u2060\ufeff\u00ad\u00a0\u202f\u2009")
FORBIDDEN |= {chr(c) for c in range(0x202A, 0x202F)} | {chr(c) for c in range(0x2066, 0x206A)}
FORBIDDEN |= {chr(c) for c in range(0x2010, 0x2016)} | {"\u2212", "\uff0d"}
FORBIDDEN |= {chr(c) for c in range(0xFF10, 0xFF1A)}


def load_gold() -> list[dict]:
    return score.load_jsonl(DATA)


class GeneratorTest(unittest.TestCase):
    def test_committed_dataset_matches_a_fresh_run(self):
        fresh = generate.dumps(generate.generate(generate.DEFAULT_SEED, generate.DEFAULT_DOCS))
        self.assertEqual(DATA.read_text(encoding="ascii"), fresh,
                         "data/synthetic_v1.jsonl differs from generate.py; rerun it and the results")

    def test_seed_changes_output(self):
        a = generate.dumps(generate.generate(1, 40))
        b = generate.dumps(generate.generate(2, 40))
        self.assertNotEqual(a, b)
        self.assertEqual(a, generate.dumps(generate.generate(1, 40)))

    def test_dataset_shape(self):
        docs = load_gold()
        self.assertTrue(300 <= len(docs) <= 500)
        types = {s["type"] for d in docs for s in d["spans"]}
        self.assertEqual(types, set(generate.GOLD_TYPES))
        kinds = {s["kind"] for d in docs for s in d["decoys"]}
        self.assertEqual(kinds, set(generate.DECOY_KINDS))
        tags = {t for d in docs for s in d["spans"] for t in s["tags"]}
        for tag in ("lookalike_dash", "lookalike_space", "fullwidth", "zero_width", "fin_term_name", "name_in_email"):
            self.assertIn(tag, tags)
        pw = {t for t in tags if t.startswith("pw_redact_core:")}
        self.assertEqual(len(pw), len(generate.PW_BYPASS_CASES))

    def test_values_are_synthetic_ranges(self):
        for d in load_gold():
            generate.validate_doc(d)  # Luhn, ABA, 9xx SSN, example domains
            for s in d["spans"]:
                if s["type"] == "PHONE":
                    digits = "".join(c for c in d["text"][s["start"]:s["end"]] if c.isdigit())
                    plain = "".join(str(int(c)) for c in digits)  # full-width digits too
                    self.assertEqual(plain[-7:-2], "55501", d["id"])

    def test_checksums(self):
        self.assertTrue(generate.luhn_ok("4111111111111111"))
        self.assertFalse(generate.luhn_ok("4111111111111112"))
        self.assertTrue(generate.aba_ok("011000015"))
        self.assertFalse(generate.aba_ok("011000016"))
        self.assertEqual(generate.cusip_check_digit("03783310"), "0")  # 037833100, from pw-redact-core's tests


class NoRawInvisibleCharactersTest(unittest.TestCase):
    def test_committed_files_use_escapes(self):
        for path in sorted(BAKEOFF.rglob("*")):
            if path.is_file() and path.suffix in (".py", ".jsonl", ".json", ".md", ".txt", ".yml"):
                bad = FORBIDDEN & set(path.read_text(encoding="utf-8"))
                self.assertFalse(bad, f"{path} has raw {sorted(hex(ord(c)) for c in bad)}")


class ScorerTest(unittest.TestCase):
    def test_self_check(self):
        self.assertEqual(score.self_check(), [])

    def test_gold_as_predictions_is_perfect_on_the_dataset(self):
        docs = load_gold()
        preds = {d["id"]: [{"start": s["start"], "end": s["end"], "type": s["type"]} for s in d["spans"]] for d in docs}
        r = score.score(docs, preds, n_boot=0)
        self.assertEqual(r["overall"]["exact"]["f1"], 1.0)
        self.assertEqual(r["overall"]["leak_rate"], 0.0)
        self.assertEqual(r["overall"]["decoy_masked_rate"], 0.0)


class RegexBaselineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = load_gold()
        adapter = regex_baseline.load()
        cls.preds = {d["id"]: adapter.predict(d["text"]) for d in cls.docs}
        cls.result = score.score(cls.docs, cls.preds, n_boot=0)

    def test_offsets_cover_hidden_characters(self):
        text = "SSN 9\u200b01\u201102\u20110003 and card 4111\u00a01111\u00a01111\u00a01111."
        spans = regex_baseline.load().predict(text)
        got = {(s["type"], text[s["start"]:s["end"]]) for s in spans}
        self.assertIn(("SSN", "9\u200b01\u201102\u20110003"), got)
        self.assertIn(("CARD", "4111\u00a01111\u00a01111\u00a01111"), got)

    def test_pw_redact_core_bypass_cases_do_not_leak(self):
        self.assertEqual(self.result["slices"]["pw_redact_core:*"]["leak_rate"], 0.0)

    def test_decoys_are_not_masked(self):
        self.assertEqual(self.result["overall"]["decoy_masked_rate"], 0.0)

    def test_matches_committed_results(self):
        runs = sorted(p for p in (BAKEOFF / "results").glob("*/results.json"))
        self.assertTrue(runs, "no committed results")
        committed = json.loads(runs[-1].read_text())["results"]["regex"]
        for mode in score.MODES:
            self.assertAlmostEqual(self.result["overall"][mode]["f1"], committed["overall"][mode]["f1"], places=9)
        self.assertAlmostEqual(self.result["overall"]["leak_rate"], committed["overall"]["leak_rate"], places=9)


class LocalLLMTest(unittest.TestCase):
    def test_locate_finds_exact_copies_only(self):
        text = "Dana Roth, 900-01-0001. Dana Roth again."
        spans = local_llm.locate(text, [{"type": "person", "value": "Dana Roth"}, {"type": "SSN", "value": "900 01 0001"}])
        self.assertEqual([(s["type"], s["start"]) for s in spans], [("PERSON", 0), ("PERSON", 24)])

    def test_refuses_remote_endpoint(self):
        with self.assertRaises(AdapterUnavailable):
            local_llm.LocalLLM(model="m", endpoint="https://example.com")


if __name__ == "__main__":
    unittest.main()
