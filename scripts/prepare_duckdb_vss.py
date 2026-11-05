"""Explicitly install the signed matching DuckDB VSS extension into the course cache.
Run: uv run --extra embedded python scripts/prepare_duckdb_vss.py
CPU: seconds. First run needs network access. No Docker.
"""

import duckdb

from common.settings import cache_dir


def main():
    directory = cache_dir() / "tier3/duckdb-extensions"
    directory.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(config={"extension_directory": str(directory)}) as conn:
        conn.execute("INSTALL vss")
        conn.execute("LOAD vss")
        print(
            conn.execute(
                "SELECT extension_name,installed,loaded FROM duckdb_extensions() WHERE extension_name='vss'"
            ).fetchone()
        )


if __name__ == "__main__":
    main()
