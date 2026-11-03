"""Canonicalisation of Indian corporate names and addresses.

Deterministic string normalisation only. No matching happens here.
"""
from __future__ import annotations

import re

_SUFFIX_MAP = [
    (r"\bpvt\.?\b", "private"),
    (r"\(p\)", "private"),
    (r"\bltd\.?\b", "limited"),
    (r"\bllp\.?\b", "llp"),
    (r"\bco\.?\b", "company"),
    (r"\bcorpn\.?\b", "corporation"),
    (r"\binds?\.?\b", "industries"),
    (r"\bindustries\b", "industries"),
]

_PUNCT = re.compile(r"[^\w\s]")
_WS = re.compile(r"\s+")
_GSTIN = re.compile(r"^\d{2}([A-Z]{5}\d{4}[A-Z])[1-9A-Z]Z[0-9A-Z]$")


def canon_name(name: str) -> str:
    s = name.lower()
    for pat, rep in _SUFFIX_MAP:
        s = re.sub(pat, rep, s)
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s


def canon_address(addr: str) -> str:
    s = addr.lower()
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s


def pan_from_gstin(gstin: str | None) -> str | None:
    """Characters 3-12 of a GSTIN are the holder's PAN."""
    if not gstin:
        return None
    m = _GSTIN.match(gstin.strip().upper())
    if not m:
        return None
    return m.group(1)
