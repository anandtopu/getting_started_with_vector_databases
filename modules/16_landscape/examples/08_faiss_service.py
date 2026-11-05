"""Measure native FAISS retrieval through a real loopback HTTP service.

Run: uv run --extra apps --extra libs python modules/16_landscape/examples/08_faiss_service.py
Concepts: Measure native FAISS retrieval through a real loopback HTTP service.
Expected: loopback HTTP timings.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

# course-extra: apps,libs
import socket
import tempfile
import threading
import time
from pathlib import Path

import httpx
import uvicorn

from common.apps.faiss_service import create_app
from common.teaching import catalog, evidence, timed


def main() -> None:
    # KEY IDEA: Measure native FAISS retrieval through a real loopback HTTP service.
    rows, matrix, q, meta = catalog(160)
    with tempfile.TemporaryDirectory() as directory, socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        server = uvicorn.Server(
            uvicorn.Config(create_app(Path(directory), 384, meta["space"]), log_level="error")
        )
        thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 20
            while not server.started:
                if not thread.is_alive() or time.monotonic() > deadline:
                    raise RuntimeError("Local FAISS service failed to start")
                time.sleep(0.05)
            with httpx.Client(base_url=f"http://127.0.0.1:{listener.getsockname()[1]}") as http:
                http.put(
                    "/items",
                    json=[
                        {"id": p.id, "vector": v.tolist(), "text": p.title}
                        for p, v in zip(rows.itertuples(), matrix, strict=True)
                    ],
                ).raise_for_status()

                def query():
                    return (
                        http.post(
                            "/search", json={"vector": q.tolist(), "space": meta["space"], "k": 5}
                        )
                        .raise_for_status()
                        .json()
                    )

                hits = query()
                assert len(hits) == 5
                observation = timed(query)
                http.post("/snapshot").raise_for_status()
                print(hits, observation)
                evidence(
                    "faiss-http",
                    {"loopback_http": observation, "ids": [h["id"] for h in hits]},
                    tier=3,
                )
        finally:
            server.should_exit = True
            thread.join(10)


if __name__ == "__main__":
    main()
