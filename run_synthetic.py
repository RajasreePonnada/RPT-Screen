"""Run the pipeline on the synthetic company and compare against expected.json.

Usage:
  python run_synthetic.py                      # stub extractor, rules as in force during the period
  python run_synthetic.py --extractor openrouter
  python run_synthetic.py --rule-as-of 2022-10-01   # counterfactual: evaluate under the rules of that date
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rptscreen.pipeline import run  # noqa: E402
from rptscreen.report import write_evidence_pack, write_markdown  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "synthetic")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "synthetic")


def compare(result: dict, expected: dict) -> list[dict]:
    by_cp = {}
    for q in result["queue"]:
        by_cp.setdefault(q["counterparty_id"], []).append(q)
    unresolved = {u["ledger_id"] for u in result["unresolved"]}
    rows = []
    for c in expected["cases"]:
        lid = c["ledger_id"]
        items = by_cp.get(lid, [])
        got_types = sorted({q["item_type"] for q in items})
        if c["expect"] == "unresolved":
            ok = lid in unresolved
            got = "unresolved" if ok else ",".join(got_types) or "none"
        elif c["expect"] == "none":
            ok = not any(q["item_type"] == "rule_hit" for q in items)
            got = ",".join(got_types) or "none"
        else:
            cand = [q for q in items if q["item_type"] == c["expect"]]
            if c["expect"] == "rule_hit" and c.get("clause"):
                cand = [q for q in cand if q["detail"]["clause_id"] == c["clause"]]
            ok = bool(cand)
            if ok and c.get("evidence_tier") is not None:
                ok = any(q["evidence_tier"] == c["evidence_tier"] for q in cand)
            got = ",".join(f"{q['item_type']}:{q['detail'].get('clause_id', '')}:tier{q['evidence_tier']}" for q in items) or "none"
        if c["designed_miss"]:
            # The relationship exists in the synthetic world but in no record the auditor can see.
            verdict = "DESIGNED MISS (not detectable)" if ok else "UNEXPECTED HIT"
        else:
            verdict = "PASS" if ok else "FAIL"
        rows.append({"case": c["case"], "ledger_id": lid, "title": c["title"], "expected": c["expect"] + (f" {c['clause']}" if c.get("clause") else "") + (f" tier {c['evidence_tier']}" if c.get("evidence_tier") is not None else ""),
                     "got": got, "verdict": verdict, "note": c["note"]})
    return rows


def render_compare(rows: list[dict]) -> str:
    out = ["| Case | Counterparty | Expected | Got | Verdict |", "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['case']} | {r['title']} ({r['ledger_id']}) | {r['expected']} | {r['got']} | {r['verdict']} |")
    n_pass = sum(1 for r in rows if r["verdict"] == "PASS")
    n_fail = sum(1 for r in rows if r["verdict"] == "FAIL")
    n_miss = sum(1 for r in rows if r["verdict"].startswith("DESIGNED MISS"))
    n_unexp = sum(1 for r in rows if r["verdict"] == "UNEXPECTED HIT")
    out.append(f"\n{n_pass} pass, {n_fail} fail, {n_miss} designed misses (relationship exists but is not discoverable from the auditor's vantage point), {n_unexp} unexpected hits.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extractor", default="stub", choices=["stub", "openrouter"])
    ap.add_argument("--rule-as-of", default=None)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    result = run(DATA, extractor_kind=args.extractor, rule_as_of=args.rule_as_of)
    suffix = f"_asof_{args.rule_as_of}" if args.rule_as_of else ""
    out_dir = args.out + suffix
    write_evidence_pack(result, out_dir)
    write_markdown(result, out_dir)

    with open(os.path.join(DATA, "expected.json")) as f:
        expected = json.load(f)
    rows = compare(result, expected)
    table = render_compare(rows)
    with open(os.path.join(out_dir, "test_results.md"), "w") as f:
        f.write("# Planted cases vs pipeline output\n\n" + table + "\n")
    print(table)
    print(f"\nwrote {out_dir}/evidence_pack.json, report.md, test_results.md")


if __name__ == "__main__":
    main()
