"""Authenticated reference API, with tenant identity resolved on the server.
Run: uv run --extra apps python scripts/serve_tier5.py
Expected: HTTPS on localhost:8443. CPU: seconds; prepare Tier 5 credentials first.
"""

from common.apps.secure_api import create_app

app = create_app()


def main() -> None:
    from scripts.serve_tier5 import main as serve

    serve()


if __name__ == "__main__":
    main()
