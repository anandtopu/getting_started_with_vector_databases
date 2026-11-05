"""Behavioral checks for filtering, leakage, citations and application integration."""

import numpy as np
import pytest

from common.apps.database import AppDatabase
from common.apps.deduplication import calibrate, threshold_metrics
from common.apps.multimodal import MultimodalSearch, weighted_fusion
from common.apps.product_search import ProductSearch
from common.apps.rag import chunk_article
from common.apps.recommendations import mmr, user_profile
from common.embeddings import frozen_query
from common.search.query_parser import parse_query
from common.settings import data_dir
from common.stores.filters import matches, parse_filter
from common.tier4 import open_rag


def test_query_parser_boundaries_and_ambiguity():
    result = parse_query("mug under $100, in stock, in the north region")
    assert result.text == "mug" and not result.warnings
    expr = parse_filter(result.filter)
    assert matches({"price": 99.99, "stock": 1, "region": "north"}, expr)
    assert not matches({"price": 100, "stock": 1, "region": "north"}, expr)
    assert matches({"price": 100}, parse_filter(parse_query("mug at most $100").filter))
    assert parse_query("mug under $10 or over $100").filter is None
    assert parse_query("not in stock").warnings
    assert parse_query("chair under $19.999").warnings
    with pytest.raises(ValueError):
        parse_query("   ")


@pytest.mark.parametrize("backend", ["tinyvec", "qdrant-local", "sqlite-vec"])
def test_hybrid_both_branches_filter_and_sku(backend):
    if backend == "qdrant-local":
        pytest.importorskip("qdrant_client")
    if backend == "sqlite-vec":
        pytest.importorskip("sqlite_vec")
    with AppDatabase(backend) as db:
        search = ProductSearch(db, 100)
        vector, _ = frozen_query("q000", data_dir())
        result = search.search("mug under $100 in stock in the north region", vector)
        assert result.hits
        assert all(
            h.metadata["price"] < 100
            and h.metadata["stock"] > 0
            and h.metadata["region"] == "north"
            for h in result.hits
        )
        key = search.records[31].metadata["sku"]
        lexical = search.search(key, vector, mode="lexical")
        assert lexical.hits[0].id == search.records[31].id
        empty = search.search("mug", vector, filter={"op": "lt", "field": "price", "value": 0})
        assert empty.hits == []


def test_chunking_keeps_passage_identity_and_tail(tmp_path):
    source = tmp_path / "help-999.md"
    source.write_text(
        "# Returns for a buyer in the north region\n\n## Procedure\n\none two three four five six seven",
        encoding="utf8",
    )
    chunks = chunk_article(source, words=4, overlap=1)
    assert len(chunks) == 2
    assert chunks[1].text.endswith("four five six seven")
    assert {c.passage_id for c in chunks} == {"help-999#procedure"}
    assert chunks[0].metadata["role"] == "buyer"
    with pytest.raises(ValueError):
        chunk_article(source, words=4, overlap=4)


def test_rag_citation_is_not_faithfulness():
    with AppDatabase() as db:
        rag, qa, queries = open_rag(db)
        hits = rag.retrieve(qa[0]["question"], queries[qa[0]["id"]])
        assert all(h.metadata["role"] == "buyer" and h.metadata["region"] == "north" for h in hits)
        result = rag.answer(
            qa[0]["question"],
            hits,
            generate=lambda _: "Returns are available forever [help-000#procedure].",
        )
        assert result["citation_validity"] == 1 and result["faithfulness"] is None
        invalid = rag.answer("returns", hits, generate=lambda _: "[help-999#procedure]")
        assert invalid["draft_citation_validity"] == 0
        assert invalid["delivery_mode"] == "extractive_fallback"
        assert "help-999" not in invalid["answer"]
        assert rag.answer("unknown", [], generate=lambda _: pytest.fail("Should not call LLM"))[
            "abstained"
        ]


def test_profile_excludes_future_and_unknown_actions():
    vectors = {"a": np.array([1.0, 0.0]), "b": np.array([0.0, 1.0])}
    events = [
        {"product_id": "a", "action": "view", "timestamp": "2025-01-01"},
        {"product_id": "b", "action": "purchase", "timestamp": "2025-02-01"},
    ]
    profile, seen = user_profile(events, vectors, "2025-02-01")
    np.testing.assert_allclose(profile, [1, 0])
    assert seen == {"a"}
    assert user_profile([], vectors, "2025-02-01") == (None, set())


