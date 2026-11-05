"""Vespa tensor search in a dedicated deployed course application."""

import httpx
import numpy as np

from common.settings import setting
from common.stores.database import DatabaseStore, literals, pack


def tensor(v):
    padded = np.zeros(384, dtype=np.float32)
    padded[: len(v)] = v / np.linalg.norm(v)
    return padded.tolist()


class VespaStore(DatabaseStore):
    def __init__(self):
        super().__init__()
        self.db = httpx.Client(base_url=setting("VESPA_URL", "http://127.0.0.1:8081"), timeout=20)

    def _create(self, spec):
        if spec.dimensions > 384:
            raise ValueError("Vespa course schema accepts at most 384 dimensions")
        self.db.get("/ApplicationStatus").raise_for_status()

    def path(self, key):
        return f"/document/v1/{self.name}/product/docid/{key}"

    def _put(self, rows):
        for key, r in rows.items():
            self.db.post(
                self.path(key),
                json={
                    "fields": {
                        "key": key,
                        "scope": self.name,
                        "v": tensor(r.vector),
                        "body": r.text,
                        "packed": pack(r),
                    }
                },
            ).raise_for_status()

    def _delete(self, keys):
        for key in keys:
            self.db.delete(self.path(key)).raise_for_status()

    def _query(self, q, keys, k):
        where = "scope contains @scope"
        if keys is not None:
            where += " AND key in (" + literals(keys) + ")"
        yql = f"select key from product where {where} AND ({{targetHits:{k},approximate:false}}nearestNeighbor(v,q))"
        result = (
            self.db.post(
                "/search/",
                json={
                    "yql": yql,
                    "scope": self.name,
                    "input.query(q)": tensor(q),
                    "ranking": "semantic",
                    "hits": k,
                    "timeout": "10s",
                },
            )
            .raise_for_status()
            .json()["root"]
        )
        if result.get("errors"):
            raise RuntimeError(result["errors"])
        return [(h["fields"]["key"], h["relevance"]) for h in result.get("children", [])]

    def _payloads(self):
        for key in self.catalog:
            yield self.db.get(self.path(key)).raise_for_status().json()["fields"]["packed"]

    def _drop(self):
        self._delete(list(self.catalog))

    def _disconnect(self):
        self.db.close()
