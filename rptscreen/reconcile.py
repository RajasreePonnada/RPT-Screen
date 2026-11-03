"""Reconciliation: ledger gross flows per counterparty vs the draft Ind AS 24 note.

Deterministic. Catches the "disclosed but understated" pattern (Coffee Day /
MACEL: highest balance reported instead of gross transactions). Ind AS 24
discloses by category, with named parties for the larger ones, so the check runs
on the note's rows that carry a counterparty reference.
"""
from __future__ import annotations

from .models import Transaction

TOLERANCE_PCT = 5.0   # variance below this is treated as rounding / timing
TOLERANCE_ABS_CR = 1.0

FLOW_KINDS = {"purchase", "sale", "loan_given", "loan_taken", "advance", "rent", "service", "receipt"}  # 'grn' is a receipt, not a flow


def ledger_gross(txns: list[Transaction]) -> float:
    return round(sum(t.amount for t in txns if t.kind in FLOW_KINDS), 2)


def reconcile(note: dict, txns_by_cp: dict[str, list[Transaction]]) -> list[dict]:
    items = []
    for row in note["categories"]:
        lid = row.get("ledger_id")
        if not lid:
            continue
        gross = ledger_gross(txns_by_cp.get(lid, []))
        disclosed = float(row["disclosed_amount_cr"])
        variance = round(gross - disclosed, 2)
        pct = round(100.0 * variance / disclosed, 1) if disclosed else None
        if abs(variance) <= TOLERANCE_ABS_CR or (pct is not None and abs(pct) <= TOLERANCE_PCT):
            continue
        items.append({
            "ledger_id": lid, "party": row["party"], "category": row["category"], "transaction_type": row["transaction_type"],
            "disclosed_cr": disclosed, "ledger_gross_cr": gross, "variance_cr": variance, "variance_pct": pct,
            "rows": [t.row_id for t in txns_by_cp.get(lid, []) if t.kind in FLOW_KINDS],
            "source": note["source"],
            "note": "Ind AS 24 para 18 requires gross transaction amounts; a balance-based figure or an omission would show here.",
        })
    return items
