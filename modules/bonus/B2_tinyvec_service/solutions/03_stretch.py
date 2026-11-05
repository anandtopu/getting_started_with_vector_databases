"""Return the complete newline-terminated prefix of a WAL string. Do not silently repair a corrupt complete record.
Run: uv run python modules/bonus/B2_tinyvec_service/solutions/03_stretch.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(data):
    position = data.rfind("\n")
    return data[: position + 1] if position >= 0 else ""


def main() -> None:
    print(solve(*["a\nb\npartial"]))


if __name__ == "__main__":
    main()
