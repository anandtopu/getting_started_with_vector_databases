"""Trust the server principal.
Return sorted IDs for [id,tenant] rows belonging to the trusted principal. An empty principal sees nothing.
Run: uv run python modules/23_security_reliability/exercises/01_practice.py
CPU: under a second; no downloads or services.
Acceptance: uv run python scripts/check_exercise.py modules/23_security_reliability/exercises/01_practice.py
"""


def solve(principal_tenant, rows):
    # YOUR CODE HERE: replace the runnable placeholder.
    return None


def main():
    print(solve(*["a", [["x", "a"], ["y", "b"]]]))


if __name__ == "__main__":
    main()
