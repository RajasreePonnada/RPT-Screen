"""Vendor risk indicators: reasons to look, never relationships.

Exactly three, all computable from the auditor's own vantage point:
  (a) counterparty shares a director, shareholder or registered address with a
      promoter-group entity or promoter  [graph, public records]
  (b) counterparty was incorporated shortly before first payment and has paid-up
      capital small relative to what it was paid  [MCA master data + ledger]
  (c) advances paid materially ahead of goods/services received  [ledger only]

Each emits a signal with its inputs and sources. None of these appears in any
legal definition of "related party"; that is exactly why they are indicators.
The thresholds below are the author's choices and are stated as such.
"""
from __future__ import annotations

from datetime import date, timedelta

from .graph import RPGraph
from .models import Transaction

NEW_VENDOR_MONTHS = 18        # (b) incorporated within this many months before first payment
CAPITAL_RATIO = 20.0          # (b) payments in period / paid-up capital
ADVANCE_GRACE_DAYS = 90       # (c) days an advance may sit before any goods receipt
UNAPPLIED_ADVANCE_PCT = 25.0  # (c2) advances not matched by receipts at period end, as % of advances
CIRCULAR_RATIO = 0.5          # (d) min(paid, received) / max(paid, received)
CIRCULAR_MIN_GROSS_CR = 10.0  # (d) ignore small counterparties

# Post-registration additions (2026-11-02), after retrieving the Gensol public records:
#   (b2) thin capital regardless of age   — Go-Auto (2008, Rs 2.9 cr capital, Rs 775 cr received)
#   (c2) unapplied advance at period end  — Go-Auto (Rs 775 cr paid, Rs 567.73 cr of EVs delivered; GRN dates not public)
#   (d)  circular flow                    — Wellray (Rs 424 cr out, Rs 310 cr back, Rs 1 lakh capital)
# These were NOT in the pre-registered design. They are kept separate so the brief can say which
# signals came from the real document rather than from the original design.


def promoter_side(g: RPGraph, company: str, start: date, end: date) -> set[str]:
    ids = set()
    for e in g.in_edges(company, "PROMOTER_GROUP_OF", start, end):
        ids.add(e.src)
    return ids


def indicator_a(g: RPGraph, company: str, cp: str, start: date, end: date) -> list[dict]:
    out = []
    promo = promoter_side(g, company, start, end)
    if cp in promo or cp == company:
        return out
    # shared registered address
    cp_addrs = {e.dst for e in g.out_edges(cp, "REGISTERED_AT", start, end)}
    for p in promo:
        for e in g.out_edges(p, "REGISTERED_AT", start, end):
            if e.dst in cp_addrs:
                out.append({"indicator": "a", "signal": "shared_registered_address", "with": p, "with_name": g.nodes[p].names[0],
                            "value": g.nodes[e.dst].names[0], "sources": [pp.model_dump(mode="json") for pp in e.provenance]})
    # shared director (who is not themselves a director of the company — that case is a rule hit)
    company_dirs = {e.src for e in g.in_edges(company, "DIRECTOR_OF", start, end)}
    cp_dirs = {e.src: e for e in g.in_edges(cp, "DIRECTOR_OF", start, end)}
    for p in promo:
        for e in g.in_edges(p, "DIRECTOR_OF", start, end):
            if e.src in cp_dirs and e.src not in company_dirs:
                out.append({"indicator": "a", "signal": "shared_director_with_promoter_entity", "with": p, "with_name": g.nodes[p].names[0],
                            "value": g.nodes[e.src].names[0], "sources": [pp.model_dump(mode="json") for pp in e.provenance + cp_dirs[e.src].provenance]})
    # promoter-side shareholder in the counterparty
    for e in g.in_edges(cp, "SHAREHOLDER_OF", start, end):
        if e.src in promo:
            out.append({"indicator": "a", "signal": "promoter_entity_is_shareholder", "with": e.src, "with_name": g.nodes[e.src].names[0],
                        "value": f"{e.attrs.get('pct')}%", "sources": [pp.model_dump(mode="json") for pp in e.provenance]})
    return out


