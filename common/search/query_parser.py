"""Conservative English constraints with explicit ambiguity instead of guessed filters."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedQuery:
    text: str
    filter: dict | None
    warnings: tuple[str, ...] = ()


def combine(*expressions: dict | None) -> dict | None:
    clauses = [value for value in expressions if value is not None]
    return (
        {"op": "and", "clauses": clauses} if len(clauses) > 1 else clauses[0] if clauses else None
    )


def parse_query(text: str) -> ParsedQuery:
    if not text.strip():
        raise ValueError("Enter a nonempty query")
    # Negation and alternatives need a richer grammar. Never interpret a fragment of them.
    if re.search(
        r"\b(or|except|between)\b|\bnot\s+(?:under|below|at most|up to|in\s+(?:stock|(?:the\s+)?(?:north|south|east|west)))\b",
        text,
        re.I,
    ):
        return ParsedQuery(text, None, ("Ambiguous constraint: use the explicit filter controls.",))
    patterns = [
        (r"\b(under|below|at most|up to)\s*\$?\s*(\d+(?:\.\d{1,2})?)(?![\d.])\b", "price"),
        (r"\bin stock\b", "stock"),
        (r"\bin (?:the )?(north|south|east|west)(?: region)?\b", "region"),
    ]
    clauses = []
    remaining = text
    for pattern, field in patterns:
        for match in re.finditer(pattern, text, re.I):
            if field == "price":
                op = "lte" if match[1].lower() in {"at most", "up to"} else "lt"
                value = float(match[2])
            elif field == "stock":
                op, value = "gt", 0
            else:
                op, value = "eq", match[1].lower()
            clauses.append({"op": op, "field": field, "value": value})
        remaining = re.sub(pattern, " ", remaining, flags=re.I)
    warnings = ()
    if re.search(r"\b(over|above|cheap|expensive|near|under|below)\b|\$", remaining, re.I):
        warnings = ("Some constraints were not understood. Check the applied filters.",)
    cleaned = re.sub(r"\s+", " ", remaining.replace(",", " ")).strip()
    return ParsedQuery(cleaned, combine(*clauses), warnings)
