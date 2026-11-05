"""Practice: vector-space identity.

Return true only when model, revision, dimensions and preprocessing all match. Missing identity fields cannot establish compatibility.
Run: uv run python modules/20_multimodal/exercises/01_practice.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(a, b):
    # YOUR CODE HERE: improve the baseline to meet every criterion.
    return a.get("dimensions") == b.get("dimensions")


def main() -> None:
    print(
        solve(
            *[
                {"model": "A", "revision": "1", "dimensions": 2, "preprocessing": "unit"},
                {"model": "B", "revision": "1", "dimensions": 2, "preprocessing": "unit"},
            ]
        )
    )


if __name__ == "__main__":
    main()
