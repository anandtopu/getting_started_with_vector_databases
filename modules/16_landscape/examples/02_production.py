"""Serve FAISS behind a local request and restore it in a new application.

Run: uv run --extra apps --extra libs python modules/16_landscape/examples/02_production.py
Concepts: Serve FAISS behind a local request and restore it in a new application.
Expected: FAISS API lifecycle.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

# course-extra: apps,libs
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from common.apps.faiss_service import create_app
from common.teaching import catalog


def main() -> None:
    # KEY IDEA: Serve FAISS behind a local request and restore it in a new application.
    products, matrix, q, meta = catalog(80)
    payload = [
        {"id": p.id, "vector": v.tolist(), "metadata": {"region": p.region}, "text": p.title}
        for p, v in zip(products.itertuples(), matrix, strict=True)
    ]
    request = {
        "vector": q.tolist(),
        "space": meta["space"],
        "k": 5,
        "filter": {"op": "eq", "field": "region", "value": "north"},
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        with TestClient(create_app(path, 384, meta["space"])) as api:
            api.put("/items", json=payload).raise_for_status()
            first = api.post("/search", json=request).raise_for_status().json()
            api.post("/snapshot").raise_for_status()
        with TestClient(create_app(path, 384, meta["space"])) as api:
            restored = api.post("/search", json=request).raise_for_status().json()
            assert first == restored and all(r["metadata"]["region"] == "north" for r in first)
            print("HTTP contract restored", first)


if __name__ == "__main__":
    main()
