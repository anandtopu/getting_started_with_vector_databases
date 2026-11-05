"""Compare Lance table versions, native hybrid ranking and vector indexing.

Run: uv run --extra embedded python modules/11_embedded/examples/04_lancedb.py
Concepts: Compare Lance table versions, native hybrid ranking and vector indexing.
Expected: restored version, IVF-PQ and northern hybrid IDs.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

# course-extra: embedded
import tempfile

import lancedb
import pyarrow as pa
from lancedb.index import FTS, IvfPq

from common.teaching import catalog


def main() -> None:
    # KEY IDEA: Compare Lance table versions, native hybrid ranking and vector indexing.
    products, matrix, q, _ = catalog(640)
    schema = pa.schema(
        [
            ("id", pa.string()),
            ("text", pa.string()),
            ("region", pa.string()),
            ("v", pa.list_(pa.float32(), matrix.shape[1])),
        ]
    )
    rows = [
        {"id": p.id, "text": p.title, "region": p.region, "v": v.tolist()}
        for p, v in zip(products.itertuples(), matrix, strict=True)
    ]
    with tempfile.TemporaryDirectory() as tmp:
        with lancedb.connect(tmp) as db:
            table = db.create_table("products", data=pa.Table.from_pylist(rows, schema=schema))
            version = table.version
            table.delete("region = 'north'")
            smaller = table.count_rows()
            table.checkout(version)
            assert smaller < table.count_rows() == 640
            table.restore()
            table.create_index("text", config=FTS())
            table.create_index(
                "v",
                config=IvfPq(
                    distance_type="cosine", num_partitions=4, num_sub_vectors=8, num_bits=4
                ),
            )
            hits = (
                table.search(query_type="hybrid", vector_column_name="v")
                .vector(q)
                .text("mug warmer")
                .where("region = 'north'", prefilter=True)
                .limit(5)
                .to_list()
            )
            assert hits and all(h["region"] == "north" for h in hits)
            print("versions", table.list_versions(), "hybrid hits", [h["id"] for h in hits])
            del table


if __name__ == "__main__":
    main()
