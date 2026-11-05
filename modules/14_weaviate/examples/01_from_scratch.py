"""Trace how hybrid alpha changes the first product.

Run: uv run python modules/14_weaviate/examples/01_from_scratch.py
Concepts: Trace how hybrid alpha changes the first product.
Expected: alpha changes the winning title.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""


def combine(dense, lexical, alpha):
    if not 0 <= alpha <= 1:
        raise ValueError("alpha outside [0,1]")

    def scale(values):
        lo, hi = min(values), max(values)
        return [(v - lo) / (hi - lo) if hi > lo else 0 for v in values]

    return [
        alpha * vector + (1 - alpha) * term
        for vector, term in zip(scale(dense), scale(lexical), strict=True)
    ]


def main() -> None:
    # KEY IDEA: Trace how hybrid alpha changes the first product.
    titles = ["SKU exact match", "semantic alternative", "unrelated"]
    for alpha in [0, 0.5, 1]:
        scores = combine([0.35, 0.95, 0.1], [8, 2, 0], alpha)
        print(alpha, titles[scores.index(max(scores))], scores)
    assert combine([0, 1], [1, 0], 1) == [0, 1]


if __name__ == "__main__":
    main()
