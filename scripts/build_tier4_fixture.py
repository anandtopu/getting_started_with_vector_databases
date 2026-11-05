"""Reproduce a labeled temporal fixture independent of vector scores.
Run: uv run python scripts/build_tier4_fixture.py
CPU: seconds. Existing generator events remain unchanged.
"""

import argparse
import shutil

import numpy as np
import pandas as pd

from common.data import load_products
from common.io import atomic_json, file_hash
from common.settings import data_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sources",
        action="store_true",
        help="Also extract included small fixtures from the generated full datasets",
    )
    args = parser.parse_args()
    products = load_products()
    root = data_dir() / "tier4"
    root.mkdir(parents=True, exist_ok=True)
    if args.sources:
        ids = set(products.id)
        pd.read_parquet(data_dir() / "reviews.parquet").head(400).to_parquet(
            root / "reviews.parquet", index=False
        )
        pairs = pd.read_parquet(data_dir() / "duplicates.parquet")
        pairs[pairs.source_id.isin(ids) & pairs.duplicate_id.isin(ids)].to_parquet(
            root / "duplicates.parquet", index=False
        )
        original = pd.read_parquet(data_dir() / "events.parquet")
        original[original.product_id.isin(ids)].to_parquet(root / "events.parquet", index=False)
        (root / "images").mkdir(exist_ok=True)
        for key in products.id[:200]:
            shutil.copyfile(data_dir() / "images" / f"{key}.png", root / "images" / f"{key}.png")
    kinds = sorted(products.kind.unique())
    rng = np.random.default_rng(20261104)
    events = []
    for user in range(100):
        kind = kinds[user % len(kinds)]
        ids = rng.choice(products.loc[products.kind == kind, "id"].tolist(), 7, replace=False)
        for i, key in enumerate(ids):
            events.append(
                {
                    "id": f"temporal-{user:03d}-{i}",
                    "user_id": f"eval-user-{user:03d}",
                    "product_id": key,
                    "action": ["view", "view", "view", "cart", "purchase", "purchase", "purchase"][
                        i
                    ],
                    "timestamp": f"2025-12-{i + 1 if i < 5 else i + 16:02d}T12:00:00Z",
                    "provenance": "synthetic-kind-preference-v1",
                }
            )
    path = data_dir() / "tier4/events_evaluation.parquet"
    pd.DataFrame(events).to_parquet(path, index=False)
    atomic_json(
        path.with_suffix(".json"),
        {
            "seed": 20261104,
            "users": 100,
            "events": len(events),
            "rule": "Per-user product kind chosen independently of embeddings. Five past events, two distinct future purchases, sampled without replacement.",
            "cutoff": "2025-12-20T00:00:00Z",
            "reason": "Original event generator repeats seen products and assigns only one action type per user, leaving no eligible unseen-purchase cases in the first 100-user audit.",
            "sha256": file_hash(path),
            "license": "MIT synthetic data",
        },
    )
    print(path)


if __name__ == "__main__":
    main()
