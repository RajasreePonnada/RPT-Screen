"""Prose extraction: proposes relationship edges from unstructured text.

Two backends share one contract:
  extract(doc_id, text) -> list[ExtractedEdge]

Contract enforced on every output regardless of backend:
  - source_span must appear verbatim in the input text, else the record is dropped
  - edge_type must be one of the allowed types
  - the extractor is never asked whether something IS a related party
  - confidence is NOT taken from the model; a fixed table by edge type is used

Backends:
  StubExtractor       deterministic regex rules; runs offline; used for the test harness
  OpenRouterExtractor calls a free-tier model on OpenRouter; set OPENROUTER_API_KEY and
                      optionally RPT_MODEL. Not required to run the prototype.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field

from pydantic import ValidationError

from .models import ExtractedEdge

RELATIVE_KINDS = ["wife", "husband", "spouse", "brother", "sister", "daughter", "son", "father", "mother",
                  "son's wife", "daughter's husband", "step-father", "step-mother", "step-son", "step-daughter", "step-brother", "step-sister"]

SCHEMA_INSTRUCTION = (
    "You read a director's declaration of interest. Extract relationships as a JSON list. "
    "Each item: {\"from_name\": str, \"to_name\": str, \"edge_type\": one of "
    "[RELATIVE_OF, DIRECTOR_OF, PARTNER_OF, MEMBER_OF, SHAREHOLDER_OF, KMP_OF], "
    "\"kind\": relative kind if RELATIVE_OF else null, \"source_span\": the exact sentence or clause copied verbatim}. "
    "For RELATIVE_OF, from_name is the declarant and to_name is the relative. "
    "For DIRECTOR_OF / PARTNER_OF / MEMBER_OF / SHAREHOLDER_OF, from_name is the person and to_name is the entity or firm. "
    "Do not infer anything not stated. Do not decide whether anyone is a related party. "
    "If nothing is stated, return []. Output JSON only."
)


@dataclass
class ExtractionResult:
    doc_id: str
    accepted: list[ExtractedEdge] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)
    backend: str = ""


def validate_records(doc_id: str, text: str, raw: list[dict], backend: str) -> ExtractionResult:
    res = ExtractionResult(doc_id=doc_id, backend=backend)
    for r in raw:
        try:
            rec = ExtractedEdge(**r)
        except ValidationError as ex:
            res.rejected.append({"record": r, "reason": f"schema: {ex.errors()[0].get('msg')}"})
            continue
        if rec.source_span.strip() not in text:
            res.rejected.append({"record": r, "reason": "span not found verbatim in source"})
            continue
        if rec.edge_type == "RELATIVE_OF" and (rec.kind or "").lower() not in RELATIVE_KINDS:
            res.rejected.append({"record": r, "reason": f"relative kind '{rec.kind}' not in Rule 4 list"})
            continue
        res.accepted.append(rec)
    return res


class StubExtractor:
    """Regex rules covering the declaration phrasings used in the synthetic MBP-1 forms.

    This stands in for the LLM so the pipeline is reproducible offline. It is
    deliberately narrow: anything outside these patterns is not extracted.
    """
    name = "stub"

    _declarant = re.compile(r"I,\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),")
    _relative = re.compile(
        r"(My\s+(wife|husband|brother|sister|daughter|son|father|mother)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+a\s+(director|partner|shareholder)\s+(?:of|in)\s+(?:the\s+firm\s+)?([A-Z][A-Za-z&]*(?:\s+[A-Z][A-Za-z&]*)*?)(?=[\.,;]))")
    _self_dir = re.compile(r"(I am a director(?: and shareholder)? of\s+([A-Z][A-Za-z&]*(?:\s+[A-Z][A-Za-z&]*)*?)(?=[\.,;]| and hold))")
    _self_sh = re.compile(r"(I am a shareholder of\s+([A-Z][A-Za-z&]*(?:\s+[A-Z][A-Za-z&]*)*?)(?=[\.,;]| and hold))")
    _dirships = re.compile(r"(I hold directorships in the following bodies corporate:\s+([^\.]+)\.)")

    def extract(self, doc_id: str, text: str) -> ExtractionResult:
        raw = []
        m = self._declarant.search(text)
        declarant = m.group(1) if m else None
        for mm in self._relative.finditer(text):
            span, kind, rel_name, role, ent = mm.groups()
            if declarant:
                raw.append({"from_name": declarant, "to_name": rel_name, "edge_type": "RELATIVE_OF", "kind": kind, "source_span": span})
            etype = {"director": "DIRECTOR_OF", "partner": "PARTNER_OF", "shareholder": "MEMBER_OF"}[role]
            raw.append({"from_name": rel_name, "to_name": ent, "edge_type": etype, "kind": None, "source_span": span})
        for mm in self._self_dir.finditer(text):
            span, ent = mm.groups()
            if declarant:
                raw.append({"from_name": declarant, "to_name": ent, "edge_type": "DIRECTOR_OF", "kind": None, "source_span": span})
                if "shareholder" in span:
                    raw.append({"from_name": declarant, "to_name": ent, "edge_type": "MEMBER_OF", "kind": None, "source_span": span})
        for mm in self._self_sh.finditer(text):
            span, ent = mm.groups()
            if declarant:
                raw.append({"from_name": declarant, "to_name": ent, "edge_type": "MEMBER_OF", "kind": None, "source_span": span})
        for mm in self._dirships.finditer(text):
            span, lst = mm.groups()
            if declarant:
                for ent in re.split(r",\s*|\s+and\s+", lst):
                    raw.append({"from_name": declarant, "to_name": ent.strip(), "edge_type": "DIRECTOR_OF", "kind": None, "source_span": span})
        return validate_records(doc_id, text, raw, self.name)


class OpenRouterExtractor:
    """Free-tier models on OpenRouter are rate-limited per second and per day. Calls are
    paced (PAUSE_BETWEEN_CALLS) and 429s are retried with backoff honouring Retry-After.
    Default model: google/gemma-4-31b-it:free (the free list changes; set RPT_MODEL)."""
    name = "openrouter"
    PAUSE_BETWEEN_CALLS = 6.0
    MAX_RETRIES = 5

    def __init__(self, model: str | None = None, api_key: str | None = None):
        self.model = model or os.environ.get("RPT_MODEL", "google/gemma-4-31b-it:free")
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        self.name = f"openrouter:{self.model}"
        self._last_call = 0.0

    def _post(self, body: dict):
        import requests  # imported lazily so the stub path has no network dependency

        wait = max(0.0, self.PAUSE_BETWEEN_CALLS - (time.time() - self._last_call))
        if wait:
            time.sleep(wait)
        delay = 10.0
        for attempt in range(self.MAX_RETRIES):
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                         "HTTP-Referer": "https://github.com/RajasreePonnada/rpt-screen", "X-Title": "rpt-screen"},
                data=json.dumps(body), timeout=90,
            )
            self._last_call = time.time()
            if resp.status_code != 429:
                resp.raise_for_status()
                return resp
            detail = ""
            try:
                detail = resp.json().get("error", {}).get("message", "")
            except Exception:
                detail = resp.text[:200]
            if "per-day" in detail or "daily" in detail.lower():
                raise RuntimeError(f"OpenRouter free-tier daily quota exhausted for {self.model}: {detail}. "
                                   f"Try another :free model via RPT_MODEL, or tomorrow.")
            retry_after = resp.headers.get("Retry-After")
            sleep_for = float(retry_after) if retry_after and retry_after.replace(".", "", 1).isdigit() else delay
            print(f"  [openrouter] 429 on attempt {attempt + 1}: {detail or 'rate limited'}; sleeping {sleep_for:.0f}s")
            time.sleep(sleep_for)
            delay = min(delay * 2, 120.0)
        raise RuntimeError(f"OpenRouter still rate-limiting {self.model} after {self.MAX_RETRIES} retries")

    def extract(self, doc_id: str, text: str) -> ExtractionResult:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SCHEMA_INSTRUCTION},
                {"role": "user", "content": text},
            ],
            "temperature": 0,
        }
        resp = self._post(body)
        content = resp.json()["choices"][0]["message"]["content"]
        content = content.strip()
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content)
        try:
            raw = json.loads(content)
            if isinstance(raw, dict):
                raw = raw.get("items") or raw.get("relationships") or [raw]
        except json.JSONDecodeError:
            res = ExtractionResult(doc_id=doc_id, backend=self.name)
            res.rejected.append({"record": content[:500], "reason": "model output was not valid JSON"})
            return res
        return validate_records(doc_id, text, raw, self.name)


def make_extractor(kind: str):
    if kind == "stub":
        return StubExtractor()
    if kind == "openrouter":
        return OpenRouterExtractor()
    raise ValueError(f"unknown extractor '{kind}'")
