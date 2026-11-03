"""Adapters from source documents to graph nodes and edges, each with provenance."""
from __future__ import annotations

from datetime import date

from .canon import canon_address, canon_name
from .extractor import ExtractionResult
from .graph import RPGraph
from .models import LLM_EDGE_CONFIDENCE, Edge, Node, Provenance


def _d(s):
    return date.fromisoformat(s) if s else None


def _prov(source_id, source_type, retrieved, locator):
    return Provenance(source_id=source_id, source_type=source_type, retrieved_at=_d(retrieved), locator=locator)


def address_node_id(addr: str) -> str:
    return "ADDR:" + canon_address(addr)


def ingest_registry(g: RPGraph, registry: dict, company_id: str = "E0"):
    retrieved = None
    for rec in registry["entities"]:
        retrieved = rec["retrieved_at"]
        ids = {k: v for k, v in {"cin": rec.get("cin"), "llpin": rec.get("llpin"), "pan": rec.get("pan")}.items() if v}
        # An LLP is treated as a "firm" for s.2(76)(iii). This is an interpretive choice:
        # the Act's text says "firm"; whether an LLP falls under (iii) is contested in
        # practice. Recorded on the node so the reviewer sees it.
        kind = "firm" if rec.get("kind") in ("firm", "proprietorship", "llp") else "entity"
        g.add_node(Node(id=rec["entity_id"], kind=kind, names=[rec["name"]] + list(rec.get("aliases", [])), identifiers=ids,
                        attrs={"incorporated_on": rec.get("incorporated_on"), "paid_up_capital_cr": rec.get("paid_up_capital_cr"),
                               "is_public": rec.get("is_public"), "entity_kind": rec.get("kind", "company"), "address": rec["registered_address"],
                               "interpretation": "LLP treated as firm for 2(76)(iii); contested" if rec.get("kind") == "llp" else None},
                        provenance=[_prov(rec["source"], "registry", retrieved, "master_data")]))
        addr = rec.get("registered_address")
        if addr and "not retrieved" not in addr.lower():
            aid = address_node_id(addr)
            g.add_node(Node(id=aid, kind="address", names=[addr]))
            g.add_edge(Edge(src=rec["entity_id"], dst=aid, type="REGISTERED_AT", origin="registry",
                            provenance=[_prov(rec["source"], "registry", retrieved, "master_data:registered_address")]))
        for dr in rec["directors"]:
            pid = registry["people_dins"].get(dr["din"], {}).get("person_id") or f"DIN:{dr['din']}"
            g.add_node(Node(id=pid, kind="person", names=[dr["name"]], identifiers={"din": dr["din"]},
                            provenance=[_prov(rec["source"], "registry", retrieved, "signatory_details")]))
            etype = "PARTNER_OF" if "partner" in str(dr.get("designation", "")).lower() else "DIRECTOR_OF"
            g.add_edge(Edge(src=pid, dst=rec["entity_id"], type=etype, valid_from=_d(dr["from"]), valid_to=_d(dr.get("to")),
                            origin="registry", attrs={"designation": dr["designation"]},
                            provenance=[_prov(rec["source"], "registry", retrieved, f"signatory_details:din={dr['din']}")]))
        sh = rec.get("shareholders_filing")
        if sh:
            for h in sh["holders"]:
                if h["holder"] in g.nodes:
                    g.add_edge(Edge(src=h["holder"], dst=rec["entity_id"], type="SHAREHOLDER_OF", origin="filing",
                                    attrs={"pct": h["pct"], "basis": "direct"},
                                    provenance=[_prov(sh["source"], "filing", retrieved, f"MGT-7:holder={h['holder']}")]))
                    g.add_edge(Edge(src=h["holder"], dst=rec["entity_id"], type="MEMBER_OF", origin="filing",
                                    attrs={"pct": h["pct"]},
                                    provenance=[_prov(sh["source"], "filing", retrieved, f"MGT-7:holder={h['holder']}")]))
    for k in registry.get("kmp", []):
        g.add_node(Node(id=k["person_id"], kind="person", names=[k["name"]],
                        provenance=[_prov(k["source"], "filing", retrieved, "board_report:kmp")]))
        g.add_edge(Edge(src=k["person_id"], dst=company_id, type="KMP_OF", valid_from=_d(k["from"]), valid_to=_d(k.get("to")), origin="filing",
                        attrs={"designation": k["designation"]}, provenance=[_prov(k["source"], "filing", retrieved, "board_report:kmp")]))


