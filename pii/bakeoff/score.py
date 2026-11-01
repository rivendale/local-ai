#!/usr/bin/env python3
"""Span-level scoring for the PII bake-off. Standard library only.

Inputs are the gold dataset (``generate.py`` output) and predictions: one JSON
object per line, ``{"id": doc_id, "spans": [{"start", "end", "type"}, ...]}``.

Metrics, per entity type and overall:

- **exact**: a prediction matches a gold span with the same start, end and type.
- **overlap**: a prediction matches a gold span of the same type that shares at
  least one character. Precision counts predictions that overlap a same-type
  gold span; recall counts gold spans overlapped by a same-type prediction.
- **untyped overlap**: as overlap, ignoring type. This is what matters for
  masking, where the label does not change what is hidden.
- **leaked characters**: of the visible characters inside gold spans
  (whitespace and zero-width characters excluded), the share not covered by
  the union of all predicted spans, of any type. This is what a redactor that
  masks every predicted span leaves in clear.
- **decoy over-redaction**: the share of decoy characters (CUSIPs, form
  numbers, amounts, percentages, non-birth dates, years, finance terms)
  covered by a prediction. Lower is better.

Predictions whose type is not a gold type (``OTHER``) count against overall
typed precision but not against any one type.

Confidence intervals are 95% percentile intervals from a bootstrap that
resamples documents with replacement (each document is a cluster), so spans
from one document move together.

    python score.py --self-check
    python score.py --gold data/synthetic_v1.jsonl --pred preds.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from generate import GOLD_TYPES, ZERO_WIDTH  # noqa: E402

INVISIBLE = frozenset(ZERO_WIDTH) | {"\u2060", "\u00ad"}
MODES = ("exact", "overlap", "untyped")


def load_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def visible(ch: str) -> bool:
    return not ch.isspace() and ch not in INVISIBLE


def _overlaps(a: dict, b: dict) -> bool:
    return a["start"] < b["end"] and b["start"] < a["end"]


def doc_counts(doc: dict, preds: list[dict]) -> dict[str, float]:
    """Additive counts for one document. Keys are 'metric|type|field'."""
    c: dict[str, float] = defaultdict(float)
    gold = doc["spans"]
    seen = set()
    uniq = []
    for p in preds:
        key = (p["start"], p["end"], p["type"])
        if key not in seen and p["end"] > p["start"]:
            seen.add(key)
            uniq.append(p)
    preds = uniq

    for mode in MODES:
        for p in preds:
            if mode == "exact":
                hit = any(g["start"] == p["start"] and g["end"] == p["end"] and g["type"] == p["type"] for g in gold)
            elif mode == "overlap":
                hit = any(g["type"] == p["type"] and _overlaps(g, p) for g in gold)
            else:
                hit = any(_overlaps(g, p) for g in gold)
            t = p["type"] if p["type"] in GOLD_TYPES and mode != "untyped" else "OTHER"
            for bucket in (t, "ALL"):
                c[f"{mode}|{bucket}|n_pred"] += 1
                c[f"{mode}|{bucket}|tp_pred"] += hit
        for g in gold:
            if mode == "exact":
                hit = any(g["start"] == p["start"] and g["end"] == p["end"] and g["type"] == p["type"] for p in preds)
            elif mode == "overlap":
                hit = any(g["type"] == p["type"] and _overlaps(g, p) for p in preds)
            else:
                hit = any(_overlaps(g, p) for p in preds)
            for bucket in (g["type"], "ALL"):
                c[f"{mode}|{bucket}|n_gold"] += 1
                c[f"{mode}|{bucket}|tp_gold"] += hit

    text = doc["text"]
    masked = bytearray(len(text))
    for p in preds:
        for i in range(max(0, p["start"]), min(len(text), p["end"])):
            masked[i] = 1
    for g in gold:
        for i in range(g["start"], g["end"]):
            if visible(text[i]):
                for bucket in (g["type"], "ALL"):
                    c[f"leak|{bucket}|chars"] += 1
                    c[f"leak|{bucket}|leaked"] += not masked[i]
    for dcy in doc.get("decoys", []):
        for i in range(dcy["start"], dcy["end"]):
            if visible(text[i]):
                for bucket in (dcy["kind"], "ALL"):
                    c[f"decoy|{bucket}|chars"] += 1
                    c[f"decoy|{bucket}|masked"] += masked[i]
    return dict(c)


def prf(c: dict[str, float], mode: str, bucket: str) -> dict[str, float | None]:
    n_pred = c.get(f"{mode}|{bucket}|n_pred", 0)
    n_gold = c.get(f"{mode}|{bucket}|n_gold", 0)
    p = c.get(f"{mode}|{bucket}|tp_pred", 0) / n_pred if n_pred else None
    r = c.get(f"{mode}|{bucket}|tp_gold", 0) / n_gold if n_gold else None
    f = 2 * p * r / (p + r) if p is not None and r is not None and (p + r) > 0 else (0.0 if p is not None and r is not None else None)
    return {"precision": p, "recall": r, "f1": f, "n_pred": n_pred, "n_gold": n_gold}


def ratio(c: dict[str, float], num: str, den: str) -> float | None:
    d = c.get(den, 0)
    return c.get(num, 0) / d if d else None


def summarize(c: dict[str, float]) -> dict:
    out: dict = {"overall": {}, "per_type": {}, "decoy_masked_by_kind": {}}
    for mode in MODES:
        out["overall"][mode] = prf(c, mode, "ALL")
    out["overall"]["leak_rate"] = ratio(c, "leak|ALL|leaked", "leak|ALL|chars")
    out["overall"]["decoy_masked_rate"] = ratio(c, "decoy|ALL|masked", "decoy|ALL|chars")
    for t in GOLD_TYPES:
        out["per_type"][t] = {
            "exact": prf(c, "exact", t),
            "overlap": prf(c, "overlap", t),
            "untyped_recall": prf(c, "untyped", t)["recall"],
            "leak_rate": ratio(c, f"leak|{t}|leaked", f"leak|{t}|chars"),
        }
    kinds = sorted({k.split("|")[1] for k in c if k.startswith("decoy|") and k.split("|")[1] != "ALL"})
    for k in kinds:
        out["decoy_masked_by_kind"][k] = ratio(c, f"decoy|{k}|masked", f"decoy|{k}|chars")
    return out


def add(total: dict[str, float], part: dict[str, float], times: int = 1) -> None:
    for k, v in part.items():
        total[k] = total.get(k, 0) + v * times


def _flatten(d: dict, prefix: str = "") -> dict[str, float]:
    flat = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            flat.update(_flatten(v, key + "."))
        elif isinstance(v, float) and not key.endswith(("n_pred", "n_gold")):
            flat[key] = v
    return flat


def _set(d: dict, dotted: str, value) -> None:
    keys = dotted.split(".")
    for k in keys[:-1]:
        d = d[k]
    d[keys[-1]] = value


def bootstrap(per_doc: list[dict[str, float]], n: int, seed: int) -> dict[str, tuple[float, float]]:
    """95% percentile intervals for every rate in ``summarize``, docs as clusters."""
    if n <= 0 or not per_doc:
        return {}
    rng = random.Random(seed)
    m = len(per_doc)
    samples: dict[str, list[float]] = defaultdict(list)
    for _ in range(n):
        counts = [0] * m
        for _ in range(m):
            counts[int(rng.random() * m) % m] += 1
        total: dict[str, float] = {}
        for i, k in enumerate(counts):
            if k:
                add(total, per_doc[i], k)
        for key, val in _flatten(summarize(total)).items():
            samples[key].append(val)
    ci = {}
    for key, vals in samples.items():
        vals.sort()
        lo = vals[int(0.025 * (len(vals) - 1))]
        hi = vals[int(round(0.975 * (len(vals) - 1)))]
        ci[key] = (lo, hi)
    return ci


def slice_recall(gold_docs: list[dict], preds_by_id: dict[str, list[dict]]) -> dict[str, dict]:
    """Untyped overlap recall and leak rate for gold spans carrying each tag."""
    acc: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for doc in gold_docs:
        preds = preds_by_id.get(doc["id"], [])
        text = doc["text"]
        for g in doc["spans"]:
            hit = any(_overlaps(g, p) for p in preds)
            covered = [any(p["start"] <= i < p["end"] for p in preds) for i in range(g["start"], g["end"])]
            vis = [visible(text[i]) for i in range(g["start"], g["end"])]
            for tag in g["tags"] or ["plain"]:
                tag = "pw_redact_core:*" if tag.startswith("pw_redact_core:") else tag
                a = acc[tag]
                a["n"] += 1
                a["hit"] += hit
                a["chars"] += sum(vis)
                a["leaked"] += sum(1 for c, v in zip(covered, vis) if v and not c)
    return {
        tag: {"n": int(a["n"]), "untyped_recall": a["hit"] / a["n"], "leak_rate": a["leaked"] / a["chars"] if a["chars"] else None}
        for tag, a in sorted(acc.items())
    }


def score(gold_docs: list[dict], preds_by_id: dict[str, list[dict]], n_boot: int = 1000, seed: int = 0) -> dict:
    per_doc = [doc_counts(d, preds_by_id.get(d["id"], [])) for d in gold_docs]
    total: dict[str, float] = {}
    for c in per_doc:
        add(total, c)
    result = summarize(total)
    ci = bootstrap(per_doc, n_boot, seed)
    result["ci95"] = {k: [round(lo, 4), round(hi, 4)] for k, (lo, hi) in sorted(ci.items())}
    result["bootstrap"] = {"resamples": n_boot, "seed": seed, "unit": "document"}
    result["slices"] = slice_recall(gold_docs, preds_by_id)
    result["n_docs"] = len(gold_docs)
    return result


# ---------------------------------------------------------------- self-check


def self_check() -> list[str]:
    """Return a list of failures; empty means the scorer behaves as specified."""
    fails: list[str] = []

    def expect(name: str, got, want) -> None:
        if isinstance(want, float):
            ok = got is not None and abs(got - want) < 1e-9
        else:
            ok = got == want
        if not ok:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    # Hand-built document: "Call Dana Roth at 212-555-0101 about the Roth IRA."
    text = "Call Dana Roth at 212-555-0101 about the Roth IRA."
    doc = {
        "id": "t1",
        "text": text,
        "spans": [
            {"start": 5, "end": 14, "type": "PERSON", "tags": []},
            {"start": 18, "end": 30, "type": "PHONE", "tags": []},
        ],
        "decoys": [{"start": 41, "end": 49, "kind": "FIN_TERM", "tags": []}],
    }
    assert text[5:14] == "Dana Roth" and text[18:30] == "212-555-0101" and text[41:49] == "Roth IRA"

    # 1. Perfect predictions.
    r = score([doc], {"t1": [{"start": s["start"], "end": s["end"], "type": s["type"]} for s in doc["spans"]]}, 0)
    for mode in MODES:
        expect(f"perfect {mode} f1", r["overall"][mode]["f1"], 1.0)
    expect("perfect leak", r["overall"]["leak_rate"], 0.0)
    expect("perfect decoy", r["overall"]["decoy_masked_rate"], 0.0)

    # 2. No predictions: recall 0, precision undefined, everything leaks.
    r = score([doc], {}, 0)
    expect("empty recall", r["overall"]["overlap"]["recall"], 0.0)
    expect("empty precision", r["overall"]["overlap"]["precision"], None)
    expect("empty leak", r["overall"]["leak_rate"], 1.0)

    # 3. Name found without its last letter, phone typed as ACCOUNT, and the
    #    decoy "Roth" flagged as a PERSON.
    preds = [
        {"start": 5, "end": 13, "type": "PERSON"},   # "Dana Rot"
        {"start": 18, "end": 30, "type": "ACCOUNT"},  # right span, wrong type
        {"start": 41, "end": 45, "type": "PERSON"},  # "Roth" in "Roth IRA"
    ]
    r = score([doc], {"t1": preds}, 0)
    expect("exact tp", r["overall"]["exact"]["recall"], 0.0)
    expect("overlap recall", r["overall"]["overlap"]["recall"], 0.5)
    expect("overlap precision", r["overall"]["overlap"]["precision"], 1 / 3)
    expect("untyped recall", r["overall"]["untyped"]["recall"], 1.0)
    expect("untyped precision", r["overall"]["untyped"]["precision"], 2 / 3)
    # Visible gold chars: "DanaRoth" (8) + "212-555-0101" (12) = 20; 1 leaked ("h").
    expect("leak", r["overall"]["leak_rate"], 1 / 20)
    expect("PERSON leak", r["per_type"]["PERSON"]["leak_rate"], 1 / 8)
    # Decoy "RothIRA" has 7 visible chars; "Roth" masked.
    expect("decoy", r["overall"]["decoy_masked_rate"], 4 / 7)
    expect("PHONE typed recall", r["per_type"]["PHONE"]["overlap"]["recall"], 0.0)
    expect("PHONE untyped recall", r["per_type"]["PHONE"]["untyped_recall"], 1.0)

    # 4. Zero-width characters inside a span are not counted as leaked text.
    zw = "SSN 9\u200b01-02-0003."
    zdoc = {"id": "z", "text": zw, "spans": [{"start": 4, "end": 16, "type": "SSN", "tags": ["zero_width"]}], "decoys": []}
    r = score([zdoc], {"z": [{"start": 6, "end": 16, "type": "SSN"}]}, 0)
    # Visible: "901-02-0003" = 11 chars; "9" leaked.
    expect("zero-width leak", r["overall"]["leak_rate"], 1 / 11)
    expect("zero-width slice", r["slices"]["zero_width"]["untyped_recall"], 1.0)

    # 5. Bootstrap intervals bracket the point estimate and are reproducible.
    docs = [dict(doc, id=f"b{i}") for i in range(20)]
    preds_b = {f"b{i}": (preds if i % 2 else []) for i in range(20)}
    r1 = score(docs, preds_b, 200, seed=1)
    r2 = score(docs, preds_b, 200, seed=1)
    lo, hi = r1["ci95"]["overall.untyped.recall"]
    point = r1["overall"]["untyped"]["recall"]
    if not (lo <= point <= hi and lo < hi):
        fails.append(f"bootstrap interval [{lo}, {hi}] does not bracket {point}")
    if r1["ci95"] != r2["ci95"]:
        fails.append("bootstrap is not reproducible with the same seed")

    # 6. Duplicate predictions are not double counted.
    dup = [{"start": 5, "end": 14, "type": "PERSON"}] * 3
    r = score([doc], {"t1": dup}, 0)
    expect("dedup precision", r["overall"]["exact"]["precision"], 1.0)
    return fails


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Score PII predictions against the synthetic gold set.")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--gold", type=Path, default=HERE / "data" / "synthetic_v1.jsonl")
    ap.add_argument("--pred", type=Path)
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    if args.self_check:
        fails = self_check()
        for f in fails:
            print("FAIL", f, file=sys.stderr)
        print("scorer self-check:", "ok" if not fails else f"{len(fails)} failures")
        return 1 if fails else 0
    if not args.pred:
        ap.error("--pred is required unless --self-check")
    preds = {p["id"]: p["spans"] for p in load_jsonl(args.pred)}
    print(json.dumps(score(load_jsonl(args.gold), preds, args.bootstrap, args.seed), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
