"""Query a real database with an event-weighted user vector.

Run: uv run --extra qdrant python modules/19_recommendations/examples/02_production.py
Expected: recommendations exclude products already seen before the cutoff.
CPU: seconds to one minute. Needs: qdrant extra, saved catalog and events. No implicit downloads.
"""
# course-extra: qdrant

import pandas as pd

from common.apps.database import AppDatabase
from common.apps.product_search import ProductSearch
from common.apps.recommendations import recommend, user_profile
from common.settings import data_dir


def main() -> None:
    events = pd.read_parquet(data_dir() / "tier4/events.parquet")
    with AppDatabase("qdrant-local") as db:
        search = ProductSearch(db, 1000)
        vectors = {key: r.vector for key, r in search.by_id.items()}
        group = events[events.user_id == "synthetic-user-0000"]
        profile, seen = user_profile(group.to_dict("records"), vectors, "2025-12-20T00:00:00Z")
        assert profile is not None
        # KEY IDEA: future purchases cannot leak into the user profile.
        ids = recommend(search, profile, exclude=seen)
        assert not set(ids) & seen
        print({"seen": sorted(seen), "recommendations": ids})


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
