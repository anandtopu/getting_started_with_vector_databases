"""Minimize audit data.
Keep only subject, tenant, action, outcome and request_id from a supplied event. Never copy query, token, text or vector fields.
Run: uv run python modules/23_security_reliability/exercises/03_stretch.py
CPU: under a second; no downloads or services.
Acceptance: uv run python scripts/check_exercise.py modules/23_security_reliability/exercises/03_stretch.py
"""


def solve(event):
    # YOUR CODE HERE: replace the runnable placeholder.
    return None


def main():
    print(
        solve(
            *[
                {
                    "subject": "alice",
                    "tenant": "a",
                    "token": "secret",
                    "query": "private",
                    "outcome": "200",
                }
            ]
        )
    )


if __name__ == "__main__":
    main()
