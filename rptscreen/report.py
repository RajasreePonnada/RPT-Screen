"""Evidence pack (JSON) and a human-readable markdown report."""
from __future__ import annotations

import json
import os

TIER_LABEL = {0: "registry-backed rule hit", 1: "filing/books-backed rule hit", 2: "rule hit via fuzzy name merge",
              3: "rule hit via extractor-proposed edge", 4: "reconciliation variance", 5: "indicator only"}
MAT_LABEL = {0: "material (Reg 23)", 1: ">=10% of threshold", 2: "below"}


def write_evidence_pack(result: dict, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "evidence_pack.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)


def _path_str(path, labels=None):
    labels = labels or {}
    parts = []
    for e in path:
        w = ""
        if e.get("valid_from") or e.get("valid_to"):
            w = f" [{e.get('valid_from') or '…'} → {e.get('valid_to') or 'open'}]"
        extra = ""
        if e.get("attrs", {}).get("pct") is not None:
            extra = f" {e['attrs']['pct']}%"
        if e.get("attrs", {}).get("kind"):
            extra = f" ({e['attrs']['kind']})"
        src = labels.get(e["src"], e["src"])
        dst = labels.get(e["dst"], e["dst"])
        parts.append(f"{src} —{e['type']}{extra}→ {dst}{w}  [{e['origin']}, conf {e['confidence']}]")
    return "\n    then ".join(parts)


def _procedure(q) -> str:
    d = q["detail"]
    if q["item_type"] == "rule_hit":
        steps = []
        if not d["disclosed_by_management"]:
            steps.append("put to management under SA 550 para 22 (previously unidentified related party); obtain written explanation")
        if d["approvals"]["audit_committee"] != "ok":
            steps.append("no audit committee approval on record — test Reg 23(2) / s.188 compliance")
        if d["approvals"]["shareholder"] == "missing":
            steps.append("material RPT without shareholder approval — Reg 23(4)")
        if d["transactions_outside_window"]:
            steps.append("transactions outside the relationship window: confirm they are not RPTs for that part of the period")
        if d["weakest_origin"] == "llm":
            steps.append("relationship rests on a declaration read by the extractor — verify the quoted span against the original form")
        if d["resolution"]["method"] in ("fuzzy", "candidate"):
            steps.append("identity rests on a name match — obtain the counterparty's PAN/CIN from the vendor master or an invoice")
        steps.append("obtain external confirmation of balances and terms; evaluate arm's length and disclosure in the Ind AS 24 note")
        return "; ".join(steps)
    if q["item_type"] == "reconciliation":
        return "obtain the schedule behind the disclosed figure; Ind AS 24 para 18 requires gross amounts, not net or peak balances; reconcile to the ledger rows listed"
    sig = {s_["indicator"] for s_ in d["signals"]}
    steps = []
    if "a" in sig:
        steps.append("ask management whether the counterparty is connected to the promoter group; consider whether the transaction's purpose and effect is to benefit a related party (Reg 2(1)(zc))")
    if "b" in sig:
        steps.append("vendor due diligence: business rationale for a new, thinly capitalised supplier at this volume")
    if "c" in sig or "c2" in sig:
        steps.append("trace the advance to delivery: GRNs, contracts, bank statement; consider whether the advance is in substance a loan")
    if "b2" in sig:
        steps.append("counterparty's paid-up capital is tiny relative to what it was paid — obtain its financials; consider whether it is a pass-through")
    if "d" in sig:
        steps.append("money went out and most came back — obtain the commercial rationale for each leg; consider round-tripping and whether the net is a loan")
    return "; ".join(steps)


def _summary(result: dict) -> list[str]:
    q = result["queue"]
    hits = [x for x in q if x["item_type"] == "rule_hit"]
    undisclosed = [x for x in hits if not x["detail"]["disclosed_by_management"]]
    undisclosed_cps = sorted({x["counterparty_name"] for x in undisclosed})
    strong = [x for x in undisclosed if x["evidence_tier"] <= 1]
    no_ac = sorted({x["counterparty_name"] for x in hits if x["detail"]["approvals"]["audit_committee"] != "ok"})
    material = sorted({x["counterparty_name"] for x in hits if x["materiality_tier"] == 0})
    recon = [x for x in q if x["item_type"] == "reconciliation"]
    ind = [x for x in q if x["item_type"] == "indicator"]
    out = []
    out.append(f"- {len(undisclosed_cps)} counterparties not on management's related-party list meet a legal definition on the evidence here "
               f"({len({x['counterparty_name'] for x in strong})} on registry/filing-backed paths): {', '.join(undisclosed_cps) or 'none'}")
    out.append(f"- {len(no_ac)} related counterparties have no audit committee approval on record: {', '.join(no_ac) or 'none'}")
    out.append(f"- {len(material)} counterparties crossed the Reg 23 materiality threshold: {', '.join(material) or 'none'}")
    out.append(f"- {len(recon)} disclosed figures do not reconcile to the ledger" + (": " + ", ".join(x["counterparty_name"] for x in recon) if recon else ""))
    out.append(f"- {len(ind)} counterparties carry vendor risk indicators only (no legal definition met)")
    out.append(f"- {len(result['unresolved'])} counterparties could not be matched to any public record and were not screened")
    out.append("- Every item above is evidence for the engagement team's judgment under SA 550; none is a determination.")
    return out


def render_markdown(result: dict) -> str:
    r = result["run"]
    labels = result.get("node_labels", {})
    lines = []
    lines.append("# Related-party screening — evidence queue\n")
    lines.append(f"Period {r['period'][0]} to {r['period'][1]} · rules as of {r['rule_as_of'] or 'period'} · extractor `{r['extractor']}` · "
                 f"resolver τ_high={r['resolver_thresholds']['tau_high']} τ_low={r['resolver_thresholds']['tau_low']} · graph {r['graph']['nodes']} nodes / {r['graph']['edges']} edges\n")
    lines.append(f"Counterparties screened: {result['counterparties_screened']} · queue items: {len(result['queue'])} · "
                 f"unresolved: {len(result['unresolved'])} · resolution candidates needing a human: {len(result['resolution_candidates'])}\n")
    lines.append("Clauses in force: " + ", ".join(r["clauses_in_force"]) + "\n")
    lines.append("Not evaluated (human judgment only): " + "; ".join(f"{c} — {t}" for c, t in r["clauses_not_evaluated"]) + "\n")

    lines.append("\n## Summary for the engagement partner\n")
    lines.extend(_summary(result))
    lines.append("\n## Ranked evidence queue\n")
    lines.append("Ordering: evidence tier → undisclosed before disclosed → materiality tier → gross value → min confidence. No item is a conclusion.\n")
    lines.append("| # | Counterparty | Item | Evidence tier | Materiality | Gross ₹cr | Min conf | Clause / signal | Mgmt list | Approvals |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for i, q in enumerate(result["queue"], 1):
        d = q["detail"]
        if q["item_type"] == "rule_hit":
            what = d["clause_id"]
            mg = "yes" if d["disclosed_by_management"] else "**no**"
            ap = f"AC {d['approvals']['audit_committee']}, SH {d['approvals']['shareholder']}"
        elif q["item_type"] == "reconciliation":
            what = f"variance ₹{d['variance_cr']} cr ({d['variance_pct']}%)"
            mg, ap = "yes", "—"
        else:
            what = ", ".join(sorted({s['indicator'] + ":" + s['signal'] for s in d["signals"]}))
            mg, ap = "—", "—"
        mat = MAT_LABEL[q["materiality_tier"]] if q["item_type"] == "rule_hit" else (
            "value ≥ Reg 23 threshold (if related)" if q["materiality_tier"] == 0 else MAT_LABEL[q["materiality_tier"]])
        lines.append(f"| {i} | {q['counterparty_name']} ({q['counterparty_id']}) | {q['item_type']} | {q['evidence_tier']} {TIER_LABEL[q['evidence_tier']]} | "
                     f"{mat} | {q['gross_value']} | {q['min_confidence']} | {what} | {mg} | {ap} |")

    lines.append("\n## Item detail\n")
    for i, q in enumerate(result["queue"], 1):
        d = q["detail"]
        lines.append(f"### {i}. {q['counterparty_name']} — {q['item_type']}")
        if q["item_type"] == "rule_hit":
            lines.append(f"- Clause: `{d['clause_id']}` (version `{d['rule_version']}`), weakest origin: {d['weakest_origin']}")
            lines.append(f"- Path: {_path_str(d['path'], labels)}")
            for alt in d.get("alternate_paths", []):
                lines.append(f"- Corroborating path (tier {alt['evidence_tier']}, conf {alt['min_confidence']}): {_path_str(alt['path'], labels)}")
            lines.append(f"- Suggested procedure: {_procedure(q)}")
            lines.append(f"- Relationship window within period: {d['relationship_window'][0]} → {d['relationship_window'][1]}")
            if d["transactions_outside_window"]:
                lines.append(f"- Transactions outside the relationship window: {', '.join(d['transactions_outside_window'])}")
            lines.append(f"- Resolution: {d['resolution']['method']} — {d['resolution']['evidence']}")
            m = d["materiality"]
            if m["crossed"]:
                lines.append(f"- Materiality: crossed on {m['crossed']['date']} (cumulative ₹{m['crossed']['cumulative_cr']} cr > ₹{m['crossed']['threshold_cr']} cr; {m['crossed']['basis']}); "
                             f"threshold at period end ₹{m['threshold_at_period_end_cr']} cr ({m['basis_at_period_end']})")
            elif m["gross_cr"] == 0:
                lines.append("- Materiality: no transactions with this counterparty in the ledger provided (relationship exists; transactions, if any, may be routed elsewhere)")
            else:
                lines.append(f"- Materiality: gross ₹{m['gross_cr']} cr, below ₹{m['threshold_at_period_end_cr']} cr ({m['basis_at_period_end']})")
            lines.append(f"- Approvals: {d['approvals']}")
            lines.append(f"- On management's related-party list: {d['disclosed_by_management']}")
            for e in d["path"]:
                for p in e["provenance"]:
                    lines.append(f"  - source: {p['source_id']} · {p['locator']} · retrieved {p['retrieved_at']}")
        elif q["item_type"] == "reconciliation":
            lines.append(f"- {d['category']} / {d['transaction_type']}: disclosed ₹{d['disclosed_cr']} cr vs ledger gross ₹{d['ledger_gross_cr']} cr → variance ₹{d['variance_cr']} cr ({d['variance_pct']}%)")
            lines.append(f"- Ledger rows: {', '.join(d['rows'])} · note source: {d['source']}")
            lines.append(f"- {d['note']}")
            lines.append(f"- Suggested procedure: {_procedure(q)}")
        else:
            for s in d["signals"]:
                lines.append(f"- ({s['indicator']}) {s['signal']}: {s['value']}" + (f" — with {s['with_name']}" if s.get("with_name") else ""))
            lines.append(f"- Resolution: {d['resolution']['method']} — {d['resolution']['evidence']}")
            lines.append("- These are reasons to look, not relationships. No clause fired.")
            lines.append(f"- Suggested procedure: {_procedure(q)}")
        lines.append("")

    lines.append("\n## Unresolved counterparties (absence of evidence, not a finding)\n")
    if not result["unresolved"]:
        lines.append("None.")
    for u in result["unresolved"]:
        lines.append(f"- {u['name']} ({u['ledger_id']}), gross ₹{u['gross_cr']} cr — {u['evidence']}")

    uni = result.get("related_universe_not_in_ledger", [])
    lines.append("\n## Registry-derived related entities with no recorded transactions\n")
    lines.append("Entities connected to the company's directors/KMP in public records that are not in the vendor master. "
                 "Counterparty screening cannot see these; search payments and bank statements for them.\n")
    if not uni:
        lines.append("None.")
    for u in uni:
        w = f" [{u['valid_from'] or '…'} → {u['valid_to'] or 'open'}]"
        lines.append(f"- {u['entity']} — via {u['via_person']} ({u['edge']}, {u['origin']}){w}")

    if result["resolution_candidates"]:
        lines.append("\n## Resolution candidates (human must confirm identity before evaluation)\n")
        for c in result["resolution_candidates"]:
            lines.append(f"- {c['ledger_name']} ({c['ledger_id']}) → {c['node_id']} : {c['evidence']}")

    lines.append("\n## Coverage gaps\n")
    lines.append("Clauses that could not be evaluated for lack of data, so a non-hit is not a clearance.\n")
    gap_counts: dict[str, list[str]] = {}
    for lid, gaps in result["coverage"].items():
        for x in gaps:
            if "human judgment" in x:
                continue
            gap_counts.setdefault(x, []).append(lid)
    n_resolved = len(result["coverage"])
    for gap, lids in sorted(gap_counts.items(), key=_by_len_desc):
        lines.append(f"- {len(lids)} of {n_resolved} resolved counterparties — {gap}")
        if len(lids) <= 6:
            lines.append(f"  - {', '.join(lids)}")
    if not gap_counts:
        lines.append("None.")

    lines.append("\n## Extraction log\n")
    for e in result["extraction"]:
        lines.append(f"- {e['doc']} ({e['backend']}): {len(e['accepted'])} accepted, {len(e['rejected'])} rejected")
        for a in e["accepted"]:
            lines.append(f"  - {a['from_name']} -{a['edge_type']}{'(' + a['kind'] + ')' if a.get('kind') else ''}→ {a['to_name']} · span: “{a['source_span']}”")
        for rj in e["rejected"]:
            lines.append(f"  - rejected: {rj['reason']}")
    return "\n".join(lines) + "\n"


def _by_len_desc(kv):
    return -len(kv[1])


def write_markdown(result: dict, out_dir: str, name: str = "report.md"):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, name), "w") as f:
        f.write(render_markdown(result))
