"""Query vector, halfvec and bit data inside a PostgreSQL transaction.

Run: uv run --extra pgvector python modules/12_pgvector/examples/02_production.py
Concepts: Query vector, halfvec and bit data inside a PostgreSQL transaction.
Expected: SQL join, halfvec, Hamming distance and rollback.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the pgvector profile first.
"""

# course-extra: pgvector
# course-profile: pgvector
import psycopg

from common.settings import setting
from common.teaching import catalog


def main() -> None:
    # KEY IDEA: Query vector, halfvec and bit data inside a PostgreSQL transaction.
    products, matrix, q, _ = catalog(160)
    with psycopg.connect(
        setting("POSTGRES_URL", "postgresql://marlowe:marlowe-local@127.0.0.1:5432/marlowe")
    ) as db:
        db.execute("CREATE EXTENSION IF NOT EXISTS vector")
        db.execute("CREATE TEMP TABLE sellers(id text PRIMARY KEY, enabled boolean)")
        db.execute(
            "CREATE TEMP TABLE items(id text PRIMARY KEY,seller text,v vector(384),price float8)"
        )
        with db.cursor() as c:
            c.executemany(
                "INSERT INTO sellers VALUES (%s,true)",
                [(k,) for k in sorted(set(products.seller_id))],
            )
            c.executemany(
                "INSERT INTO items VALUES (%s,%s,%s::vector,%s)",
                [
                    (p.id, p.seller_id, str(v.tolist()), p.price)
                    for p, v in zip(products.itertuples(), matrix, strict=True)
                ],
            )
        db.execute("CREATE INDEX graph ON items USING hnsw(v vector_cosine_ops)")
        db.execute("SET LOCAL hnsw.iterative_scan='strict_order'")
        query = str(q.tolist())
        sql = "SELECT i.id,i.v <=> %s::vector AS cosine,i.v::halfvec(384) <-> %s::halfvec AS half_l2,binary_quantize(i.v) <~> binary_quantize(%s::vector) AS hamming FROM items i JOIN sellers s ON s.id=i.seller WHERE s.enabled AND i.price<50 ORDER BY cosine LIMIT 5"
        result = db.execute(sql, (query, query, query)).fetchall()
        db.execute("SAVEPOINT before_delete")
        db.execute("DELETE FROM items")
        db.execute("ROLLBACK TO before_delete")
        db.execute("CREATE INDEX lists ON items USING ivfflat(v vector_cosine_ops) WITH (lists=4)")
        print(
            result,
            db.execute(
                "EXPLAIN SELECT id FROM items ORDER BY v <=> %s::vector LIMIT 5", (query,)
            ).fetchall(),
        )
        assert result and db.execute("SELECT count(*) FROM items").fetchone()[0] == 160


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "pgvector")
