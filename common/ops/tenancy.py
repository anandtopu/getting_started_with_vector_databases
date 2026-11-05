"""Trusted tenant boundaries precede all client-supplied conditions."""

from common.search.query_parser import combine


def tenant_filter(principal, expression=None):
    if not principal.tenant:
        raise PermissionError("A trusted tenant identity is required")
    return combine({"op": "eq", "field": "seller_id", "value": principal.tenant}, expression)


def owned(record, principal):
    if record is None or record.metadata.get("seller_id") != principal.tenant:
        # Missing and foreign IDs are intentionally indistinguishable.
        raise KeyError("Listing unavailable")
    return record
