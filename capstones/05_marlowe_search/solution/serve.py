"""Run the flagship API against the TLS-protected Qdrant server.
Run: uv run --extra apps --extra qdrant python capstones/05_marlowe_search/solution/serve.py
Expected: HTTPS localhost:8443. CPU: seconds; prepare/start the advanced stack first.
"""

import os


def main() -> None:
    os.environ.setdefault("MARLOWE_APP_BACKEND", "qdrant-secure")
    from scripts.serve_tier5 import main as serve

    serve()


if __name__ == "__main__":
    main()