def test_mmr_can_choose_different_candidate_and_no_repeats():
    matrix = np.array([[1, 0], [0.99, 0.01], [0, 1]], dtype=float)
    assert mmr(["a", "b", "c"], matrix, [1, 0], 2, 1) == ["a", "b"]
    assert mmr(["a", "b", "c"], matrix, [1, 0], 2, 0.2) == ["a", "c"]
    with pytest.raises(ValueError):
        mmr(["a", "a", "b"], matrix, [1, 0])


def test_calibration_uses_labels_and_handles_no_predictions():
    result = calibrate([0.2, 0.4, 0.8, 0.9], [0, 0, 1, 1])
    assert result["threshold"] == 0.8 and result["f1"] == 1
    assert threshold_metrics([0.1], [1], 0.9)["recall"] == 0
    with pytest.raises(ValueError):
        calibrate([], [])


@pytest.mark.parametrize("backend", ["tinyvec", "qdrant-local"])
def test_named_spaces_self_exclusion_and_weight_endpoints(backend):
    if backend == "qdrant-local":
        pytest.importorskip("qdrant_client")
    with AppDatabase(backend) as db:
        images = np.array([[1.0, 0], [0, 1]])
        photos = MultimodalSearch(db, ["a", "b"], images, images[::-1], "shared")
        try:
            assert photos.search([1, 0], space="shared", image_weight=1)[0].id == "a"
            assert photos.search([1, 0], space="shared", image_weight=0)[0].id == "b"
            assert [h.id for h in photos.search([1, 0], space="shared", exclude=["a"])] == ["b"]
            with pytest.raises(ValueError):
                photos.search([1, 0], space="another-model")
        finally:
            photos.close()
    assert weighted_fusion({"a": ["x", "x", "y"]}, {"a": 1}) == [("x", 1 / 61), ("y", 1 / 62)]


@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
@pytest.mark.parametrize("backend", ["tinyvec", "qdrant-local", "sqlite-vec"])
def test_complete_api_lifecycle(backend):
    pytest.importorskip("fastapi")
    if backend == "qdrant-local":
        pytest.importorskip("qdrant_client")
    if backend == "sqlite-vec":
        pytest.importorskip("sqlite_vec")
    from fastapi.testclient import TestClient

    from common.apps.marlowe_api import create_app

    with TestClient(create_app(backend=backend, limit=100)) as client:
        assert client.get("/health").json()["version"] == 5
        found = client.post("/search", json={"query_id": "q000"})
        assert found.status_code == 200 and len(found.json()["hits"]) == 5
        multilingual = client.post("/search", json={"query_id": "q004", "multilingual": True})
        assert multilingual.status_code == 200
        assert all("mug warmer" in h["metadata"]["title"] for h in multilingual.json()["hits"])
        assert client.post("/search", json={"k": 0}).status_code == 422
        assert client.post("/search", json={"query_id": "missing"}).status_code == 400
        assert client.post("/help", json={}).json()["passages"]
        assert len(client.get("/similar/p0000000").json()) == 5
        assert (
            client.post(
                "/duplicates", json={"first": "p0000000", "second": "p0000049", "threshold": 0.9}
            ).status_code
            == 200
        )
        assert all(h["id"] != "p0000000" for h in client.post("/photos", json={}).json())


@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
def test_marlowe_ui_saved_workflows():
    testing = pytest.importorskip("streamlit.testing.v1")
    from common.settings import ROOT

    app = testing.AppTest.from_file(str(ROOT / "playground/marlowe.py")).run(timeout=45)
    assert not app.exception and not app.error
    for label in [
        "Find products",
        "Find help",
        "Discover similar items",
        "Compare listings",
        "Search images",
    ]:
        next(b for b in app.button if b.label == label).click().run(timeout=45)
        assert not app.exception and not app.error
    next(b for b in app.button if b.label == "Release application data").click().run(timeout=30)
    assert not app.exception
