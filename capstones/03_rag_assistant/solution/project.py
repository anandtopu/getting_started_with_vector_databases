"""Evidence-first help assistant with a chosen database, abstention and evaluation.
Run: uv run python capstones/03_rag_assistant/solution/project.py --backend tinyvec
Expected: cited source excerpts plus a passage-recall report. CPU: seconds to minutes.
Needs: included MiniLM help vectors; --generate explicitly requires local Ollama.
"""

import argparse
import re

from common.apps.database import AppDatabase
from common.apps.evaluation import rag_evaluation
from common.errors import run_cli
from common.research import record
from common.tier4 import open_rag


class HelpProject:
    def __init__(self, backend="tinyvec"):
        self.database = AppDatabase(backend)
        try:
            self.rag, self.questions, self.vectors = open_rag(self.database)
        except BaseException:
            self.database.close()
            raise

    def ask(self, question_id="rag-000", generate=False):
        question = next((q for q in self.questions if q["id"] == question_id), None)
        if question is None:
            raise ValueError("Choose a saved help question")
        hits = self.rag.retrieve(question["question"], self.vectors[question_id])
        if generate:
            return self.rag.answer(question["question"], hits)
        evidence = [h for h in hits if h.score >= 0.35]
        if not evidence:
            return {
                "answer": "I do not have enough evidence.",
                "citations": [],
                "mode": "abstention",
            }
        first = evidence[0]
        body = first.text.split("\n", 1)[-1]
        excerpt = " ".join(re.split(r"(?<=[.!?])\s+", body)[:2])
        citation = first.metadata["passage_id"]
        return {
            "answer": excerpt + f" [{citation}]",
            "citations": [citation],
            "mode": "source_excerpt",
            "evidence": first.text,
            "limits": "Textual support does not establish that retrieval chose the correct policy",
        }

    def close(self):
        self.database.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="tinyvec")
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    project = HelpProject(args.backend)
    try:
        sample = project.ask(generate=args.generate)
        observations = rag_evaluation(project.database, generate=args.generate)
        print(sample)
        print(
            record(
                "capstone-rag",
                {"backend": args.backend, "sample": sample, "evaluation": observations},
                "python capstones/03_rag_assistant/solution/project.py --backend "
                + args.backend
                + (" --generate" if args.generate else ""),
            )
        )
    finally:
        project.close()


if __name__ == "__main__":
    run_cli(main)
