"""Small native API checks for the embedded databases; shared adapters follow in Tier 3."""

import pytest

pytestmark = pytest.mark.embedded


def test_chroma_explicit_vectors_no_model(tmp_path):
    chromadb = pytest.importorskip("chromadb")
    client = chromadb.PersistentClient(
        path=str(tmp_path / "chroma"), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    collection = client.create_collection("marlowe_native", embedding_function=None)
    try:
        collection.upsert(
            ids=["a", "b"],
            embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            metadatas=[{"seller": "one"}, {"seller": "two"}],
        )
        result = collection.query(
            query_embeddings=[[1.0, 0.0, 0.0]], n_results=2, where={"seller": "two"}
        )
        assert result["ids"] == [["b"]]
        collection.delete(ids=["b"])
        assert collection.count() == 1
    finally:
        client.delete_collection("marlowe_native")


@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
def test_lancedb_explicit_vectors_no_model(tmp_path):
    # Windows asyncio uses a loopback socketpair for its internal wake-up pipe.
    # External connections remain blocked; no database server is started.
    lancedb = pytest.importorskip("lancedb")
    db = lancedb.connect(str(tmp_path / "lance"))
    table = db.create_table(
        "products",
        data=[
            {"id": "a", "vector": [1.0, 0.0, 0.0], "seller": "one"},
            {"id": "b", "vector": [0.0, 1.0, 0.0], "seller": "two"},
        ],
    )
    assert (
        table.search([1.0, 0.0, 0.0])
        .where("seller = 'two'", prefilter=True)
        .limit(2)
        .to_list()[0]["id"]
        == "b"
    )
    table.delete("id = 'b'")
    assert table.count_rows() == 1
    db.drop_table("products")


def test_duckdb_exact_array_search_without_extension_download():
    duckdb = pytest.importorskip("duckdb")
    with duckdb.connect(
        ":memory:",
        config={"autoinstall_known_extensions": False, "autoload_known_extensions": False},
    ) as db:
        db.execute("CREATE TABLE items (id INTEGER, embedding FLOAT[3])")
        db.execute("INSERT INTO items VALUES (1, [1,0,0]), (2, [0,1,0])")
        assert db.execute(
            "SELECT id FROM items ORDER BY array_distance(embedding, [1,0,0]::FLOAT[3]) LIMIT 1"
        ).fetchone() == (1,)
