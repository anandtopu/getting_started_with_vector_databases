"""Reject equally sized vectors from incompatible spaces.

Run: uv run python modules/02_embeddings/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/02_embeddings/solutions/03_stretch.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

from common.embeddings import EmbeddingSpec


def solve(left: dict, right: dict) -> bool:
    # KEY IDEA: this reference implements the stated acceptance policy.
    return EmbeddingSpec(**left).space == EmbeddingSpec(**right).space


def main() -> None:
    print(solve({"dimensions": 384}, {"dimensions": 384}))


if __name__ == "__main__":
    main()
