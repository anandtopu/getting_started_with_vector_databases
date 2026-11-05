"""Authorize actions.
Return true only for reader:read, writer:read/write, admin:read/write/admin. Unknown roles and actions are denied.
Run: uv run python modules/23_security_reliability/exercises/02_apply.py
CPU: under a second; no downloads or services.
Acceptance: uv run python scripts/check_exercise.py modules/23_security_reliability/exercises/02_apply.py
"""


def solve(role, action):
    # YOUR CODE HERE: replace the runnable placeholder.
    return None


def main():
    print(solve(*["reader", "read"]))


if __name__ == "__main__":
    main()
