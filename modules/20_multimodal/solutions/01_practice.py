"""Practice: vector-space identity.

Return true only when model, revision, dimensions and preprocessing all match. Missing identity fields cannot establish compatibility.
Run: uv run python modules/20_multimodal/solutions/01_practice.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(a, b):
    # KEY IDEA: Return true only when model, revision, dimensions and preprocessing all match.
    fields = ["model", "revision", "dimensions", "preprocessing"]
    return all(field in a and field in b and a[field] == b[field] for field in fields)


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
