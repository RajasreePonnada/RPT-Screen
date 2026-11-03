"""End-to-end run over one data directory.

ingest books + registry -> extract prose -> graph -> resolve counterparties ->
rule engine + reconciliation + indicators -> ranked queue + unresolved list +
coverage report -> evidence pack.
"""
from __future__ import annotations

import json
import os
from datetime import date

from .extractor import make_extractor
from .graph import RPGraph
from .indicators import indicator_a, indicator_b, indicator_c, indicator_c2, indicator_d
from .ingest import ingest_extracted, ingest_group, ingest_registry, ingest_shareholding
from .models import Transaction
from .ranking import build_queue
from .reconcile import reconcile
from .resolver import TAU_HIGH, TAU_LOW, resolve_counterparty
from .rulebook import CLAUSES, HUMAN_ONLY_CLAUSES, clauses_in_force, coverage_gaps, evaluate_counterparty


def _load(data_dir: str, name: str):
    with open(os.path.join(data_dir, name)) as f:
        return json.load(f)


def _label(n) -> str:
    name = n.names[0]
    ids = n.identifiers
    tag = ids.get("din") and f"DIN {ids['din']}" or ids.get("cin") and f"CIN {ids['cin']}" or ids.get("llpin") and f"LLPIN {ids['llpin']}" or ids.get("pan") and f"PAN {ids['pan']}" or ""
    if n.kind == "address":
        return f"address: {name}"
    return f"{name} ({tag})" if tag else f"{name} (no public identifier)"


