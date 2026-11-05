"""Build overlapping chunks while retaining an article's citation identity.

Run: uv run  python modules/18_rag/examples/01_from_scratch.py
Expected: overlapping windows share help-000#procedure.
CPU: seconds to one minute. Needs: base, help articles. No implicit downloads.
"""

from common.apps.rag import chunk_article
from common.settings import data_dir


def main() -> None:
    path = data_dir() / "help_center/help-000.md"
    # KEY IDEA: window IDs distinguish chunks, but citations refer to stable passages.
    windows = chunk_article(path, words=20, overlap=5)
    for chunk in windows:
        print(chunk.id, chunk.passage_id, chunk.text)
    assert len(windows) > 1
    assert len({c.passage_id for c in windows}) == 1


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
