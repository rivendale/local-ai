#!/usr/bin/env python3
"""Run detector adapters over the fixed dataset and write scored results.

    python run.py --adapters regex --out results/2026-11-01
    /tmp/venv/bin/python run.py --adapters regex,presidio --out results/2026-11-01

Writes, in ``--out``:

- ``results.json``: environment, dataset hash, adapter versions, metrics with
  bootstrap 95% intervals, and why any adapter did not run.
- ``results.md``: the same numbers as tables.
- ``predictions-<adapter>.jsonl``: raw spans, so a result can be rescored.

Adapter options go as ``--opt adapter.key=value`` (for example
``--opt gliner.revision=<sha>``).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import adapters  # noqa: E402
from generate import DATASET_VERSION, DEFAULT_SEED, GOLD_TYPES  # noqa: E402
from score import load_jsonl, score  # noqa: E402


def git_head() -> str | None:
    try:
        return subprocess.run(["git", "-C", str(HERE), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


def code_sha256() -> str:
    """Hash of the bake-off code (generator, scorer, runner, adapters)."""
    h = hashlib.sha256()
    for path in sorted([*HERE.glob("*.py"), *(HERE / "adapters").glob("*.py")]):
        h.update(path.relative_to(HERE).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()


def git_dirty() -> bool | None:
    try:
        out = subprocess.run(["git", "-C", str(HERE), "status", "--porcelain", "--", "."], capture_output=True, text=True, check=True).stdout
        return bool(out.strip())
    except Exception:  # noqa: BLE001
        return None


def parse_opts(pairs: list[str]) -> dict[str, dict[str, str]]:
    opts: dict[str, dict[str, str]] = {}
    for p in pairs:
        key, _, value = p.partition("=")
        adapter, _, field = key.partition(".")
        opts.setdefault(adapter, {})[field] = value
    return opts


def fmt(x, pct: bool = True) -> str:
    if x is None:
        return "n/a"
    return f"{100 * x:.1f}" if pct else f"{x:.3f}"


def fmt_ci(ci: dict, key: str) -> str:
    if key not in ci:
        return ""
    lo, hi = ci[key]
    return f" ({100 * lo:.1f} to {100 * hi:.1f})"


def markdown(report: dict) -> str:
    lines = [
        f"# PII bake-off results, {report['date']}",
        "",
        "Measurements on the synthetic dataset in `../../data/`, not product rankings. "
        "Numbers are percentages; brackets are bootstrap 95% intervals over documents. "
        "See `../../README.md` for what each metric means and what the dataset leaves out.",
        "",
        f"- Dataset: `{report['dataset']['file']}`, {report['dataset']['docs']} documents, "
        f"{report['dataset']['gold_spans']} gold spans, sha256 `{report['dataset']['sha256'][:16]}`",
        f"- Code: sha256 `{report['environment']['code_sha256'][:16]}` over the bake-off's .py files "
        f"(repository HEAD `{report['environment']['repo_commit']}` when run, uncommitted changes: "
        f"{report['environment']['bakeoff_dir_dirty']})",
        f"- Python {report['environment']['python']} on {report['environment']['platform']}",
        "",
        "## Overall",
        "",
        "| Adapter | Exact F1 | Overlap P | Overlap R | Overlap F1 | Untyped R | Leaked chars | Decoys masked |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, r in report["results"].items():
        o, ci = r["overall"], r["ci95"]
        lines.append(
            f"| {name} | {fmt(o['exact']['f1'])}{fmt_ci(ci, 'overall.exact.f1')} "
            f"| {fmt(o['overlap']['precision'])}{fmt_ci(ci, 'overall.overlap.precision')} "
            f"| {fmt(o['overlap']['recall'])}{fmt_ci(ci, 'overall.overlap.recall')} "
            f"| {fmt(o['overlap']['f1'])}{fmt_ci(ci, 'overall.overlap.f1')} "
            f"| {fmt(o['untyped']['recall'])}{fmt_ci(ci, 'overall.untyped.recall')} "
            f"| {fmt(o['leak_rate'])}{fmt_ci(ci, 'overall.leak_rate')} "
            f"| {fmt(o['decoy_masked_rate'])}{fmt_ci(ci, 'overall.decoy_masked_rate')} |"
        )
    for name, r in report["results"].items():
        lines += ["", f"## {name}: per type", "",
                  "| Type | Gold | Overlap P | Overlap R | Overlap F1 | Exact F1 | Untyped R | Leaked chars |",
                  "|---|---|---|---|---|---|---|---|"]
        ci = r["ci95"]
        for t in GOLD_TYPES:
            pt = r["per_type"][t]
            k = f"per_type.{t}"
            lines.append(
                f"| {t} | {int(pt['overlap']['n_gold'])} | {fmt(pt['overlap']['precision'])} "
                f"| {fmt(pt['overlap']['recall'])}{fmt_ci(ci, k + '.overlap.recall')} "
                f"| {fmt(pt['overlap']['f1'])}{fmt_ci(ci, k + '.overlap.f1')} | {fmt(pt['exact']['f1'])} "
                f"| {fmt(pt['untyped_recall'])} | {fmt(pt['leak_rate'])}{fmt_ci(ci, k + '.leak_rate')} |"
            )
        lines += ["", f"### {name}: hard cases (untyped overlap recall, leaked characters)", "",
                  "| Tag | Spans | Untyped R | Leaked chars |", "|---|---|---|---|"]
        for tag, s in r["slices"].items():
            lines.append(f"| {tag} | {s['n']} | {fmt(s['untyped_recall'])} | {fmt(s['leak_rate'])} |")
        lines += ["", f"### {name}: decoys masked, by kind", "", "| Kind | Masked chars |", "|---|---|"]
        for kind, v in r["decoy_masked_by_kind"].items():
            lines.append(f"| {kind} | {fmt(v)} |")
    lines += ["", "## Adapters", ""]
    for name, info in report["adapters"].items():
        lines.append(f"- **{name}**: `{json.dumps(info, sort_keys=True)}`")
    if report["not_run"]:
        lines += ["", "## Not run", ""]
        for name, why in report["not_run"].items():
            lines.append(f"- **{name}**: {why}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run PII detector adapters on the synthetic dataset.")
    ap.add_argument("--adapters", default="regex")
    ap.add_argument("--data", type=Path, default=HERE / "data" / "synthetic_v1.jsonl")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--opt", action="append", default=[])
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--note", action="append", default=[], help="adapter=text, added to a not-run reason")
    args = ap.parse_args(argv)

    gold = load_jsonl(args.data)
    raw = args.data.read_bytes()
    opts = parse_opts(args.opt)
    args.out.mkdir(parents=True, exist_ok=True)
    report = {
        "date": args.date,
        "dataset": {
            "file": f"{DATASET_VERSION}.jsonl",
            "generator_seed": DEFAULT_SEED,
            "docs": len(gold),
            "gold_spans": sum(len(d["spans"]) for d in gold),
            "decoys": sum(len(d["decoys"]) for d in gold),
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": f"{platform.system()} {platform.machine()}",
            "repo_commit": git_head(),
            "bakeoff_dir_dirty": git_dirty(),
            "code_sha256": code_sha256(),
        },
        "adapters": {},
        "not_run": {},
        "results": {},
    }
    for name in [a.strip() for a in args.adapters.split(",") if a.strip()]:
        try:
            adapter = adapters.load(name, **opts.get(name, {}))
        except adapters.AdapterUnavailable as exc:
            notes = [n.partition("=")[2] for n in args.note if n.partition("=")[0] == name]
            report["not_run"][name] = " ".join([str(exc).rstrip(".") + "."] + notes)
            print(f"{name}: not run: {exc}", file=sys.stderr)
            continue
        started = time.perf_counter()
        preds = {d["id"]: adapter.predict(d["text"]) for d in gold}
        elapsed = time.perf_counter() - started
        info = adapter.info()
        info["wall_seconds_all_docs"] = round(elapsed, 2)
        report["adapters"][name] = info
        with open(args.out / f"predictions-{name}.jsonl", "w", encoding="ascii") as f:
            for d in gold:
                f.write(json.dumps({"id": d["id"], "spans": preds[d["id"]]}, ensure_ascii=True, sort_keys=True) + "\n")
        report["results"][name] = score(gold, preds, args.bootstrap, args.seed)
        o = report["results"][name]["overall"]
        print(f"{name}: overlap F1 {fmt(o['overlap']['f1'])}, leaked {fmt(o['leak_rate'])}%, {elapsed:.1f}s")
    (args.out / "results.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii")
    (args.out / "results.md").write_text(markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
