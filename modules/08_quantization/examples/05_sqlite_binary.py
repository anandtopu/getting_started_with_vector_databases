"""Compute a binary distance using sqlite-vec.

Run: uv run --extra embedded python modules/08_quantization/examples/05_sqlite_binary.py
Expected: compare the reported ranking and verify the final assertion.
CPU: seconds, included data, no Docker or model downloads.
"""

# course-extra: embedded
import sqlite3

import sqlite_vec

from common.index_lessons import unit_catalog


def main():
    _, matrix, q = unit_catalog(64)
    with sqlite3.connect(":memory:") as db:
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        value = db.execute(
            "select vec_distance_hamming(vec_quantize_binary(?),vec_quantize_binary(?))",
            (matrix[0].tobytes(), q.tobytes()),
        ).fetchone()[0]
        print("different sign bits", value)
        assert 0 <= value <= matrix.shape[1]


if __name__ == "__main__":
    main()
