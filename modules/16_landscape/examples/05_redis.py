"""Redis Search native vector and text indexes.

Run: uv run --extra landscape python modules/16_landscape/examples/05_redis.py
Concepts: Redis Search native vector and text indexes.
Expected: Redis tag and KNN.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the redis profile first.
"""

# course-extra: landscape
# course-profile: redis
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Redis Search native vector and text indexes.
    with session("redis", 80) as (s, _, q):
        rows = s.db.execute_command(
            "FT.SEARCH", s.name, "@body:(mug warmer)", "NOCONTENT", "LIMIT", 0, 3
        )
        print("lexical matches", rows)
        hits = s.search(q, 5, {"op": "eq", "field": "region", "value": "north"})
        assert hits and all(h.metadata["region"] == "north" for h in hits)
        print("vector hits", [h.id for h in hits])


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "redis")
