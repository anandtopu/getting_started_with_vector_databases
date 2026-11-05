"""Runnable starting point for Capstone 05.
Run: uv run python capstones/05_marlowe_search/starter/project.py
Expected: a working baseline, not completed acceptance. CPU: seconds.
Needs: included vectors; no downloads, credentials or containers.
"""

from common.apps.marlowe import MarloweSearch


def main() -> None:
    service = MarloweSearch("tinyvec", limit=100)
    try:
        # YOUR CODE HERE: integrate trusted identity, TLS database, UI and operational evidence.
        print([h.id for h in service.search().hits])
        print("Local v5 baseline; complete v6 security before exposing seller traffic.")
    finally:
        service.close()


if __name__ == "__main__":
    main()
