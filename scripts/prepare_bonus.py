"""Export genuine frozen vectors for the TypeScript examples; no model downloads.
Run: uv run python scripts/prepare_bonus.py
Expected: 200 explicit MiniLM vectors, stable UUIDs and one query. CPU: seconds.
"""

import uuid

from common.io import atomic_json
from common.settings import cache_dir
from common.teaching import catalog


def main():
    products, vectors, query, metadata = catalog(200)
    rows = [
        {
            "id": row.id,
            "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, "marlowe:" + row.id)),
            "vector": vector.tolist(),
            "seller_id": row.seller_id,
            "title": row.title,
            "price": float(row.price),
        }
        for row, vector in zip(products.itertuples(), vectors, strict=True)
    ]
    path = cache_dir() / "bonus/ts-fixture.json"
    atomic_json(
        path,
        {
            "space": metadata["space"],
            "dimensions": vectors.shape[1],
            "records": rows,
            "query": query.tolist(),
        },
    )
    print(path)


if __name__ == "__main__":
    main()
