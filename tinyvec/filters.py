"""Equality postings narrow the rows examined by more complex metadata predicates."""

from collections import defaultdict

from common.stores.filters import matches


class MetadataIndex:
    def __init__(self, records):
        self.rows = records
        self.postings = defaultdict(set)
        for i, r in enumerate(records):
            for key, value in r.metadata.items():
                if type(value) in (int, str, float, bool, type(None)):
                    self.postings[(key, type(value), value)].add(i)

    def eligible(self, expr):
        if expr.op == "eq":
            return self.postings.get((expr.field, type(expr.value), expr.value), set()).copy()
        if expr.op == "in":
            return set().union(
                *(self.postings.get((expr.field, type(v), v), set()) for v in expr.value)
            )
        if expr.op == "and":
            indexed = [c for c in expr.clauses if c.op in ("eq", "in")]
            if indexed:
                rows = set.intersection(*(self.eligible(c) for c in indexed))
                return {i for i in rows if matches(self.rows[i].metadata, expr)}
        return {i for i, r in enumerate(self.rows) if matches(r.metadata, expr)}
