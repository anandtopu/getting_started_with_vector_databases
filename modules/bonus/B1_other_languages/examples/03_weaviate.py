"""Repeat CRUD, replacement, scope and deletion through the official Weaviate client.
Concepts: serialization and native clients.
Run: uv run python modules/bonus/B1_other_languages/examples/03_weaviate.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""
# course-profile: weaviate

from common.bonus import typescript
from common.research import record


def main() -> None:
    result = typescript("weaviate")
    print(result)
    print(
        record(
            "typescript-weaviate",
            result,
            "python modules/bonus/B1_other_languages/examples/03_weaviate.py",
        )
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
