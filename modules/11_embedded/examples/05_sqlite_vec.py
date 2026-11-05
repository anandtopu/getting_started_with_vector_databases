"""Join native SQLite vector scores to catalog metadata.

Run: uv run --extra embedded python modules/11_embedded/examples/05_sqlite_vec.py
Concepts: Join native SQLite vector scores to catalog metadata.
Expected: five SQLite distances.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

# course-extra: embedded
import sqlite3

import sqlite_vec

from common.teaching import catalog


def main() -> None:
    # KEY IDEA: Join native SQLite vector scores to catalog metadata.
    rows, matrix, q, _ = catalog(80)
    with sqlite3.connect(":memory:") as db:
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        db.execute("CREATE TABLE products(id TEXT PRIMARY KEY, region TEXT, v BLOB)")
        db.executemany(
            "INSERT INTO products VALUES (?,?,?)",
            [(p.id, p.region, v.tobytes()) for p, v in zip(rows.itertuples(), matrix, strict=True)],
        )
        hits = db.execute(
            "SELECT id,vec_distance_cosine(v,?) FROM products WHERE region=? ORDER BY 2,id LIMIT 5",
            (q.tobytes(), "north"),
        ).fetchall()
        print(hits)
        assert hits and all(rows.set_index("id").loc[k, "region"] == "north" for k, _ in hits)


if __name__ == "__main__":
    main()
