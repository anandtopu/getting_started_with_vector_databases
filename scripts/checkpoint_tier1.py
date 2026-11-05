"""Verify a saved semantic session in a fresh process and produce a measured checkpoint.

Run: uv run python scripts/checkpoint_tier1.py
CPU: about 10 seconds. Included vectors, no model, external network, or Docker.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from common.apps.search import open_catalog, search_saved
from common.bench.config import load_config
from common.bench.runner import run_benchmark
from common.io import atomic_json
from common.settings import ROOT, cache_dir
from tinyvec import TinyVec


def playground_observation() -> dict:
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "playground/app.py")).run(timeout=60)
    app.button[0].click().run(timeout=60)
    assert not app.exception
    before = app.dataframe[0].value.to_dict("records")
    app.checkbox[0].check()
    app.number_input[0].set_value(30)
    app.button[0].click().run(timeout=60)
    assert not app.exception
    after = app.dataframe[0].value.to_dict("records")
    assert after and all(hit["region"] == "north" and hit["price"] <= 30 for hit in after)
    return {
        "method": "Streamlit interaction runner; no browser screenshot",
        "engine": "tinyvec",
        "products": 1000,
        "query": "q000",
        "k": 5,
        "before": before,
        "filter": {"region": "north", "maximum_price": 30},
        "after": after,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore", type=Path)
    parser.add_argument(
        "--playground",
        action="store_true",
        help="Record a real Streamlit test session; requires --extra apps",
    )
    args = parser.parse_args()
    if args.restore:
        store = TinyVec.load(args.restore)
        try:
            _, hits, _ = search_saved(store)
            expected = json.loads((args.restore / "expected.json").read_text())
            assert [hit.id for hit in hits] == expected
        finally:
            store.close()
        print("Fresh-process restore preserved saved-query IDs.")
        return
    store, _, _ = open_catalog(limit=1000)
    try:
        _, hits, _ = search_saved(store)
        assert all("mug warmer" in hit.metadata["title"] for hit in hits)
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            store.save(directory)
            atomic_json(directory / "expected.json", [hit.id for hit in hits])
            subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--restore", str(directory)],
                check=True,
                cwd=ROOT,
                timeout=60,
            )
    finally:
        store.close()
    output = cache_dir() / "tier1" / "checkpoint"
    result = run_benchmark(load_config(ROOT / "configs/bench/benchmark_method.yaml"), output)
    assert result["summary"]["recall_at_k"] == 1.0
    atomic_json(
        output / "submission.json",
        {
            "restore_verified_in_new_process": True,
            "semantic_hits": [hit.id for hit in hits],
            "benchmark_run": result["run_id"],
            "playground_observation": playground_observation() if args.playground else None,
            "summary": result["summary"],
            "learner_tasks_remaining": [
                "Record a Playground search and filter",
                "Explain relevance versus recall",
                "Complete exercise acceptance checks",
            ],
        },
    )
    print(f"Checkpoint evidence: {output / 'submission.json'}")


if __name__ == "__main__":
    main()
