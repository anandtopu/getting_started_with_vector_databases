"""Compare FAISS flat, rotated one-bit and four-bit RaBitQ.
Concepts: rotation, quantization and rescoring.
Run: uv run python modules/bonus/B4_whats_new/examples/02_production.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""
# course-extra: libs

from common.research import rabitq_experiment, record


def main() -> None:
    result = rabitq_experiment(native=True)
    print(result["native"])
    print(
        record(
            "rabitq-native", result, "python modules/bonus/B4_whats_new/examples/02_production.py"
        )
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
