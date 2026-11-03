"""Single ranked evidence queue. No categorical lanes.

Ordering is lexicographic, so there are no weights to defend:
  1. evidence tier   0 registry-backed rule hit
                     1 filing/books-backed rule hit
                     2 rule hit depending on a fuzzy name merge
                     3 rule hit depending on an extractor-proposed edge
                     4 reconciliation variance
                     5 indicator only
  2. disclosure      0 not on management's related-party list, 1 on it
                     (a finding management did not disclose is what SA 550 is for)
  3. materiality tier 0 material under Reg 23(1) at the rule in force on the crossing date
                      1 >= 10% of the materiality threshold
                      2 below that
  4. gross value (descending)
  5. minimum confidence along the path (descending)
Each component is kept visible on the item; nothing is collapsed into one number.
"""
from __future__ import annotations

from datetime import date

from .canon import canon_name
from .models import MatchRecord, QueueItem, RuleHit, Transaction
from .resolver import resolution_confidence
from .rulebook import materiality_threshold_cr

ORIGIN_TIER = {"human": 0, "registry": 0, "filing": 1, "books": 1, "ledger": 1, "llm": 3}


def evidence_tier_for_hit(hit: RuleHit, match: MatchRecord) -> int:
    tier = ORIGIN_TIER.get(hit.weakest_origin, 3)
    if match.method in ("fuzzy", "candidate", "exact_name") and tier < 2:
        tier = 2 if match.method != "exact_name" else tier
    return tier


def materiality(txns: list[Transaction], turnover_cr: float, period_end: date, rule_as_of: date | None = None) -> dict:
    """Cumulative per-related-party value in the FY vs the threshold in force on each transaction date
    (or on rule_as_of, for a counterfactual run)."""
    total = 0.0
    crossed = None
    for t in sorted(txns, key=_by_date):
        if t.kind == "grn":
            continue
        total += t.amount
        thr, basis = materiality_threshold_cr(turnover_cr, rule_as_of or t.date)
        if crossed is None and total > thr:
            crossed = {"date": t.date.isoformat(), "cumulative_cr": round(total, 2), "threshold_cr": round(thr, 2), "basis": basis, "row_id": t.row_id}
    thr_end, basis_end = materiality_threshold_cr(turnover_cr, rule_as_of or period_end) if txns else (0, "")
    return {"gross_cr": round(total, 2), "crossed": crossed, "threshold_at_period_end_cr": round(thr_end, 2), "basis_at_period_end": basis_end}


def materiality_tier(m: dict) -> int:
    if m["crossed"]:
        return 0
    if m["threshold_at_period_end_cr"] and m["gross_cr"] >= 0.10 * m["threshold_at_period_end_cr"]:
        return 1
    return 2


def approvals_for(ledger_id: str, approvals: dict) -> list[dict]:
    return [a for a in approvals["approvals"] if a["ledger_id"] == ledger_id]


def approval_status(ledger_id: str, m: dict, approvals: dict) -> dict:
    aps = approvals_for(ledger_id, approvals)
    ac = [a for a in aps if a["type"] in ("omnibus", "specific")]
    sh = [a for a in aps if a["type"] == "shareholder"]
    ac_ok = any(a["limit_cr"] >= m["gross_cr"] for a in ac)
    needs_sh = m["crossed"] is not None
    sh_ok = (not needs_sh) or any(a["limit_cr"] >= m["gross_cr"] for a in sh)
    return {"audit_committee": "ok" if ac_ok else ("none" if not ac else "limit_exceeded"),
            "shareholder": ("ok" if sh_ok else "missing") if needs_sh else "not_required",
            "refs": [a["minute_ref"] for a in aps]}


def disclosed_by_management(cp_names: list[str], mgmt: dict) -> bool:
    canon_mgmt = {canon_name(p["name"]) for p in mgmt["parties"]}
    return any(canon_name(n) in canon_mgmt for n in cp_names)


