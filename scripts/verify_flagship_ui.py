"""Exercise the secure UI against an owned HTTPS API and real TLS Qdrant.

Run: uv run --extra apps --extra ops --extra qdrant python scripts/verify_flagship_ui.py
CPU: minutes. Requires prepared Tier 5 credentials and the secure database on 6333.
Uses port 8443 only when free; never prints credentials or downloads models.
"""

import json
import socket
import ssl
import subprocess
import sys
import time

from common.research import record
from common.settings import ROOT, cache_dir


def serve() -> None:
    import uvicorn

    from common.apps.secure_api import create_app

    runtime = cache_dir() / "tier5/runtime"
    uvicorn.run(
        create_app(root=cache_dir() / "bonus/ui-server", backend="qdrant-secure", limit=500),
        host="127.0.0.1",
        port=8443,
        access_log=False,
        ssl_certfile=str(runtime / "tls/server.pem"),
        ssl_keyfile=str(runtime / "tls/server-key.pem"),
    )


def main() -> None:
    import httpx
    from streamlit.testing.v1 import AppTest

    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", 8443)) == 0:
            raise RuntimeError("Port 8443 is occupied; stop your own API before this check")
    runtime = cache_dir() / "tier5/runtime"
    identities = json.loads((runtime / "identities.json").read_text())
    token = next(row["token"] for row in identities if row["tenant"] == "seller-000")
    context = ssl.create_default_context(cafile=str(runtime / "tls/ca.pem"))
    log_path = cache_dir() / "bonus/ui-server.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w") as log:
        child = subprocess.Popen(
            [sys.executable, __file__, "--serve"], cwd=ROOT, stdout=log, stderr=log
        )
        try:
            with httpx.Client(verify=context, timeout=2) as client:
                deadline = time.monotonic() + 90
                while time.monotonic() < deadline:
                    if child.poll() is not None:
                        raise RuntimeError("Owned API exited; inspect the private cache log")
                    try:
                        if client.get("https://localhost:8443/health").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.2)
                else:
                    raise TimeoutError("Owned HTTPS API did not become ready")
            app = AppTest.from_file(str(ROOT / "capstones/05_marlowe_search/solution/ui.py"))
            app.run(timeout=60)
            app.text_input[0].set_value(token).run(timeout=60)
            observations = {}
            for flow in ["Products", "Help center", "Similar items", "Listing review", "Photos"]:
                app.radio[0].set_value(flow).run(timeout=60)
                app.button[0].click().run(timeout=90)
                assert not app.exception and not app.error, f"UI flow failed: {flow}"
                assert app.json, f"No response rendered: {flow}"
                observations[flow] = "passed against HTTPS API and TLS Qdrant"
            print(record("flagship-ui", observations, "python scripts/verify_flagship_ui.py"))
        finally:
            child.terminate()
            try:
                child.wait(timeout=20)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=10)


if __name__ == "__main__":
    serve() if "--serve" in sys.argv else main()
