"""Find a visible product revision.
Run: uv run python modules/15_milvus/solutions/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(events, watermark):
    seen = [r for r in events if r[0] <= watermark]
    return max(seen, key=lambda r: r[0])[1] if seen else None


def main() -> None:
    print(solve([[1, "sale"], [3, "retired"]], 2))


if __name__ == "__main__":
    main()
