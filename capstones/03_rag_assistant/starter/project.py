"""Runnable starting point for Capstone 03.
Run: uv run python capstones/03_rag_assistant/starter/project.py
Expected: a working baseline, not completed acceptance. CPU: seconds.
Needs: included vectors; no downloads, credentials or containers.
"""

from common.apps.database import AppDatabase
from common.tier4 import open_rag


def main() -> None:
    with AppDatabase("tinyvec") as database:
        rag, questions, vectors = open_rag(database)
        question = questions[0]
        hits = rag.retrieve(question["question"], vectors[question["id"]])
        # YOUR CODE HERE: deliver cited evidence, abstain and evaluate policy correctness.
        print([(h.metadata["passage_id"], h.score) for h in hits])


if __name__ == "__main__":
    main()
