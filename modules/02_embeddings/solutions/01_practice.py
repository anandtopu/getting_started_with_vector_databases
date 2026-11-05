"""Key cached embeddings by content and complete model identity.

Run: uv run python modules/02_embeddings/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py modules/02_embeddings/solutions/01_practice.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

from common.io import digest


def solve(text: str, spec: dict, role: str) -> str:
    # KEY IDEA: this reference implements the stated acceptance policy.
    return digest({"content": text, "spec": spec, "role": role})


def main() -> None:
    print(solve("coffee", {"revision": "one", "dimensions": 3}, "query"))


if __name__ == "__main__":
    main()
