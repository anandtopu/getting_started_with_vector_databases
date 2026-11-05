"""Native API smoke tests; full shared server adapters arrive with Tier 3."""

import os
import time
import uuid

import httpx
import pytest

pytestmark = pytest.mark.docker


def test_qdrant_native_crud_filter():
    if os.environ.get("MARLOWE_TEST_DATABASE") != "qdrant":
        pytest.skip("Set MARLOWE_TEST_DATABASE=qdrant and start its profile")
    collection = "marlowe_test_" + uuid.uuid4().hex
    with httpx.Client(base_url="http://127.0.0.1:6333", timeout=10) as client:
        for attempt in range(60):
            try:
                if client.get("/readyz").is_success:
                    break
            except httpx.HTTPError:
                if attempt == 59:
                    raise
            time.sleep(1)
        client.put(
            f"/collections/{collection}", json={"vectors": {"size": 3, "distance": "Cosine"}}
        ).raise_for_status()
        try:
            client.put(
                f"/collections/{collection}/points?wait=true",
                json={
                    "points": [
                        {"id": 1, "vector": [1.0, 0.0, 0.0], "payload": {"seller": "a"}},
                        {"id": 2, "vector": [0.9, 0.1, 0.0], "payload": {"seller": "b"}},
                    ]
                },
            ).raise_for_status()
            response = client.post(
                f"/collections/{collection}/points/query",
                json={
                    "query": [1.0, 0.0, 0.0],
                    "limit": 2,
                    "filter": {"must": [{"key": "seller", "match": {"value": "b"}}]},
                },
            )
            response.raise_for_status()
            assert [p["id"] for p in response.json()["result"]["points"]] == [2]
            client.post(
                f"/collections/{collection}/points/delete?wait=true", json={"points": [2]}
            ).raise_for_status()
        finally:
            client.delete(f"/collections/{collection}").raise_for_status()


def test_pgvector_native_distance_and_transaction():
    if os.environ.get("MARLOWE_TEST_DATABASE") != "pgvector":
        pytest.skip("Set MARLOWE_TEST_DATABASE=pgvector and start its profile")
    import psycopg

    with psycopg.connect("postgresql://marlowe:marlowe-local@127.0.0.1:5432/marlowe") as connection:
        connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
        connection.execute(
            "CREATE TEMP TABLE marlowe_test (id integer, seller text, embedding vector(3))"
        )
        connection.execute(
            "INSERT INTO marlowe_test VALUES (1, 'a', '[1,0,0]'), (2, 'b', '[0.9,0.1,0]')"
        )
        rows = connection.execute(
            "SELECT id FROM marlowe_test WHERE seller=%s ORDER BY embedding <=> %s::vector LIMIT 2",
            ("b", "[1,0,0]"),
        ).fetchall()
        assert rows == [(2,)]
