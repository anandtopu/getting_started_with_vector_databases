"""A small validated filter language; missing fields never satisfy a comparison."""

import math
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Filter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    op: Literal["eq", "in", "lt", "lte", "gt", "gte", "and", "or"]
    field: str | None = None
    value: Any = None
    clauses: tuple["Filter", ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def validate_expression(self) -> "Filter":
        if self.op in {"and", "or"}:
            if not self.clauses or self.field is not None or self.value is not None:
                raise ValueError("AND/OR require nonempty clauses and no field/value.")
        else:
            if not self.field or self.clauses:
                raise ValueError("Comparisons require a field and no clauses.")
            if self.op == "in" and not isinstance(self.value, (list, tuple)):
                raise ValueError("IN requires a list of values.")
            values = self.value if self.op == "in" else [self.value]
            if any(type(value) not in {str, int, float, bool, type(None)} for value in values):
                raise ValueError("Comparison values must be JSON scalars.")
            if any(isinstance(value, float) and not math.isfinite(value) for value in values):
                raise ValueError("Comparison numbers must be finite.")
            if self.op in {"lt", "lte", "gt", "gte"} and (
                not isinstance(self.value, (int, float)) or isinstance(self.value, bool)
            ):
                raise ValueError("Range comparisons require a numeric value.")
        return self


def parse_filter(expression: Filter | dict | None) -> Filter | None:
    return Filter.model_validate(expression) if expression is not None else None


def matches(metadata: dict, expression: Filter | None) -> bool:
    if expression is None:
        return True
    if expression.op == "and":
        return all(matches(metadata, child) for child in expression.clauses)
    if expression.op == "or":
        return any(matches(metadata, child) for child in expression.clauses)
    if expression.field not in metadata:
        return False
    actual = metadata[expression.field]
    expected = expression.value
    if expression.op == "eq":
        return type(actual) is type(expected) and actual == expected
    if expression.op == "in":
        return any(type(actual) is type(value) and actual == value for value in expected)
    if isinstance(actual, bool) or not isinstance(actual, (int, float)):
        return False
    return {
        "lt": actual < expected,
        "lte": actual <= expected,
        "gt": actual > expected,
        "gte": actual >= expected,
    }[expression.op]
