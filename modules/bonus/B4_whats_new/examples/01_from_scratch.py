"""Estimate distances with one-bit RaBitQ and an explicit correction term.
Concepts: rotation, quantization and rescoring.
Run: uv run python modules/bonus/B4_whats_new/examples/01_from_scratch.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""

import numpy as np
from threadpoolctl import threadpool_limits

from tinyvec.rabitq import RaBitQ


def main() -> None:
    vectors = np.random.default_rng(42).normal(size=(500, 64)).astype(np.float32)
    with threadpool_limits(limits=1):
        index = RaBitQ(vectors)
        estimated = index.distances(vectors[0])
    assert abs(estimated[0]) < 1e-3
    print(
        {
            "first_candidates": np.argsort(estimated)[:5].tolist(),
            "code_and_rotation_bytes": index.payload_bytes,
            "self_distance": float(estimated[0]),
        }
    )
    print("Dense unpacking teaches the estimator; it is not a SIMD implementation.")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