def indicator_b(g: RPGraph, cp: str, txns: list[Transaction]) -> list[dict]:
    n = g.nodes.get(cp)
    if n is None or not txns:
        return []
    inc = n.attrs.get("incorporated_on")
    cap = n.attrs.get("paid_up_capital_cr")
    if not inc or cap is None:
        return []
    inc_d = date.fromisoformat(inc)
    first = min(t.date for t in txns)
    paid = sum(t.amount for t in txns if t.kind in ("purchase", "advance", "service", "rent", "loan_given"))
    months = (first.year - inc_d.year) * 12 + (first.month - inc_d.month)
    ratio = (paid / cap) if cap > 0 else float("inf")
    out = []
    desc = f"incorporated {inc}, first payment {first.isoformat()} ({months} months); paid Rs {paid:.1f} cr vs paid-up capital Rs {cap} cr (ratio {ratio:.0f}x)"
    srcs = [pp.model_dump(mode="json") for pp in n.provenance] + [{"ledger_rows": [t.row_id for t in txns]}]
    if months <= NEW_VENDOR_MONTHS and ratio >= CAPITAL_RATIO:
        out.append({"indicator": "b", "signal": "new_thinly_capitalised_vendor", "value": desc,
                    "thresholds": {"months": NEW_VENDOR_MONTHS, "ratio": CAPITAL_RATIO}, "sources": srcs})
    elif ratio >= CAPITAL_RATIO * 10:
        out.append({"indicator": "b2", "signal": "thinly_capitalised_vendor_any_age", "value": desc, "post_registration": True,
                    "thresholds": {"ratio": CAPITAL_RATIO * 10}, "sources": srcs})
    return out


def indicator_c(txns: list[Transaction]) -> list[dict]:
    advances = sorted([t for t in txns if t.kind == "advance"], key=_by_date)
    receipts = sorted([t for t in txns if t.kind == "grn"], key=_by_date)
    out = []
    for a in advances:
        later = [r for r in receipts if r.date >= a.date]
        first_receipt = later[0] if later else None
        gap = (first_receipt.date - a.date).days if first_receipt else None
        if first_receipt is None or gap > ADVANCE_GRACE_DAYS:
            recv = sum(r.amount for r in later)
            out.append({"indicator": "c", "signal": "advance_ahead_of_receipt",
                        "value": f"advance Rs {a.amount} cr on {a.date.isoformat()}; first receipt {'none' if first_receipt is None else first_receipt.date.isoformat() + f' ({gap} days later)'}; received Rs {recv:.1f} cr in total",
                        "thresholds": {"grace_days": ADVANCE_GRACE_DAYS},
                        "sources": [{"ledger_rows": [a.row_id] + [r.row_id for r in later]}]})
    return out


def indicator_c2(txns: list[Transaction]) -> list[dict]:
    """Advances not matched by receipts at period end. Does not depend on receipt dates."""
    adv = sum(t.amount for t in txns if t.kind == "advance")
    rec = sum(t.amount for t in txns if t.kind == "grn")
    if adv <= 0:
        return []
    unapplied = adv - rec
    pct = 100.0 * unapplied / adv
    if pct >= UNAPPLIED_ADVANCE_PCT:
        return [{"indicator": "c2", "signal": "unapplied_advance_at_period_end", "post_registration": True,
                 "value": f"advances Rs {adv:.2f} cr vs goods/services received Rs {rec:.2f} cr; Rs {unapplied:.2f} cr ({pct:.0f}%) unapplied",
                 "thresholds": {"pct": UNAPPLIED_ADVANCE_PCT},
                 "sources": [{"ledger_rows": [t.row_id for t in txns if t.kind in ("advance", "grn")]}]}]
    return []


def indicator_d(txns: list[Transaction]) -> list[dict]:
    """Circular flow: money goes out to a counterparty and a large share comes back."""
    paid = sum(t.amount for t in txns if t.kind in ("purchase", "advance", "service", "rent", "loan_given"))
    received = sum(t.amount for t in txns if t.kind in ("receipt", "sale", "loan_taken"))
    gross = paid + received
    if gross < CIRCULAR_MIN_GROSS_CR or paid <= 0 or received <= 0:
        return []
    ratio = min(paid, received) / max(paid, received)
    if ratio >= CIRCULAR_RATIO:
        return [{"indicator": "d", "signal": "circular_flow", "post_registration": True,
                 "value": f"paid Rs {paid:.2f} cr, received back Rs {received:.2f} cr (ratio {ratio:.2f}); net Rs {paid - received:.2f} cr on gross Rs {gross:.2f} cr",
                 "thresholds": {"ratio": CIRCULAR_RATIO, "min_gross_cr": CIRCULAR_MIN_GROSS_CR},
                 "sources": [{"ledger_rows": [t.row_id for t in txns]}]}]
    return []


def _by_date(t: Transaction):
    return t.date
