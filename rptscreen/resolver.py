"""Entity resolution: ledger counterparty names to graph nodes.

Order of evidence: identifier agreement (CIN / LLPIN / PAN / GSTIN-derived PAN)
> exact canonical name > fuzzy similarity. Fuzzy matches carry their score as
confidence; identifiers carry 1.0. Nothing here creates a relationship edge.

Thresholds (TAU_HIGH, TAU_LOW) were set from the synthetic test set: the decoy
pair "sunrise agro private limited" / "sunrise agro foods limited" must stay
apart while "bharat coldchain private limited" / "bharat cold chain private
limited" must merge. See README for the calibration table.
"""
from __future__ import annotations

from rapidfuzz import fuzz

from .canon import canon_name, pan_from_gstin
from .models import MatchRecord, Node

TAU_HIGH = 90.0
TAU_LOW = 75.0
EXACT_NAME_CONFIDENCE = 0.95


def _score(a: str, b: str) -> float:
    return max(fuzz.ratio(a, b), fuzz.token_set_ratio(a, b))


def _identifier_match(cp: dict, nodes: list[Node]) -> tuple[Node | None, str]:
    ids = {}
    if cp.get("cin"):
        ids["cin"] = cp["cin"].strip().upper()
    if cp.get("llpin"):
        ids["llpin"] = cp["llpin"].strip().upper()
    pan = cp.get("pan") or pan_from_gstin(cp.get("gstin"))
    if pan:
        ids["pan"] = pan.strip().upper()
    for n in nodes:
        for k, v in ids.items():
            if n.identifiers.get(k, "").upper() == v:
                how = k if cp.get(k) else f"pan derived from gstin {cp.get('gstin')}"
                return n, f"{how} = {v}"
    return None, ""


def _by_score(item):
    return item[0]


def resolve_counterparty(cp: dict, nodes: list[Node]) -> MatchRecord:
    node, ev = _identifier_match(cp, nodes)
    if node is not None:
        return MatchRecord(ledger_name=cp["name"], ledger_id=cp["ledger_id"], node_id=node.id, method="identifier", score=100.0, evidence=ev)

    cname = canon_name(cp["name"])
    scored = []
    for n in nodes:
        if n.kind == "address":
            continue
        best = 0.0
        best_name = ""
        for nm in n.names:
            s = _score(cname, canon_name(nm))
            if s > best:
                best, best_name = s, nm
        scored.append((best, n, best_name))
    scored.sort(key=_by_score, reverse=True)
    if not scored:
        return MatchRecord(ledger_name=cp["name"], ledger_id=cp["ledger_id"], node_id=None, method="none", score=0.0, evidence="no candidates")

    top_s, top_n, top_name = scored[0]
    second_s = scored[1][0] if len(scored) > 1 else 0.0

    if canon_name(top_name) == cname:
        return MatchRecord(ledger_name=cp["name"], ledger_id=cp["ledger_id"], node_id=top_n.id, method="exact_name", score=100.0,
                           evidence=f"canonical names identical: '{cname}'")
    if top_s >= TAU_HIGH:
        if second_s >= TAU_HIGH:
            return MatchRecord(ledger_name=cp["name"], ledger_id=cp["ledger_id"], node_id=top_n.id, method="candidate", score=top_s,
                               evidence=f"ambiguous: '{top_name}' {top_s:.0f} vs '{scored[1][2]}' {second_s:.0f}")
        return MatchRecord(ledger_name=cp["name"], ledger_id=cp["ledger_id"], node_id=top_n.id, method="fuzzy", score=top_s,
                           evidence=f"fuzzy '{cname}' ~ '{canon_name(top_name)}' score {top_s:.0f}")
    if top_s >= TAU_LOW:
        return MatchRecord(ledger_name=cp["name"], ledger_id=cp["ledger_id"], node_id=top_n.id, method="candidate", score=top_s,
                           evidence=f"below merge threshold: '{cname}' ~ '{canon_name(top_name)}' score {top_s:.0f}")
    return MatchRecord(ledger_name=cp["name"], ledger_id=cp["ledger_id"], node_id=None, method="none", score=top_s,
                       evidence=f"best candidate '{canon_name(top_name)}' scored only {top_s:.0f}")


def resolution_confidence(m: MatchRecord) -> float:
    if m.method == "identifier":
        return 1.0
    if m.method == "exact_name":
        return EXACT_NAME_CONFIDENCE
    if m.method == "fuzzy":
        return round(m.score / 100.0, 2)
    if m.method == "candidate":
        return round(m.score / 100.0, 2)
    return 0.0