def run(data_dir: str, extractor_kind: str = "stub", rule_as_of: str | None = None, company_id: str = "E0") -> dict:
    registry = _load(data_dir, "registry.json")
    shareholding = _load(data_dir, "shareholding.json")
    group = _load(data_dir, "group.json")
    mbp1 = _load(data_dir, "mbp1.json")
    vendor_master = _load(data_dir, "vendor_master.json")
    ledger = _load(data_dir, "ledger.json")
    mgmt = _load(data_dir, "management_rp_list.json")
    note = _load(data_dir, "indas24_note.json")
    approvals = _load(data_dir, "approvals.json")

    start = date.fromisoformat(ledger["period"][0])
    end = date.fromisoformat(ledger["period"][1])
    as_of = date.fromisoformat(rule_as_of) if rule_as_of else None
    turnover = group["consolidated_turnover_cr_FY2024_25"]

    # 1. graph from structured sources
    g = RPGraph()
    ingest_registry(g, registry, company_id)
    ingest_shareholding(g, shareholding)
    ingest_group(g, group)

    # 2. prose extraction (probabilistic), then into the graph as llm-origin edges
    extractor = make_extractor(extractor_kind)
    declarant_ids = {}
    for p in registry["people_dins"].values():
        declarant_ids[p["name"]] = p["person_id"]
    for k in registry.get("kmp", []):
        declarant_ids[k["name"]] = k["person_id"]
    results = []
    for dec in mbp1["declarations"]:
        declarant_ids.setdefault(dec["director"], dec["director_id"])
        results.append(extractor.extract(dec["director_id"], dec["text"]))
    if results:
        ingest_extracted(g, results, mbp1["source"], mbp1["declarations"][0]["date"], declarant_ids, company_id)
    extraction_log = [{"doc": r.doc_id, "backend": r.backend, "accepted": [a.model_dump() for a in r.accepted], "rejected": r.rejected} for r in results]

    # 3. ledger
    txns_by_cp: dict[str, list[Transaction]] = {}
    for row in ledger["rows"]:
        t = Transaction(row_id=row["row_id"], date=date.fromisoformat(row["date"]), counterparty_id=row["counterparty_id"],
                        counterparty_name=row["counterparty_name"], kind=row["kind"], amount=row["amount_cr"])
        txns_by_cp.setdefault(t.counterparty_id, []).append(t)

    # 4. resolve every counterparty (probabilistic)
    nodes = g.node_list()
    matches = {}
    cp_names = {}
    for cp in vendor_master["counterparties"]:
        matches[cp["ledger_id"]] = resolve_counterparty(cp, nodes)
        node = g.nodes.get(matches[cp["ledger_id"]].node_id) if matches[cp["ledger_id"]].node_id else None
        cp_names[cp["ledger_id"]] = [cp["name"]] + (node.names if node else [])

    # 5. evaluate (deterministic)
    hits_by_cp = {}
    indicators_by_cp = {}
    coverage = {}
    unresolved = []
    for cp in vendor_master["counterparties"]:
        lid = cp["ledger_id"]
        m = matches[lid]
        if m.node_id is None:
            unresolved.append({"ledger_id": lid, "name": cp["name"], "evidence": m.evidence,
                               "gross_cr": round(sum(t.amount for t in txns_by_cp.get(lid, []) if t.kind != "grn"), 2)})
            continue
        hits = evaluate_counterparty(g, company_id, m.node_id, start, end, as_of)
        if hits:
            hits_by_cp[lid] = hits
        tx = txns_by_cp.get(lid, [])
        sigs = indicator_a(g, company_id, m.node_id, start, end) + indicator_b(g, m.node_id, tx) + indicator_c(tx) + indicator_c2(tx) + indicator_d(tx)
        indicators_by_cp[lid] = sigs
        coverage[lid] = coverage_gaps(g, m.node_id)

    recon_items = reconcile(note, txns_by_cp)

    # Registry-derived related-party universe: entities the company's directors/KMP are connected to
    # that do NOT appear in the vendor master. Counterparty screening cannot see these; the auditor
    # can search bank statements and payments for them. (Capbridge in the Gensol case.)
    matched_nodes = {m.node_id for m in matches.values() if m.node_id}
    universe = []
    seen = set()
    for pe in g.in_edges(company_id, "DIRECTOR_OF", start, end) + g.in_edges(company_id, "KMP_OF", start, end):
        person = pe.src
        for et in ("DIRECTOR_OF", "PARTNER_OF", "MEMBER_OF", "SHAREHOLDER_OF"):
            for e in g.out_edges(person, et, start, end):
                if e.dst == company_id or e.dst in matched_nodes or (person, e.dst) in seen:
                    continue
                seen.add((person, e.dst))
                n = g.nodes[e.dst]
                if n.kind not in ("entity", "firm"):
                    continue
                universe.append({"entity_id": e.dst, "entity": n.names[0], "via_person": g.nodes[person].names[0], "edge": et,
                                 "origin": e.origin, "valid_from": e.valid_from.isoformat() if e.valid_from else None,
                                 "valid_to": e.valid_to.isoformat() if e.valid_to else None,
                                 "provenance": [pp.model_dump(mode="json") for pp in e.provenance]})
    queue = build_queue(hits_by_cp, matches, txns_by_cp, cp_names, recon_items, indicators_by_cp, mgmt, approvals, turnover, end, as_of)

    # 6. candidates: resolutions that need a human before anything is evaluated on them
    candidates = [m.model_dump() for m in matches.values() if m.method == "candidate"]

    return {
        "run": {"data_dir": os.path.abspath(data_dir), "period": [start.isoformat(), end.isoformat()], "rule_as_of": rule_as_of,
                "extractor": extractor.name, "resolver_thresholds": {"tau_high": TAU_HIGH, "tau_low": TAU_LOW},
                "clauses_in_force": [c.id + "@" + (c.valid_from.isoformat() if c.valid_from else "") for c in clauses_in_force(start, end, as_of)],
                "clauses_not_evaluated": HUMAN_ONLY_CLAUSES, "consolidated_turnover_cr": turnover,
                "graph": {"nodes": len(g.nodes), "edges": len(g.edges)}},
        "node_labels": {nid: _label(n) for nid, n in g.nodes.items()},
        "queue": [q.model_dump(mode="json") for q in queue],
        "unresolved": unresolved,
        "related_universe_not_in_ledger": universe,
        "resolution_candidates": candidates,
        "coverage": coverage,
        "extraction": extraction_log,
        "matches": {k: v.model_dump() for k, v in matches.items()},
        "counterparties_screened": len(vendor_master["counterparties"]),
    }
