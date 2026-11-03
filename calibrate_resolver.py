"""Print similarity scores for the name pairs that fix the resolver thresholds.

TAU_HIGH must sit above every decoy pair and below every true variant pair.
TAU_LOW marks where a pair becomes worth a human's glance.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rapidfuzz import fuzz  # noqa: E402

from rptscreen.canon import canon_name  # noqa: E402
from rptscreen.resolver import TAU_HIGH, TAU_LOW  # noqa: E402

PAIRS = [
    ("Sunrise Agro Pvt Ltd", "Sunrise Agro Private Limited", "same entity, suffix variant"),
    ("BHARAT COLDCHAIN PVT LTD", "Bharat Cold Chain Private Limited", "same entity, spacing + case"),
    ("Rao Warehousing Pvt Ltd", "Rao Warehousing Private Limited", "same entity"),
    ("Sunrise Agro Foods Ltd", "Sunrise Agro Private Limited", "DECOY: different company, shared prefix"),
    ("Sunrise Agro Foods Ltd", "Sunrise Agro Foods Limited", "same entity"),
    ("Ramesh Transport", "Lotus Transport Private Limited", "DECOY: sole proprietor vs company, shared token"),
    ("Rao Warehousing Pvt Ltd", "Rao Family Holdings Private Limited", "DECOY: shared surname"),
    ("Meridian Logistics Pvt Ltd", "Meridian Agro Industries Limited", "DECOY: subsidiary vs parent"),
    ("Apex Machinery Pvt Ltd", "Apex Machinery Private Limited", "same entity"),
]


def main():
    print(f"TAU_HIGH = {TAU_HIGH}  TAU_LOW = {TAU_LOW}\n")
    print("| Ledger name | Registry name | ratio | token_set | score used | verdict | note |")
    print("|---|---|---|---|---|---|---|")
    for a, b, note in PAIRS:
        ca, cb = canon_name(a), canon_name(b)
        r = fuzz.ratio(ca, cb)
        t = fuzz.token_set_ratio(ca, cb)
        s = max(r, t)
        if ca == cb:
            v = "exact canonical"
        elif s >= TAU_HIGH:
            v = "merge (fuzzy)"
        elif s >= TAU_LOW:
            v = "candidate → human"
        else:
            v = "distinct"
        print(f"| {a} | {b} | {r:.0f} | {t:.0f} | {s:.0f} | {v} | {note} |")


if __name__ == "__main__":
    main()
