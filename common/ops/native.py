"""Owned native Qdrant experiments with TLS verification and bounded readiness waits."""

import json
import ssl
import time
import uuid
from contextlib import contextmanager

import httpx

from common.apps.artifacts import load_artifact
from common.settings import cache_dir, setting
from common.teaching import catalog


def credentials():
    root = cache_dir() / "tier5/runtime"
    return root, json.loads((root / "qdrant-keys.json").read_text())


def open_client(read_only=False):
    from qdrant_client import QdrantClient

    root, keys = credentials()
    return QdrantClient(
        url=setting("SECURE_QDRANT_URL", "https://localhost:6333"),
        api_key=keys["read" if read_only else "admin"],
        verify=ssl.create_default_context(cafile=str(root / "tls/ca.pem")),
        limits=httpx.Limits(max_connections=8, max_keepalive_connections=8),
        timeout=20,
        check_compatibility=False,
    )


@contextmanager
def client(read_only=False):
    db = open_client(read_only)
    try:
        yield db
    finally:
        db.close()


def native_migration_restore():
    from qdrant_client import models as m

    products, vectors, query, meta = catalog(500)
    _, green, gm = load_artifact("multilingual_products")
    qids, queries, _ = load_artifact("multilingual_queries")
    name = "marlowe_ops_" + uuid.uuid4().hex
    blue_name, green_name, restored_name, alias = [
        name + suffix for suffix in ["_blue", "_green", "_restored", "_active"]
    ]
    names = []
    result = {"old_space": meta["space"], "new_space": gm["space"], "rows": len(products)}
    with client() as db:
        try:
            for target, matrix in [(blue_name, vectors), (green_name, green)]:
                db.create_collection(
                    target,
                    vectors_config=m.VectorParams(size=matrix.shape[1], distance=m.Distance.COSINE),
                )
                names.append(target)
                db.upsert(
                    target,
                    [
                        m.PointStruct(
                            id=i,
                            vector=v.tolist(),
                            payload={"id": row.id, "seller_id": row.seller_id},
                        )
                        for i, (row, v) in enumerate(
                            zip(products.itertuples(), matrix, strict=True)
                        )
                    ],
                    wait=True,
                )
            db.update_collection_aliases(
                [
                    m.CreateAliasOperation(
                        create_alias=m.CreateAlias(collection_name=blue_name, alias_name=alias)
                    )
                ]
            )
            result["blue_ids"] = [
                p.payload["id"]
                for p in db.query_points(alias, query=query.tolist(), limit=5).points
            ]
            # Replay a deletion in both spaces before publishing the green alias.
            for target in [blue_name, green_name]:
                db.delete(target, points_selector=[0], wait=True)
            assert all(
                db.count(target, exact=True).count == 499 for target in [blue_name, green_name]
            )
            db.update_collection_aliases(
                [
                    m.DeleteAliasOperation(delete_alias=m.DeleteAlias(alias_name=alias)),
                    m.CreateAliasOperation(
                        create_alias=m.CreateAlias(collection_name=green_name, alias_name=alias)
                    ),
                ]
            )
            green_query = queries[qids.index("q004")]
            result["green_ids"] = [
                p.payload["id"]
                for p in db.query_points(alias, query=green_query.tolist(), limit=5).points
            ]
            assert "p0000000" not in result["green_ids"]
            try:
                db.query_points(alias, query=query.tolist(), limit=1)
            except Exception as exc:
                result["wrong_space_rejected"] = type(exc).__name__
            else:
                raise AssertionError("Server accepted a mismatched dimension")
            db.update_collection_aliases(
                [
                    m.DeleteAliasOperation(delete_alias=m.DeleteAlias(alias_name=alias)),
                    m.CreateAliasOperation(
                        create_alias=m.CreateAlias(collection_name=blue_name, alias_name=alias)
                    ),
                ]
            )
            result["rollback_count"] = db.count(alias, exact=True).count
            snapshot = db.create_snapshot(blue_name)
            root, keys = credentials()
            url = setting("SECURE_QDRANT_URL", "https://localhost:6333")
            context = ssl.create_default_context(cafile=str(root / "tls/ca.pem"))
            with httpx.Client(verify=context, timeout=30) as http:
                download = http.get(
                    f"{url}/collections/{blue_name}/snapshots/{snapshot.name}",
                    headers={"api-key": keys["admin"]},
                )
                download.raise_for_status()
                start = time.perf_counter()
                response = http.post(
                    f"{url}/collections/{restored_name}/snapshots/upload",
                    params={"priority": "snapshot"},
                    files={"snapshot": ("backup.snapshot", download.content)},
                    headers={"api-key": keys["admin"]},
                )
                response.raise_for_status()
                names.append(restored_name)
            deadline = time.monotonic() + 30
            while db.count(restored_name, exact=True).count != 499:
                if time.monotonic() > deadline:
                    raise TimeoutError("Snapshot restore readiness timeout")
                time.sleep(0.1)
            result.update(
                snapshot_bytes=len(download.content),
                restore_seconds=time.perf_counter() - start,
                restored_rows=499,
                rpo_deleted_rows=0,
            )
            assert db.retrieve(restored_name, [0]) == []
        finally:
            db.update_collection_aliases(
                [m.DeleteAliasOperation(delete_alias=m.DeleteAlias(alias_name=alias))]
            )
            for target in reversed(names):
                db.delete_collection(target)
    return result


def native_security():
    from qdrant_client import models as m

    root, keys = credentials()
    url = setting("SECURE_QDRANT_URL", "https://localhost:6333")
    context = ssl.create_default_context(cafile=str(root / "tls/ca.pem"))
    result = {}
    with httpx.Client(verify=context) as http:
        result["unauthenticated_status"] = http.get(url + "/collections").status_code
        result["read_status"] = http.get(
            url + "/collections", headers={"api-key": keys["read"]}
        ).status_code
        assert result["read_status"] == 200
        name = "marlowe_forbidden_" + uuid.uuid4().hex
        result["read_key_write_status"] = http.put(
            url + "/collections/" + name,
            json={"vectors": {"size": 2, "distance": "Cosine"}},
            headers={"api-key": keys["read"]},
        ).status_code
        assert result["read_key_write_status"] in {401, 403} and result[
            "unauthenticated_status"
        ] in {401, 403}
    try:
        httpx.get(url + "/collections", timeout=5)
    except httpx.ConnectError:
        result["untrusted_ca_rejected"] = True
    else:
        raise AssertionError("Untrusted local CA unexpectedly accepted")
    with client() as db:
        name = "marlowe_scope_" + uuid.uuid4().hex
        db.create_collection(
            name, vectors_config=m.VectorParams(size=2, distance=m.Distance.COSINE)
        )
        try:
            db.upsert(
                name,
                [
                    m.PointStruct(id=1, vector=[1.0, 0], payload={"tenant": "a"}),
                    m.PointStruct(id=2, vector=[1.0, 0], payload={"tenant": "b"}),
                ],
            )
            condition = m.Filter(
                must=[m.FieldCondition(key="tenant", match=m.MatchValue(value="a"))]
            )
            scoped = db.query_points(name, query=[1.0, 0], query_filter=condition, limit=10).points
            unscoped = db.query_points(name, query=[1.0, 0], limit=10).points
            result.update(
                scoped_ids=[p.id for p in scoped], omitted_filter_ids=[p.id for p in unscoped]
            )
            assert result["scoped_ids"] == [1] and len(unscoped) == 2
        finally:
            db.delete_collection(name)
    return result
