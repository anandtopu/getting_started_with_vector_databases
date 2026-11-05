"""Do not call a generator when there is no eligible evidence.

Run: uv run  python modules/18_rag/examples/05_abstention.py
Expected: abstained=True without a model call.
CPU: seconds to one minute. Needs: base, frozen help vectors. No implicit downloads.
"""

from common.apps.database import AppDatabase
from common.tier4 import open_rag


def main() -> None:
    with AppDatabase() as db:
        rag, _, _ = open_rag(db)

        def forbidden(_):
            raise AssertionError("An empty context must not call the generator")

        # KEY IDEA: abstention is an explicit application outcome.
        result = rag.answer("Will my investment double tomorrow?", [], generate=forbidden)
        assert result["abstained"] and result["generation_ms"] == 0
        print(result)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
