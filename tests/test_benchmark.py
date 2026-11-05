import json

from common.bench.config import BenchConfig
from common.bench.leaderboard import write_leaderboard
from common.bench.runner import run_benchmark
from common.bench.sweep import expand_sweep


def test_benchmark_records_evidence_and_filtered_ground_truth(tmp_path):
    config = BenchConfig(
        name="test-run", limit=100, queries=6, repetitions=2, warmup=2, split="all"
    )
    report = run_benchmark(config, tmp_path)
    assert report["summary"]["recall_at_k"] == 1
    assert report["summary"]["samples"] == 12
    assert report["summary"]["qps"] > 0
    assert report["summary"]["persisted_bytes"] > 0
    assert report["hardware"]["ram_bytes"] > 0
    assert report["provenance"]["source_hash"]
    saved = json.loads(next((tmp_path / "runs").glob("*.json")).read_text())
    assert saved["config"] == config.model_dump()
    assert "test-run" in write_leaderboard(tmp_path).read_text()
    assert len(expand_sweep(config, {"parameters.block_size": [10, 20], "k": [3, 5]})) == 4
