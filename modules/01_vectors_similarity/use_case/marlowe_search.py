"""Recommend a product using deliberately designed features.

Concepts: metric choice, explainable feature scale.
Run: uv run python modules/01_vectors_similarity/use_case/marlowe_search.py
Expected: cosine picks a reading chair, exposing a flaw in the designed features
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

from common.teaching import hand_features
from tinyvec.exact import exact_knn


def main() -> None:
    ids, vectors, _ = hand_features()
    ranked = exact_knn(vectors[1:], vectors[0], ids[1:], 3, "cosine")
    assert ranked[0][0] == "reading-chair"
    print("Cosine alternatives:", ranked)
    print(
        "Surprise: chair direction looks close because portability is zero. These features omit heating technology."
    )
    print(
        "Product decision: redesign features or learn embeddings before shipping recommendations."
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
