"""Use the official Qdrant TypeScript client on genuine frozen vectors.
Concepts: serialization and native clients.
Run: uv run python modules/bonus/B1_other_languages/examples/02_production.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""
# course-profile: qdrant

from common.bonus import typescript
from common.research import record


def main() -> None:
    result = typescript("qdrant")
    print(result)
    print(
        record(
            "typescript-qdrant",
            result,
            "python modules/bonus/B1_other_languages/examples/02_production.py",
        )
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
