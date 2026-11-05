"""Compile strict TypeScript and execute the offline contract tests.
Concepts: serialization and native clients.
Run: uv run python modules/bonus/B1_other_languages/examples/04_measure.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""
# course-profile: typescript

from common.bonus import typescript_check


def main() -> None:
    print(typescript_check())


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
