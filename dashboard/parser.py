import re
from typing import List, Tuple

_number_pattern = re.compile(
    r"(?P<year>20\d{2}|19\d{2})[^\d]{0,20}(?P<value>[\d,]+(?:\.\d+)?)\s*(?P<unit>trillion|trn|billion|bn|million|mn|crore|lakh|cr|₹|rs|usd|$)",
    re.IGNORECASE,
)

_unit_multipliers = {
    "trillion": 1_000_000,
    "trn": 1_000_000,
    "billion": 1_000,
    "bn": 1_000,
    "million": 1,
    "mn": 1,
    "crore": 10,
    "cr": 10,
    "lakh": 0.1,
    "₹": 0.012,  # rough INR crore to USD million depends but ignore
    "rs": 0.012,
    "usd": 1,
    "": 1,
}


def extract_year_value_pairs(text: str) -> List[Tuple[int, float]]:
    """Extract (year, value_million_usd) pairs from a block of text.

    Very heuristic. Converts common units to ~USD million using fixed multipliers.
    """
    pairs: List[Tuple[int, float]] = []
    for m in _number_pattern.finditer(text):
        year = int(m.group("year"))
        value_raw = m.group("value").replace(",", "")
        try:
            value = float(value_raw)
        except ValueError:
            continue
        unit = m.group("unit").lower()
        multiplier = _unit_multipliers.get(unit, 1)
        value_musd = value * multiplier  # treat as million USD equivalent
        pairs.append((year, value_musd))
    return pairs