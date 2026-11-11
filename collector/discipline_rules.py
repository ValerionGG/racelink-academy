"""Read-only discipline selection; keep parity with public/disciplines.js.

This metadata selector does not assert vehicle compatibility or change stored
classification. Specific disciplines use explicit title tokens only; existing
domain/category values supply motorsport/simracing respectively.
"""
from __future__ import annotations

import re
import unicodedata

DISCIPLINE_IDS = ("motorcycle", "karting", "drift", "motorsport", "simracing")
DISCIPLINE_BITS = {value: 1 << index for index, value in enumerate(DISCIPLINE_IDS)}
TITLE_TOKENS = {
    "motorcycle": frozenset("moto motos motocycle motocycles motocyclette motocyclettes "
        "motorcycle motorcycles motorcycling motorrad motorrader motocicleta motocicletas "
        "motocross supermoto superbike motogp".split()),
    "karting": frozenset("kart karts karting gokart gokarts".split()),
    "drift": frozenset("drift drifts drifting".split()),
}


def discipline_mask(title, domain_scope="", category=""):
    title = title if isinstance(title, str) else ""
    text = "".join(char for char in unicodedata.normalize("NFKD", title)
                   if not unicodedata.category(char).startswith("M")).lower()
    tokens = set(re.findall(r"[^\W_]+", text, re.UNICODE))
    result = sum(DISCIPLINE_BITS[key] for key, values in TITLE_TOKENS.items() if tokens & values)
    if domain_scope == "motorsport":
        result |= DISCIPLINE_BITS["motorsport"]
    if category == "simracing":
        result |= DISCIPLINE_BITS["simracing"]
    return result


def discipline_ids(record):
    record = record if isinstance(record, dict) else {}
    def field(full, compact):
        value = record.get(full)
        if isinstance(value, str):
            return value
        value = record.get(compact)
        return value if isinstance(value, str) else ""
    title = field("title", "t")
    domain = field("domain_scope", "d")
    category = field("category", "c")
    mask = discipline_mask(title, domain, category)
    return [key for key in DISCIPLINE_IDS if mask & DISCIPLINE_BITS[key]]