def out_of_window_rows(hit: RuleHit, txns: list[Transaction]) -> list[str]:
    lo, hi = hit.relationship_window
    return [t.row_id for t in txns if not (lo <= t.date <= hi)]


def build_queue(hits_by_cp, matches_by_cp, txns_by_cp, cp_names, recon_items, indicators_by_cp, mgmt, approvals, turnover_cr, period_end: date, rule_as_of: date | None = None) -> list[QueueItem]:
    items: list[QueueItem] = []
    for lid, hits in hits_by_cp.items():
        match = matches_by_cp[lid]
        txns = txns_by_cp.get(lid, [])
        m = materiality(txns, turnover_cr, period_end, rule_as_of)
        mt = materiality_tier(m)
        disclosed = disclosed_by_management(cp_names[lid], mgmt)
        appr = approval_status(lid, m, approvals)
        # One item per (counterparty, clause): best path is primary, others corroborate.
        by_clause: dict[str, list] = {}
        for h in hits:
            by_clause.setdefault(h.clause_id, []).append(h)
        for clause_id, group in by_clause.items():
            scored = []
            for h in group:
                et = evidence_tier_for_hit(h, match)
                conf = round(min(h.min_confidence, resolution_confidence(match)), 3)
                scored.append((et, -conf, h))
            scored.sort(key=_by_tier_then_conf)
            et, negconf, h = scored[0]
            conf = -negconf
            alternates = [{"path": alt.path, "weakest_origin": alt.weakest_origin, "min_confidence": alt.min_confidence,
                           "evidence_tier": alt_et} for alt_et, _, alt in scored[1:]]
            items.append(QueueItem(
                counterparty_id=lid, counterparty_name=cp_names[lid][0], item_type="rule_hit",
                evidence_tier=et, materiality_tier=mt, min_confidence=conf, gross_value=m["gross_cr"],
                detail={"clause_id": h.clause_id, "rule_version": h.rule_version, "path": h.path, "weakest_origin": h.weakest_origin,
                        "alternate_paths": alternates,
                        "relationship_window": [h.relationship_window[0].isoformat(), h.relationship_window[1].isoformat()],
                        "transactions_outside_window": out_of_window_rows(h, txns),
                        "resolution": match.model_dump(), "materiality": m, "approvals": appr, "disclosed_by_management": disclosed},
                # evidence tier -> undisclosed before disclosed -> materiality -> value -> confidence
                sort_key=(et, 0 if not disclosed else 1, mt, -m["gross_cr"], -conf)))
    for r in recon_items:
        lid = r["ledger_id"]
        m = materiality(txns_by_cp.get(lid, []), turnover_cr, period_end, rule_as_of)
        mt = materiality_tier(m)
        items.append(QueueItem(counterparty_id=lid, counterparty_name=r["party"], item_type="reconciliation",
                               evidence_tier=4, materiality_tier=mt, min_confidence=1.0, gross_value=r["ledger_gross_cr"],
                               detail=r, sort_key=(4, 1, mt, -r["ledger_gross_cr"], -1.0)))
    for lid, sigs in indicators_by_cp.items():
        if not sigs:
            continue
        m = materiality(txns_by_cp.get(lid, []), turnover_cr, period_end, rule_as_of)
        mt = materiality_tier(m)
        items.append(QueueItem(counterparty_id=lid, counterparty_name=cp_names[lid][0], item_type="indicator",
                               evidence_tier=5, materiality_tier=mt, min_confidence=0.5, gross_value=m["gross_cr"],
                               detail={"signals": sigs, "resolution": matches_by_cp[lid].model_dump(), "materiality": m},
                               sort_key=(5, 1, mt, -m["gross_cr"], -0.5)))
    items.sort(key=_by_sort_key)
    return items


def _by_tier_then_conf(x):
    return (x[0], x[1])


def _by_sort_key(i: QueueItem):
    return i.sort_key


def _by_date(t: Transaction):
    return t.date
