"""Reject benchmark comparisons that changed the workload.

Run: uv run python modules/16_landscape/examples/01_from_scratch.py
Concepts: Reject benchmark comparisons that changed the workload.
Expected: mismatched comparison inputs.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""


def differences(first, second):
    return [
        key
        for key in ("dataset", "queries", "k", "metric", "concurrency", "hardware", "recall_target")
        if first.get(key) != second.get(key)
    ]


def main() -> None:
    # KEY IDEA: Reject benchmark comparisons that changed the workload.
    a = {
        "dataset": "Marlowe 500",
        "queries": "test",
        "k": 10,
        "metric": "cosine",
        "concurrency": 1,
        "hardware": "same laptop",
        "recall_target": 0.95,
    }
    b = {**a, "concurrency": 16, "recall_target": 0.8}
    print("incompatible fields", differences(a, b))
    assert differences(a, b) == ["concurrency", "recall_target"]


if __name__ == "__main__":
    main()
