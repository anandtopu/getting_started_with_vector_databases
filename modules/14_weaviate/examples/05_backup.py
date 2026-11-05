"""Create a filesystem backup and restore its original Weaviate collection.

Run: uv run --extra weaviate python modules/14_weaviate/examples/05_backup.py
Concepts: Create a filesystem backup and restore its original Weaviate collection.
Expected: filesystem backup and restored IDs.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the weaviate profile first.
"""

# course-extra: weaviate
# course-profile: weaviate
import uuid

from common.tier3 import session


def main() -> None:
    # KEY IDEA: Create a filesystem backup and restore its original Weaviate collection.
    with session("weaviate", 80) as (s, _, q):
        expected = [h.id for h in s.search(q, 3)]
        backup = "marlowe-" + uuid.uuid4().hex
        s.db.backup.create(
            backup_id=backup,
            backend="filesystem",
            include_collections=[s.name],
            wait_for_completion=True,
        )
        s.db.collections.delete(s.name)
        s.created = False
        s.db.backup.restore(
            backup_id=backup,
            backend="filesystem",
            include_collections=[s.name],
            wait_for_completion=True,
        )
        s.created = True
        s.table = s.db.collections.use(s.name)
        assert [h.id for h in s.search(q, 3)] == expected
        print("restored backup", backup, "IDs", expected)


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "weaviate")
