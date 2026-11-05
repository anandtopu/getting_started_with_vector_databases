"""Practice: split before profiling.

Return only events strictly earlier than the cutoff and with recognized positive actions. Do not include future purchases.
Run: uv run python modules/19_recommendations/exercises/01_practice.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(events, cutoff):
    # YOUR CODE HERE: improve the baseline to meet every criterion.
    return list(events)


def main() -> None:
    print(
        solve(
            *[
                [
                    {"timestamp": "2025-01-01", "action": "view"},
                    {"timestamp": "2025-02-01", "action": "purchase"},
                ],
                "2025-02-01",
            ]
        )
    )


if __name__ == "__main__":
    main()
