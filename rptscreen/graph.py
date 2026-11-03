"""Temporal, provenance-carrying relationship graph.

Every edge has a validity window and provenance. All queries are "as of" a
period: an edge counts only if its window overlaps the period. ACCUSTOMED_TO_ACT
edges may only be created with origin "human".
"""
from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

import networkx as nx

from .models import Edge, Node

MIN_DATE = date(1900, 1, 1)
MAX_DATE = date(2999, 12, 31)


def overlaps(vf: Optional[date], vt: Optional[date], start: date, end: date) -> bool:
    a = vf or MIN_DATE
    b = vt or MAX_DATE
    return a <= end and b >= start


def window_intersection(windows: Iterable[tuple[Optional[date], Optional[date]]], start: date, end: date):
    lo, hi = start, end
    for vf, vt in windows:
        lo = max(lo, vf or MIN_DATE)
        hi = min(hi, vt or MAX_DATE)
    if lo > hi:
        return None
    return (lo, hi)


class RPGraph:
    def __init__(self):
        self.g = nx.MultiDiGraph()
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(self, node: Node):
        if node.id in self.nodes:
            existing = self.nodes[node.id]
            for nm in node.names:
                if nm not in existing.names:
                    existing.names.append(nm)
            existing.identifiers.update({k: v for k, v in node.identifiers.items() if v})
            existing.attrs.update(node.attrs)
            existing.provenance.extend(node.provenance)
            return
        self.nodes[node.id] = node
        self.g.add_node(node.id)

    def add_edge(self, edge: Edge):
        if edge.type == "ACCUSTOMED_TO_ACT" and edge.origin != "human":
            raise ValueError("ACCUSTOMED_TO_ACT may only be asserted by a human reviewer")
        if edge.src not in self.nodes or edge.dst not in self.nodes:
            raise KeyError(f"edge references unknown node: {edge.src} -> {edge.dst}")
        self.edges.append(edge)
        self.g.add_edge(edge.src, edge.dst, key=len(self.edges) - 1)

    def out_edges(self, node_id: str, etype: str, start: date, end: date) -> list[Edge]:
        res = []
        for _, _, key in self.g.out_edges(node_id, keys=True):
            e = self.edges[key]
            if e.type == etype and overlaps(e.valid_from, e.valid_to, start, end):
                res.append(e)
        return res

    def in_edges(self, node_id: str, etype: str, start: date, end: date) -> list[Edge]:
        res = []
        for _, _, key in self.g.in_edges(node_id, keys=True):
            e = self.edges[key]
            if e.type == etype and overlaps(e.valid_from, e.valid_to, start, end):
                res.append(e)
        return res

    def undirected_edges(self, node_id: str, etype: str, start: date, end: date) -> list[Edge]:
        return self.out_edges(node_id, etype, start, end) + self.in_edges(node_id, etype, start, end)

    def node_list(self) -> list[Node]:
        return list(self.nodes.values())

    def find_by_identifier(self, key: str, value: str) -> Optional[Node]:
        v = value.upper()
        for n in self.nodes.values():
            if n.identifiers.get(key, "").upper() == v:
                return n
        return None

    def find_by_canonical_name(self, canon: str, canon_fn) -> Optional[Node]:
        for n in self.nodes.values():
            for nm in n.names:
                if canon_fn(nm) == canon:
                    return n
        return None


def edge_to_path_item(e: Edge) -> dict:
    return {
        "src": e.src, "dst": e.dst, "type": e.type,
        "valid_from": e.valid_from.isoformat() if e.valid_from else None,
        "valid_to": e.valid_to.isoformat() if e.valid_to else None,
        "confidence": e.confidence, "origin": e.origin, "attrs": e.attrs,
        "provenance": [p.model_dump(mode="json") for p in e.provenance],
    }
