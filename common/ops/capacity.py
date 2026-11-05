"""Transparent capacity and cost assumptions, without fabricated vendor pricing."""

import math


def estimate(
    rows=10_000_000,
    dimensions=768,
    *,
    bytes_per_value=4,
    links=32,
    replicas=1,
    metadata_bytes=256,
    headroom=0.3,
):
    if (
        min(rows, dimensions, bytes_per_value, replicas) <= 0
        or links < 0
        or metadata_bytes < 0
        or not 0 <= headroom < 1
    ):
        raise ValueError("Invalid capacity assumptions")
    vectors = rows * dimensions * bytes_per_value
    graph = rows * links * 8
    metadata = rows * metadata_bytes
    total = (vectors + graph + metadata) * replicas
    return {
        "vector_bytes": vectors,
        "graph_estimate_bytes": graph,
        "metadata_estimate_bytes": metadata,
        "replicas": replicas,
        "provisioned_bytes": math.ceil(total / (1 - headroom)),
        "scope": "Planning estimate. Excludes allocator, sparse index, WAL, compaction and temporary build overhead.",
    }


def monthly_cost(
    *,
    hourly_compute,
    storage_gib,
    storage_rate,
    requests_million=0,
    request_rate=0,
    egress_gib=0,
    egress_rate=0,
    operator_hours=0,
    operator_rate=0,
):
    values = locals()
    if any(not math.isfinite(v) or v < 0 for v in values.values()):
        raise ValueError("Cost assumptions must be finite nonnegative numbers")
    return {
        "compute": 730 * hourly_compute,
        "storage": storage_gib * storage_rate,
        "requests": requests_million * request_rate,
        "egress": egress_gib * egress_rate,
        "operations": operator_hours * operator_rate,
    }
