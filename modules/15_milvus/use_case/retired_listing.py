"""Verify strong visibility after retiring a sale item.

Run: uv run --extra milvus python modules/15_milvus/use_case/retired_listing.py
Concepts: Verify strong visibility after retiring a sale item.
Expected: the eligible product IDs or recovery decision shown in the README.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the milvus profile first.
"""

# course-extra: milvus
# course-profile: milvus
from common.tier3 import observe, session


def main() -> None:
    # KEY IDEA: Verify strong visibility after retiring a sale item.
    with session("milvus", 160, consistency="Strong") as (s, _, q):
        first = s.search(q, 5)
        s.delete([first[0].id])
        after = s.search(q, 5)
        assert first[0].id not in [h.id for h in after]
        observe("milvus-retirement", {"deleted": first[0].id, "remaining": [h.id for h in after]})


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "milvus")
