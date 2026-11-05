import re

import yaml

from common.data import load_products, load_vectors
from common.embeddings import frozen_query
from common.settings import ROOT, data_dir


def test_committed_semantic_artifacts_align():
    products = load_products(limit=20)
    matrix, metadata = load_vectors(data_dir() / "embeddings_10k.parquet", products)
    query, query_metadata = frozen_query("q000", data_dir())
    assert matrix.shape == (20, 384)
    assert query.shape == (384,)
    assert metadata["space"] == query_metadata["space"]
    assert "MiniLM" in metadata["space"]


def test_every_compose_service_is_profiled_pinned_and_local():
    compose = yaml.safe_load((ROOT / "docker/compose.yaml").read_text())
    for service in compose["services"].values():
        assert service["profiles"]
        assert re.search(r":[^:@]+@sha256:[0-9a-f]{64}$", service["image"])
        assert ":latest" not in service["image"]
        assert service["labels"]["org.marlowe.course"] == "vector-databases"
        assert all(port.startswith("127.0.0.1:") for port in service.get("ports", []))
