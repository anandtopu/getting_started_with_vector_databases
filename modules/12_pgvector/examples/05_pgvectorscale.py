"""Check the optional extension before interpreting index support.

Run: uv run --extra pgvector python modules/12_pgvector/examples/05_pgvectorscale.py
Concepts: Check the optional extension before interpreting index support.
Expected: optional extension discovery.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the pgvector profile first.
"""

# course-extra: pgvector
# course-profile: pgvector
import psycopg

from common.settings import setting


def main() -> None:
    # KEY IDEA: Check the optional extension before interpreting index support.
    with psycopg.connect(
        setting("POSTGRES_URL", "postgresql://marlowe:marlowe-local@127.0.0.1:5432/marlowe")
    ) as db:
        installed = db.execute(
            "SELECT name,default_version,installed_version FROM pg_available_extensions WHERE name IN ('vector','vectorscale') ORDER BY name"
        ).fetchall()
        print(installed)
        assert any(r[0] == "vector" for r in installed)
        if not any(r[0] == "vectorscale" for r in installed):
            print(
                "Optional vectorscale is unavailable in this pinned pgvector image; no StreamingDiskANN result."
            )


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "pgvector")
