"""Run the pipeline on the Gensol public-record set.

Refuses to run while any TO_FILL placeholder remains, and prints where they are, so
the run can only happen after the registry data has actually been retrieved and the
pre-registered expectations committed.

Usage:
  python run_gensol.py              # validate templates; run if complete
  python run_gensol.py --check      # validate only
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rptscreen.pipeline import run  # noqa: E402
from rptscreen.report import write_evidence_pack, write_markdown  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "gensol")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "gensol")
FILES = ["registry.json", "shareholding.json", "group.json", "mbp1.json", "vendor_master.json", "ledger.json",
         "management_rp_list.json", "indas24_note.json", "approvals.json"]


def find_placeholders(obj, path, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("_"):
                continue
            find_placeholders(v, f"{path}.{k}", out)
            if isinstance(k, str) and "TO_FILL" in k:
                out.append(f"{path}.{k} (key)")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_placeholders(v, f"{path}[{i}]", out)
    elif isinstance(obj, str) and "TO_FILL" in obj:
        out.append(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    missing = []
    for f in FILES:
        with open(os.path.join(DATA, f)) as fh:
            find_placeholders(json.load(fh), f, missing)
    if missing:
        print(f"{len(missing)} placeholders remain. Fill these from public records before running:")
        for m in missing:
            print("  -", m)
        print("\nAlso confirm data/gensol/EXPECTATIONS.md is final and committed before the first run.")
        sys.exit(1)
    if args.check:
        print("templates complete")
        return

    result = run(DATA, extractor_kind="stub", company_id="G0")
    write_evidence_pack(result, OUT)
    write_markdown(result, OUT)
    print(f"wrote {OUT}/evidence_pack.json and report.md — compare against data/gensol/EXPECTATIONS.md by hand")


if __name__ == "__main__":
    main()
