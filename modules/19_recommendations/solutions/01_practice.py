"""Practice: split before profiling.

Return only events strictly earlier than the cutoff and with recognized positive actions. Do not include future purchases.
Run: uv run python modules/19_recommendations/solutions/01_practice.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(events, cutoff):
    # KEY IDEA: Return only events strictly earlier than the cutoff and with recognized positive actions.
    return [
        e for e in events if e["timestamp"] < cutoff and e["action"] in {"view", "cart", "purchase"}
    ]


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
