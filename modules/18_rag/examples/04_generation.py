"""Generate a cited answer using only retrieved policy evidence and local Ollama.

Run: uv run --extra rag python modules/18_rag/examples/04_generation.py
Expected: an answer plus citations and a separate unresolved faithfulness field.
CPU: seconds to one minute. Needs: rag extra, local Ollama qwen3:0.6b, prepared help vectors. No implicit downloads.
"""
# course-extra: rag
# course-profile: ollama

from common.apps.database import AppDatabase
from common.teaching import evidence
from common.tier4 import open_rag


def main() -> None:
    with AppDatabase() as db:
        rag, questions, queries = open_rag(db)
        q = questions[0]
        hits = rag.retrieve(q["question"], queries[q["id"]])
        # KEY IDEA: a valid source ID does not establish that the claim is supported.
        result = rag.answer(q["question"], hits)
    print(result)
    evidence("rag-generation", result, tier=4)


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "ollama")
