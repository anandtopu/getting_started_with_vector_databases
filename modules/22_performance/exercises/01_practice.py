"""Vector capacity arithmetic.
Return raw vector bytes for positive integer inputs. This deliberately excludes metadata, graph links and headroom; return 0 if any input is nonpositive.
Run: uv run python modules/22_performance/exercises/01_practice.py
CPU: under a second; no downloads or services.
Acceptance: uv run python scripts/check_exercise.py modules/22_performance/exercises/01_practice.py
"""


def solve(rows, dimensions, width, replicas):
    # YOUR CODE HERE: replace the runnable placeholder.
    return None


def main():
    print(solve(*[10000000, 768, 4, 2]))


if __name__ == "__main__":
    main()
