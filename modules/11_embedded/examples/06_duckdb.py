"""Compare exact array SQL with an explicitly prepared VSS index.

Run: uv run --extra embedded python modules/11_embedded/examples/06_duckdb.py
Concepts: Compare exact array SQL with an explicitly prepared VSS index.
Expected: exact SQL and optional HNSW scan.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

# course-extra: embedded
import duckdb

from common.settings import cache_dir
from common.teaching import catalog


def main() -> None:
    # KEY IDEA: Compare exact array SQL with an explicitly prepared VSS index.
    products, matrix, q, _ = catalog(160)
    ext = cache_dir() / "tier3/duckdb-extensions"
    ext.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(
        config={
            "extension_directory": str(ext),
            "autoload_known_extensions": False,
            "autoinstall_known_extensions": False,
        }
    ) as db:
        db.execute("CREATE TABLE p(id VARCHAR,v FLOAT[384])")
        db.executemany(
            "INSERT INTO p VALUES (?,?)", list(zip(products.id, matrix.tolist(), strict=True))
        )
        sql = "SELECT id FROM p ORDER BY array_cosine_distance(v,?::FLOAT[384]) LIMIT 5"
        exact = db.execute(sql, [q.tolist()]).fetchall()
        print("SQL exact", exact)
        if db.execute(
            "SELECT installed FROM duckdb_extensions() WHERE extension_name='vss'"
        ).fetchone()[0]:
            db.execute("LOAD vss")
            db.execute("CREATE INDEX vectors ON p USING HNSW(v) WITH (metric='cosine')")
            print(
                db.execute("EXPLAIN " + sql, [q.tolist()]).fetchone()[1],
                db.execute(sql, [q.tolist()]).fetchall(),
            )
        else:
            print("VSS optional: run scripts/prepare_duckdb_vss.py to install its signed extension")
        assert len(exact) == 5


if __name__ == "__main__":
    main()
