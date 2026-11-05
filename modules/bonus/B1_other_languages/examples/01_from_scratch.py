"""Preserve vector identity across a JSON boundary.
Concepts: serialization and native clients.
Run: uv run python modules/bonus/B1_other_languages/examples/01_from_scratch.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""

import json

import numpy as np

from common.teaching import catalog


def main() -> None:
    products, vectors, query, meta = catalog(100)
    encoded = json.dumps({"space": meta["space"], "query": query.tolist()})
    restored = json.loads(encoded)
    assert restored["space"] == meta["space"]
    np.testing.assert_array_equal(np.array(restored["query"], dtype=np.float32), query)
    seller = products.iloc[0].seller_id
    eligible = np.flatnonzero(products.seller_id.to_numpy() == seller)
    ranked = eligible[np.argsort(-(vectors[eligible] @ query))[:5]]
    print({"seller": seller, "ids": products.iloc[ranked].id.tolist(), "dimensions": len(query)})


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
