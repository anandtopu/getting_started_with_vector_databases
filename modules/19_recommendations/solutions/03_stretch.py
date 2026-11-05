"""Stretch: calibrate without test leakage.

Return the development threshold maximizing F1. Break ties by higher precision then higher threshold. Test labels are intentionally not an input.
Run: uv run python modules/19_recommendations/solutions/03_stretch.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(scores, labels):
    # KEY IDEA: Return the development threshold maximizing F1.
    from common.apps.deduplication import calibrate

    return calibrate(scores, labels)["threshold"]


def main() -> None:
    print(solve(*[[0.2, 0.4, 0.8, 0.9], [0, 0, 1, 1]]))


if __name__ == "__main__":
    main()
