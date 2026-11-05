"""Evaluate Marlowe v2–v5 on one database and save append-only evidence.
Run: uv run --extra qdrant python scripts/checkpoint_tier4.py --backend qdrant-local
Add --generate for a running local Ollama, and --rerank for the cached cross encoder.
CPU: minutes. No implicit downloads or container startup.
"""

import argparse
import uuid
from datetime import UTC, datetime

from common.apps.database import AppDatabase
from common.apps.evaluation import (
    multilingual_evaluation,
    photo_evaluation,
    rag_evaluation,
    recommendation_evaluation,
    search_evaluation,
)
from common.bench.hardware import hardware, provenance
from common.errors import run_cli
from common.io import atomic_json, file_hash
from common.settings import ROOT, data_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="tinyvec")
    parser.add_argument(
        "--part",
        choices=["all", "search", "multilingual", "rag", "recommendations", "photo"],
        default="all",
    )
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--rerank", action="store_true")
    args = parser.parse_args()
    parts = {
        "search": lambda db: search_evaluation(db, rerank=args.rerank),
        "multilingual": multilingual_evaluation,
        "rag": lambda db: rag_evaluation(db, generate=args.generate),
        "recommendations": recommendation_evaluation,
        "photo": photo_evaluation,
    }
    for name, evaluate in parts.items():
        if args.part not in {"all", name}:
            continue
        print("Evaluating", name, flush=True)
        with AppDatabase(args.backend) as database:
            observations = evaluate(database)
        result = {
            "created_at": datetime.now(UTC).isoformat(),
            "backend": args.backend,
            "part": name,
            "command": f"python scripts/checkpoint_tier4.py --backend {args.backend} --part {name}"
            + (" --generate" if args.generate else "")
            + (" --rerank" if args.rerank else ""),
            "hardware": hardware(),
            "provenance": provenance(),
            "artifacts": {
                p.relative_to(ROOT).as_posix(): file_hash(p)
                for p in sorted((data_dir() / "tier4").glob("*"))
                if p.is_file()
            },
            "observations": observations,
        }
        path = ROOT / "results/tier4" / f"{name}-{uuid.uuid4().hex[:8]}.json"
        atomic_json(path, result)
        print(path, flush=True)


if __name__ == "__main__":
    run_cli(main)