def ingest_shareholding(g: RPGraph, sh: dict):
    """Quarterly shareholding pattern -> SHAREHOLDER_OF (per quarter window) and PROMOTER_GROUP_OF."""
    company = sh["company_id"]
    by_holder = {}
    for r in sh["rows"]:
        if not r["holder_id"]:
            continue
        by_holder.setdefault(r["holder_id"], []).append(r)
    latest_quarter = max(r["quarter_end"] for r in sh["rows"])
    for hid, rows in by_holder.items():
        rows.sort(key=_by_quarter)
        if hid not in g.nodes:
            g.add_node(Node(id=hid, kind="entity", names=[rows[0]["holder"]], provenance=[_prov(sh["source"], "filing", sh["retrieved_at"], "reg31")]))
        # Coalesce consecutive quarters with identical (pct, category) into one window.
        # A quarterly filing states the position at quarter end; the run from the first
        # such quarter to the last is treated as continuous. If the run reaches the latest
        # filed quarter the window is left open, since no later filing contradicts it.
        runs = []
        for r in rows:
            q_end = _d(r["quarter_end"])
            q_start = date(q_end.year, q_end.month - 2, 1) if q_end.month > 2 else date(q_end.year - 1, q_end.month + 10, 1)
            key = (r["pct"], r["category"])
            if runs and runs[-1]["key"] == key and runs[-1]["end"] == _prev_quarter_end(q_start):
                runs[-1]["end"] = q_end
                runs[-1]["quarters"].append(r["quarter_end"])
            else:
                runs.append({"key": key, "start": q_start, "end": q_end, "quarters": [r["quarter_end"]], "holder": r["holder"]})
        for run in runs:
            pct, cat = run["key"]
            open_ended = run["quarters"][-1] == latest_quarter
            vt = None if open_ended else run["end"]
            loc = f"reg31:quarters={run['quarters'][0]}..{run['quarters'][-1]}:holder={run['holder']}"
            g.add_edge(Edge(src=hid, dst=company, type="SHAREHOLDER_OF", valid_from=run["start"], valid_to=vt, origin="filing",
                            attrs={"pct": pct, "basis": "direct", "category": cat, "quarters": run["quarters"]},
                            provenance=[_prov(sh["source"], "filing", sh["retrieved_at"], loc)]))
            if cat == "promoter_group":
                g.add_edge(Edge(src=hid, dst=company, type="PROMOTER_GROUP_OF", valid_from=run["start"], valid_to=vt, origin="filing",
                                attrs={"quarters": run["quarters"]},
                                provenance=[_prov(sh["source"], "filing", sh["retrieved_at"], loc + ":category=promoter_group")]))


def _prev_quarter_end(q_start: date) -> date:
    from datetime import timedelta
    return q_start - timedelta(days=1)


def _by_quarter(r):
    return r["quarter_end"]


def ingest_group(g: RPGraph, grp: dict):
    for s in grp["subsidiaries"]:
        if s["entity_id"] not in g.nodes:
            g.add_node(Node(id=s["entity_id"], kind="entity", names=[s["name"]]))
        g.add_edge(Edge(src=s["entity_id"], dst=grp["company_id"], type="SUBSIDIARY_OF", valid_from=_d(s.get("since")), origin="filing",
                        attrs={"pct": s["pct"]}, provenance=[_prov(grp["source"], "filing", grp["retrieved_at"], f"AOC-1:{s['name']}")]))
    for a in grp.get("associates", []):
        if a["entity_id"] not in g.nodes:
            g.add_node(Node(id=a["entity_id"], kind="entity", names=[a["name"]]))
        g.add_edge(Edge(src=a["entity_id"], dst=grp["company_id"], type="ASSOCIATE_OF", valid_from=_d(a.get("since")), origin="filing",
                        attrs={"pct": a["pct"]}, provenance=[_prov(grp["source"], "filing", grp["retrieved_at"], f"AOC-1:{a['name']}")]))


def _find_or_create_by_name(g: RPGraph, name: str, kind_hint: str, prov: Provenance) -> str:
    c = canon_name(name)
    existing = g.find_by_canonical_name(c, canon_name)
    if existing is not None:
        return existing.id
    nid = f"{kind_hint.upper()}:{c.replace(' ', '_')}"
    g.add_node(Node(id=nid, kind=kind_hint, names=[name], provenance=[prov]))
    return nid


SELF_REFERENCES = {"the company", "company", "this company", "the listed entity", "the listed company"}


def ingest_extracted(g: RPGraph, results: list[ExtractionResult], doc_source: str, doc_date: str, declarant_ids: dict, company_id: str = "E0"):
    """Turn validated extractor output into graph edges with origin=llm and fixed confidence.

    declarant_ids maps declarant display names to known person node ids so the
    declarant's own node is reused rather than duplicated. "the Company" and similar
    self-references in a declaration resolve to the declaring company's node (found by a
    real-model run: the stub never produced them, so no junk node was ever created).
    """
    for res in results:
        for rec in res.accepted:
            if canon_name(rec.to_name) in SELF_REFERENCES:
                rec = rec.model_copy(update={"to_name": g.nodes[company_id].names[0]})
            prov = Provenance(source_id=f"{doc_source}:{res.doc_id}", source_type="llm", retrieved_at=_d(doc_date),
                              locator=f"extractor={res.backend};span=\"{rec.source_span}\"")
            if rec.edge_type == "RELATIVE_OF":
                src = declarant_ids.get(rec.from_name) or _find_or_create_by_name(g, rec.from_name, "person", prov)
                dst = declarant_ids.get(rec.to_name) or _find_or_create_by_name(g, rec.to_name, "person", prov)
                g.add_edge(Edge(src=src, dst=dst, type="RELATIVE_OF", confidence=LLM_EDGE_CONFIDENCE["RELATIVE_OF"], origin="llm",
                                attrs={"kind": rec.kind}, provenance=[prov]))
                continue
            src = declarant_ids.get(rec.from_name) or _find_or_create_by_name(g, rec.from_name, "person", prov)
            is_firm = rec.edge_type == "PARTNER_OF"
            dst = _find_or_create_by_name(g, rec.to_name, "firm" if is_firm else "entity", prov)
            etype = rec.edge_type
            # A shareholder of a company is a member of it (s.2(55)). Extractors use either word;
            # the rulebook tests MEMBER_OF for 2(76)(iv), so normalise here.
            if etype == "SHAREHOLDER_OF":
                etype = "MEMBER_OF"
            g.add_edge(Edge(src=src, dst=dst, type=etype, confidence=LLM_EDGE_CONFIDENCE[rec.edge_type], origin="llm", provenance=[prov]))
