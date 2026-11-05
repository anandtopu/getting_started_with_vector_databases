"""Compare an acknowledged write with native SQLite transaction recovery.
Concepts: durability and replay.
Run: uv run python modules/bonus/B2_tinyvec_service/examples/02_production.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""

import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from pathlib import Path


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "native.db"
        code = "import sqlite3,sys,os; d=sqlite3.connect(sys.argv[1]); d.execute('PRAGMA journal_mode=WAL'); d.execute('PRAGMA synchronous=FULL'); d.execute('CREATE TABLE records(id TEXT PRIMARY KEY,value TEXT)'); d.execute(\"INSERT INTO records VALUES ('a','committed')\"); d.commit(); os._exit(23)"
        child = subprocess.run([sys.executable, "-c", code, str(path)], check=False)
        assert child.returncode == 23
        with closing(sqlite3.connect(path)) as db:
            assert db.execute("SELECT value FROM records").fetchone()[0] == "committed"
        print("SQLite committed row survived abrupt process exit; no power-loss claim")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
