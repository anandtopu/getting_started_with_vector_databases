"""Store a shortened Qwen prefix and retrieve its nearest LanceDB product.
Run: uv run --extra embedded python modules/08_quantization/examples/06_lance_prefix.py
CPU: a few seconds. Uses included Qwen samples, no model downloads or Docker.
"""

# course-extra: embedded
import tempfile

import lancedb
import numpy as np
import pyarrow as pa

from common.index_lessons import prefix_results
from common.settings import ROOT


def main():
    dimension = 64
    expected = prefix_results()[str(dimension)]["top10"]
    with np.load(ROOT / "data/tier2/matryoshka.npz", allow_pickle=False) as sample:
        vectors = sample["documents"][:, :dimension]
        vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        query = sample["query"][:dimension]
        query = query / np.linalg.norm(query)
        schema = pa.schema([("id", pa.string()), ("vector", pa.list_(pa.float32(), dimension))])
        rows = [
            {"id": key, "vector": v.tolist()}
            for key, v in zip(sample["ids"].tolist(), vectors, strict=True)
        ]
    with tempfile.TemporaryDirectory() as directory:
        db = lancedb.connect(directory)
        table = db.create_table("qwen_prefix", data=pa.Table.from_pylist(rows, schema=schema))
        hits = table.search(query).distance_type("cosine").limit(10).to_list()
        assert {h["id"] for h in hits} == set(expected)
        print("Qwen 64-dimensional prefix", [(h["id"], h["_distance"]) for h in hits])
        del table, db


if __name__ == "__main__":
    main()
