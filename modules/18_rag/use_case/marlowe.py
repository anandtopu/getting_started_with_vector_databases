"""Use the integrated Marlowe application in a realistic customer flow.

Run: uv run  python modules/18_rag/use_case/marlowe.py
Expected: retrieved products or cited policy passages.
CPU: seconds to one minute. Needs: base, prepared Tier 4 artifacts. No implicit downloads.
"""

from common.apps.marlowe import MarloweSearch


def main() -> None:
    with MarloweSearch() as app:
        # KEY IDEA: expose the actual evidence even when local generation is off.
        result = app.help(question_id="rag-000")
        for hit in result["passages"]:
            print(hit.metadata["passage_id"], hit.text)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
