from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


SourceType = Literal["registry", "filing", "ledger", "books", "llm", "human"]
NodeKind = Literal["person", "entity", "firm", "address"]
EdgeType = Literal[
    "DIRECTOR_OF",
    "KMP_OF",
    "PARTNER_OF",
    "MEMBER_OF",
    "SHAREHOLDER_OF",
    "RELATIVE_OF",
    "REGISTERED_AT",
    "SUBSIDIARY_OF",
    "ASSOCIATE_OF",
    "PROMOTER_GROUP_OF",
    "ACCUSTOMED_TO_ACT",
]

# Fixed confidence for edges proposed by the extractor, by edge type.
# Model self-reported probabilities are uncalibrated, so we do not use them.
LLM_EDGE_CONFIDENCE = {
    "RELATIVE_OF": 0.80,
    "PARTNER_OF": 0.75,
    "MEMBER_OF": 0.70,
    "DIRECTOR_OF": 0.70,
    "KMP_OF": 0.70,
    "SHAREHOLDER_OF": 0.65,
}


class Provenance(BaseModel):
    source_id: str
    source_type: SourceType
    retrieved_at: date
    locator: str  # filing id + field, doc + page + span, or ledger row id


class Node(BaseModel):
    id: str
    kind: NodeKind
    names: list[str]
    identifiers: dict[str, str] = Field(default_factory=dict)  # din, pan, cin, llpin, gstin
    attrs: dict = Field(default_factory=dict)  # incorporated_on, paid_up_capital, is_public, ...
    provenance: list[Provenance] = Field(default_factory=list)


class Edge(BaseModel):
    src: str
    dst: str
    type: EdgeType
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    confidence: float = 1.0
    origin: SourceType
    attrs: dict = Field(default_factory=dict)  # pct, basis, kind
    provenance: list[Provenance] = Field(default_factory=list)


class MatchRecord(BaseModel):
    ledger_name: str
    ledger_id: str
    node_id: Optional[str]
    method: Literal["identifier", "exact_name", "fuzzy", "candidate", "none"]
    score: float
    evidence: str


class ExtractedEdge(BaseModel):
    from_name: str
    to_name: str
    edge_type: EdgeType
    kind: Optional[str] = None
    source_span: str


class RuleHit(BaseModel):
    counterparty_id: str
    clause_id: str
    rule_version: str
    path: list[dict]
    min_confidence: float
    weakest_origin: SourceType
    relationship_window: tuple[Optional[date], Optional[date]]


class Transaction(BaseModel):
    row_id: str
    date: date
    counterparty_id: str
    counterparty_name: str
    kind: Literal["purchase", "sale", "loan_given", "loan_taken", "advance", "grn", "rent", "service", "receipt"]
    amount: float


class QueueItem(BaseModel):
    counterparty_id: str
    counterparty_name: str
    item_type: Literal["rule_hit", "reconciliation", "indicator"]
    evidence_tier: int
    materiality_tier: int
    min_confidence: float
    gross_value: float
    detail: dict
    sort_key: tuple
