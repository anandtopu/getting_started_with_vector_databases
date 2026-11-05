"""Store token vectors and rerank native LanceDB candidates.

Run: uv run --extra embedded python modules/10_filtering_hybrid/examples/04_lance_hybrid.py
Expected: compare the reported ranking and verify the final assertion.
CPU: seconds, included data, no Docker or model downloads.
"""

# course-extra: embedded
import tempfile

import lancedb
import pyarrow as pa
from lancedb.index import FTS

from common.index_lessons import unit_catalog
from tinyvec.hybrid import maxsim, tokens


def main():
    products, matrix, q = unit_catalog(160)
    # Interpretable token features for this scorer demonstration; neural token encoders use learned features.
    vocabulary = ["mug", "warmer", "coffee", "desk"]

    def features(text):
        return [[float(word == term) for term in vocabulary] for word in tokens(text)] or [
            [0.0] * 4
        ]

    rows = [
        {"id": p.id, "text": p.title, "vector": v.tolist(), "token_vectors": features(p.title)}
        for p, v in zip(products.itertuples(), matrix, strict=True)
    ]
    schema = pa.schema(
        [
            ("id", pa.string()),
            ("text", pa.string()),
            ("vector", pa.list_(pa.float32(), matrix.shape[1])),
            ("token_vectors", pa.list_(pa.list_(pa.float32(), 4))),
        ]
    )
    with tempfile.TemporaryDirectory() as directory:
        db = lancedb.connect(directory)
        table = db.create_table("products", data=pa.Table.from_pylist(rows, schema=schema))
        table.create_index("text", config=FTS())
        hits = (
            table.search(query_type="hybrid", vector_column_name="vector")
            .vector(q)
            .text("mug warmer")
            .limit(8)
            .to_list()
        )
        reranked = sorted(
            hits, key=lambda row: -maxsim(features("mug warmer"), row["token_vectors"])
        )
        print(
            "native hybrid",
            [h["id"] for h in hits],
            "late interaction",
            [h["id"] for h in reranked],
        )
        assert hits and {r["id"] for r in hits} == {r["id"] for r in reranked}
        del table, db


if __name__ == "__main__":
    main()
