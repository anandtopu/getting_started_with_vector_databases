"""Wait for a named, explicitly started course server using its native client.
Run: uv run --extra pgvector python scripts/check_profile.py pgvector
CPU: normally seconds; allows up to three minutes. Does not start containers.
"""

import argparse
import time

from common.stores.registry import DATABASES, make_store
from common.stores.types import CollectionSpec, Record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "backend", choices=sorted(DATABASES.keys() - {"chroma", "duckdb", "lancedb"})
    )
    args = parser.parse_args()
    deadline = time.monotonic() + 180
    while True:
        store = None
        try:
            store = make_store(args.backend)
            store.create_collection(CollectionSpec("health", 3, "cosine", "health-v1"))
            store.upsert([Record("probe", [1, 0, 0], {}, "readiness")])
            if store.search([1, 0, 0], 1)[0].id == "probe":
                print(f"{args.backend}: native write and query ready")
                return
        except Exception as error:
            if time.monotonic() >= deadline:
                raise SystemExit(
                    f"{args.backend} unavailable: {error}. Inspect its compose logs and scripts/check_env.py --services."
                ) from None
        finally:
            if store is not None:
                store.close()
        time.sleep(2)


if __name__ == "__main__":
    main()
