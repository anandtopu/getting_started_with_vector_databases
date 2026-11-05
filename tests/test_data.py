import json

import pyarrow.parquet as pq

from common.generation import build_data, product
from common.io import read_jsonl


def test_generation_reproducibility_and_referential_integrity(tmp_path):
    first = build_data(tmp_path / "first", count=100, images=20)
    second = build_data(tmp_path / "second", count=100, images=20)
    assert first == second
    root = tmp_path / "first"
    products = pq.read_table(root / "products.parquet").to_pylist()
    ids = {row["id"] for row in products}
    assert len(ids) == 100
    sellers = {s["id"] for s in json.loads((root / "sellers.json").read_text())}
    assert all(row["seller_id"] in sellers for row in products)
    duplicates = pq.read_table(root / "duplicates.parquet").to_pylist()
    assert all(row["source_id"] in ids and row["duplicate_id"] in ids for row in duplicates)
    queries = read_jsonl(root / "eval/search_qrels.jsonl")
    assert len(queries) == 300
    assert {q["type"] for q in queries} == {
        "semantic",
        "keyword",
        "filtered",
        "misspelled",
        "multilingual",
        "photo",
    }
    assert all(set(q["qrels"]) <= ids for q in queries)
    assert len(list((root / "help_center").glob("*.md"))) == 80
    assert len(read_jsonl(root / "eval/rag_qa.jsonl")) == 80
    assert products[49]["kind"] == products[0]["kind"]
    assert product(0)["id"] == products[0]["id"]
