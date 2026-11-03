"""The rulebook: legal definitions as effective-dated graph predicates.

Each clause is a function over the graph evaluated for one counterparty against
one audit period. Clauses carry valid_from / valid_to so an audit of an earlier
period is evaluated against the rules in force then. Nothing legal lives
anywhere else in the codebase.

Sources (text paraphrased in `text`):
  Companies Act 2013 s.2(76), s.2(77) + Rules 3-4 of the Companies (Specification
  of Definitions Details) Rules 2014; SEBI LODR Reg 2(1)(zb) as amended by the
  Sixth Amendment 2021 (eff. 1 Apr 2022 / 1 Apr 2023); Reg 23(1) materiality as
  amended 1 Apr 2022 and by the Fifth Amendment 2025 (Schedule XII, eff. 18 Dec 2025).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable, Optional

from .graph import RPGraph, edge_to_path_item, window_intersection
from .models import Edge, RuleHit

ORIGIN_STRENGTH = {"human": 6, "registry": 5, "filing": 4, "books": 3, "ledger": 2, "llm": 1}


@dataclass
class Clause:
    id: str
    text: str
    valid_from: Optional[date]
    valid_to: Optional[date]
    fn: Callable


def _hit(cp_id: str, clause: Clause, edges: list[Edge], start: date, end: date) -> Optional[RuleHit]:
    win = window_intersection([(e.valid_from, e.valid_to) for e in edges], start, end)
    if win is None:
        return None
    weakest = min(edges, key=_origin_strength)
    return RuleHit(
        counterparty_id=cp_id, clause_id=clause.id,
        rule_version=f"{clause.id}@{clause.valid_from.isoformat() if clause.valid_from else 'origin'}",
        path=[edge_to_path_item(e) for e in edges],
        min_confidence=round(min(e.confidence for e in edges), 3),
        weakest_origin=weakest.origin,
        relationship_window=win,
    )


def _origin_strength(e: Edge) -> int:
    return ORIGIN_STRENGTH.get(e.origin, 0)


# ---------- helpers over the graph ----------

def directors_of(g: RPGraph, company: str, start: date, end: date) -> list[Edge]:
    return g.in_edges(company, "DIRECTOR_OF", start, end)


def kmp_of(g: RPGraph, company: str, start: date, end: date) -> list[Edge]:
    return g.in_edges(company, "KMP_OF", start, end)


def relatives_of(g: RPGraph, person: str, start: date, end: date) -> list[tuple[str, Edge]]:
    out = []
    for e in g.undirected_edges(person, "RELATIVE_OF", start, end):
        other = e.dst if e.src == person else e.src
        out.append((other, e))
    return out


def insider_paths(g: RPGraph, company: str, start: date, end: date, include_kmp: bool) -> dict[str, list[list[Edge]]]:
    """person_id -> list of edge-paths from that person to the company (direct, or via a relative)."""
    paths: dict[str, list[list[Edge]]] = {}
    base = directors_of(g, company, start, end) + (kmp_of(g, company, start, end) if include_kmp else [])
    for e in base:
        paths.setdefault(e.src, []).append([e])
        for rel, re_ in relatives_of(g, e.src, start, end):
            paths.setdefault(rel, []).append([re_, e])
    return paths


def is_private(g: RPGraph, node_id: str) -> Optional[bool]:
    n = g.nodes.get(node_id)
    if n is None or n.kind not in ("entity", "firm"):
        return None
    if n.attrs.get("is_public") is None:
        return None
    return not n.attrs["is_public"]


# ---------- clause predicates ----------

def c_76_i(g, company, cp, start, end, clause):
    hits = []
    for e in directors_of(g, company, start, end):
        if e.src == cp:
            h = _hit(cp, clause, [e], start, end)
            if h:
                hits.append(h)
        for rel, re_ in relatives_of(g, e.src, start, end):
            if rel == cp:
                h = _hit(cp, clause, [re_, e], start, end)
                if h:
                    hits.append(h)
    return hits


def c_76_ii(g, company, cp, start, end, clause):
    hits = []
    for e in kmp_of(g, company, start, end):
        if e.src == cp:
            h = _hit(cp, clause, [e], start, end)
            if h:
                hits.append(h)
        for rel, re_ in relatives_of(g, e.src, start, end):
            if rel == cp:
                h = _hit(cp, clause, [re_, e], start, end)
                if h:
                    hits.append(h)
    return hits


def c_76_iii(g, company, cp, start, end, clause):
    n = g.nodes.get(cp)
    if n is None or n.kind != "firm":
        return []
    hits = []
    ins = insider_paths(g, company, start, end, include_kmp=False)
    for pe in g.in_edges(cp, "PARTNER_OF", start, end):
        for path in ins.get(pe.src, []):
            h = _hit(cp, clause, [pe] + path, start, end)
            if h:
                hits.append(h)
    return hits


def c_76_iv(g, company, cp, start, end, clause):
    priv = is_private(g, cp)
    n = g.nodes.get(cp)
    if n is None or n.kind != "entity" or priv is False:
        return []
    hits = []
    ins = insider_paths(g, company, start, end, include_kmp=False)
    for etype in ("DIRECTOR_OF", "MEMBER_OF"):
        for pe in g.in_edges(cp, etype, start, end):
            if pe.dst == company:
                continue
            for path in ins.get(pe.src, []):
                h = _hit(cp, clause, [pe] + path, start, end)
                if h:
                    hits.append(h)
    return hits


def c_76_v(g, company, cp, start, end, clause):
    if is_private(g, cp) is not False:
        return []
    hits = []
    dirs = {e.src: e for e in directors_of(g, company, start, end)}
    for pe in g.in_edges(cp, "DIRECTOR_OF", start, end):
        if pe.src not in dirs:
            continue
        holders = [pe.src] + [r for r, _ in relatives_of(g, pe.src, start, end)]
        sh_edges = []
        for hld in holders:
            sh_edges.extend([e for e in g.in_edges(cp, "SHAREHOLDER_OF", start, end) if e.src == hld])
        pct = sum(e.attrs.get("pct", 0) for e in sh_edges)
        if pct > 2.0:
            h = _hit(cp, clause, [pe] + sh_edges + [dirs[pe.src]], start, end)
            if h:
                hits.append(h)
    return hits


def c_76_viii(g, company, cp, start, end, clause):
    hits = []
    for e in g.out_edges(cp, "SUBSIDIARY_OF", start, end):
        if e.dst == company:
            h = _hit(cp, clause, [e], start, end)
            if h:
                hits.append(h)
    for e in g.out_edges(company, "SUBSIDIARY_OF", start, end):
        if e.dst == cp:
            h = _hit(cp, clause, [e], start, end)
            if h:
                hits.append(h)
        # fellow subsidiary: both are subsidiaries of the same holding
        for e2 in g.out_edges(cp, "SUBSIDIARY_OF", start, end):
            if e2.dst == e.dst and cp != company:
                h = _hit(cp, clause, [e2, e], start, end)
                if h:
                    hits.append(h)
    for e in g.undirected_edges(cp, "ASSOCIATE_OF", start, end):
        if company in (e.src, e.dst):
            h = _hit(cp, clause, [e], start, end)
            if h:
                hits.append(h)
    return hits


def c_rule3(g, company, cp, start, end, clause):
    hits = []
    for he in g.out_edges(company, "SUBSIDIARY_OF", start, end):
        holding = he.dst
        for e in directors_of(g, holding, start, end) + kmp_of(g, holding, start, end):
            if "independent" in str(e.attrs.get("designation", "")).lower():
                continue
            if e.src == cp:
                h = _hit(cp, clause, [e, he], start, end)
                if h:
                    hits.append(h)
            for rel, re_ in relatives_of(g, e.src, start, end):
                if rel == cp:
                    h = _hit(cp, clause, [re_, e, he], start, end)
                    if h:
                        hits.append(h)
    return hits


def c_lodr_zb_a(g, company, cp, start, end, clause):
    hits = []
    for e in g.out_edges(cp, "PROMOTER_GROUP_OF", start, end):
        if e.dst == company:
            h = _hit(cp, clause, [e], start, end)
            if h:
                hits.append(h)
                break
    return hits


def _make_lodr_zb_b(threshold_pct: float):
    def fn(g, company, cp, start, end, clause):
        # "at any time during the immediately preceding financial year"
        prev_start = date(start.year - 1, start.month, start.day)
        prev_end = start - timedelta(days=1)
        best = None
        for e in g.out_edges(cp, "SHAREHOLDER_OF", prev_start, prev_end):
            if e.dst != company:
                continue
            if e.attrs.get("pct", 0) >= threshold_pct:
                if best is None or e.attrs["pct"] > best.attrs["pct"]:
                    best = e
        if best is None:
            return []
        h = RuleHit(counterparty_id=cp, clause_id=clause.id,
                    rule_version=f"{clause.id}@{clause.valid_from.isoformat()}",
                    path=[edge_to_path_item(best)], min_confidence=best.confidence, weakest_origin=best.origin,
                    relationship_window=(start, end))
        h.path[0]["note"] = f"held {best.attrs['pct']}% >= {threshold_pct}% during preceding FY {prev_start}..{prev_end}"
        return [h]
    return fn


CLAUSES: list[Clause] = [
    Clause("CA2013_2(76)(i)", "a director or his relative", date(2013, 9, 12), None, c_76_i),
    Clause("CA2013_2(76)(ii)", "a key managerial personnel or his relative", date(2013, 9, 12), None, c_76_ii),
    Clause("CA2013_2(76)(iii)", "a firm in which a director, manager or his relative is a partner", date(2013, 9, 12), None, c_76_iii),
    Clause("CA2013_2(76)(iv)", "a private company in which a director or manager or his relative is a member or director", date(2013, 9, 12), None, c_76_iv),
    Clause("CA2013_2(76)(v)", "a public company in which a director or manager is a director and holds along with his relatives more than 2% of its paid-up share capital", date(2013, 9, 12), None, c_76_v),
    Clause("CA2013_2(76)(viii)", "holding, subsidiary, associate or fellow subsidiary company", date(2013, 9, 12), None, c_76_viii),
    Clause("CA2013_Rule3", "a director (other than an independent director) or KMP of the holding company, or his relative", date(2014, 7, 17), None, c_rule3),
    Clause("LODR_2(1)(zb)(a)", "any person or entity forming part of the promoter or promoter group of the listed entity", date(2022, 4, 1), None, c_lodr_zb_a),
    Clause("LODR_2(1)(zb)(b)", "any person or entity holding 20% or more of the listed entity, directly or on a beneficial interest basis, at any time during the immediately preceding FY", date(2022, 4, 1), date(2023, 3, 31), _make_lodr_zb_b(20.0)),
    Clause("LODR_2(1)(zb)(b)", "any person or entity holding 10% or more of the listed entity, directly or on a beneficial interest basis, at any time during the immediately preceding FY", date(2023, 4, 1), None, _make_lodr_zb_b(10.0)),
]

# Clauses that exist in law but are not record-testable. Listed so the coverage
# report can say they were NOT evaluated, rather than silently omitting them.
HUMAN_ONLY_CLAUSES = [
    ("CA2013_2(76)(vi)", "body corporate whose board/MD/manager is accustomed to act on the advice of a director or manager"),
    ("CA2013_2(76)(vii)", "person on whose advice a director or manager is accustomed to act"),
    ("LODR_2(1)(zc)_purpose_and_effect", "transaction with an unrelated party whose purpose and effect is to benefit a related party"),
]


def clauses_in_force(start: date, end: date, rule_as_of: Optional[date] = None) -> list[Clause]:
    """Clauses whose validity overlaps the audit period (or a single as-of date for counterfactuals)."""
    out = []
    for c in CLAUSES:
        vf = c.valid_from or date(1900, 1, 1)
        vt = c.valid_to or date(2999, 12, 31)
        if rule_as_of is not None:
            if vf <= rule_as_of <= vt:
                out.append(c)
        elif vf <= end and vt >= start:
            out.append(c)
    return out


def evaluate_counterparty(g: RPGraph, company: str, cp: str, start: date, end: date, rule_as_of: Optional[date] = None) -> list[RuleHit]:
    hits = []
    for c in clauses_in_force(start, end, rule_as_of):
        hits.extend(c.fn(g, company, cp, start, end, c))
    return hits


def coverage_gaps(g: RPGraph, cp: str) -> list[str]:
    """Clauses that could not be evaluated for this counterparty for lack of data."""
    gaps = []
    n = g.nodes.get(cp)
    if n is None:
        return ["all: counterparty not resolved to any record"]
    if n.kind == "entity":
        if n.attrs.get("is_public") is None:
            gaps.append("2(76)(iv)/(v): public/private status unknown")
        has_sh = any(e.type in ("SHAREHOLDER_OF", "MEMBER_OF") and e.dst == cp for e in g.edges)
        if not has_sh:
            gaps.append("2(76)(iv) member test and 2(76)(v): no shareholding record for this counterparty (MGT-7 not inspected)")
    for cid, _ in HUMAN_ONLY_CLAUSES:
        gaps.append(f"{cid}: human judgment only")
    return gaps


# ---------- materiality (LODR Reg 23(1)) ----------

def materiality_threshold_cr(consolidated_turnover_cr: float, on: date) -> tuple[float, str]:
    if on < date(2022, 4, 1):
        return 0.10 * consolidated_turnover_cr, "Reg23(1) pre-2022: 10% of consolidated turnover"
    if on < date(2025, 12, 18):
        return min(1000.0, 0.10 * consolidated_turnover_cr), "Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover"
    t = consolidated_turnover_cr
    if t <= 20000:
        return 0.10 * t, "Schedule XII (eff. 2025-12-18) tier 1: 10% of turnover"
    if t <= 40000:
        return 2000.0 + 0.05 * (t - 20000), "Schedule XII (eff. 2025-12-18) tier 2: Rs 2,000 cr + 5% of turnover above Rs 20,000 cr"
    return min(3000.0 + 0.025 * (t - 40000), 5000.0), "Schedule XII (eff. 2025-12-18) tier 3: lower of Rs 3,000 cr + 2.5% above Rs 40,000 cr, or Rs 5,000 cr"
