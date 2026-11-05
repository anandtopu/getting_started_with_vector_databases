"""Serve the authenticated application on loopback HTTPS.
Run: uv run --extra apps python scripts/serve_tier5.py
Prepare TLS and identities once with scripts/prepare_tier5.py. No model downloads.
"""

import argparse

from common.errors import CourseError, run_cli
from common.settings import cache_dir


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8443)
    args = parser.parse_args()
    root = cache_dir() / "tier5/runtime"
    if not (root / "tls/server.pem").exists() or not (root / "identities.json").exists():
        raise CourseError("Run uv run --extra ops python scripts/prepare_tier5.py first")
    uvicorn.run(
        "common.apps.secure_api:app",
        host="127.0.0.1",
        port=args.port,
        ssl_certfile=str(root / "tls/server.pem"),
        ssl_keyfile=str(root / "tls/server-key.pem"),
        access_log=False,
    )


if __name__ == "__main__":
    run_cli(main)
