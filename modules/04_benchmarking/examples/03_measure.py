"""Run a repeatable TinyVec benchmark from a strict configuration.

Concepts: warmup, repetitions, provenance, quality and timing separation.
Run: uv run python modules/04_benchmarking/examples/03_measure.py
Expected: 100 queries x 5 repeats; saved raw run and summary
CPU: about 10–30 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

from common.bench.config import load_config
from common.bench.runner import run_benchmark
from common.settings import ROOT, cache_dir


def main() -> None:
    config = load_config(ROOT / "configs/bench/benchmark_method.yaml")
    # KEY IDEA: loading and embedding are outside the retrieval timer; the raw report states the scope.
    result = run_benchmark(config, cache_dir() / "tier1" / "example-benchmarks")
    print(result["run_id"], result["summary"])
    assert result["summary"]["samples"] == result["query_count"] * config.repetitions
    assert result["summary"]["recall_at_k"] == 1.0


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
