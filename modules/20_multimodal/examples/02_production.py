"""Store image and text vectors together in one Qdrant point.

Run: uv run --extra qdrant python modules/20_multimodal/examples/02_production.py
Expected: same payload, two named vector spaces, cross-modal results.
CPU: seconds to one minute. Needs: qdrant extra, prepared SigLIP vectors. No implicit downloads.
"""
# course-extra: qdrant

import time

from common.apps.artifacts import load_artifact
from common.apps.database import AppDatabase
from common.pretty import show_hits
from common.tier4 import open_photos


def main() -> None:
    with AppDatabase("qdrant-local") as db:
        photos, _, _ = open_photos(db)
        try:
            _, queries, meta = load_artifact("image_queries")
            info = db.client.get_collection(photos.name)
            assert set(info.config.params.vectors) == {"image", "text"}
            start = time.perf_counter()
            # KEY IDEA: the query must declare its model space despite identical dimensions.
            hits = photos.search(
                queries[0], space=meta["space"], image_weight=1, exclude=["p0000000"]
            )
            show_hits(hits, (time.perf_counter() - start) * 1000, title="Text to image")
        finally:
            photos.close()


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
