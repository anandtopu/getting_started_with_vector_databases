"""Deploy the teaching schema to the dedicated course Vespa container.
Run: uv run python scripts/deploy_vespa_schema.py
CPU: up to two minutes. Requires the local Vespa profile, no external service.
"""

import io
import time
import zipfile

import httpx

from common.settings import ROOT


def main():
    source = ROOT / "docker/vespa"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for p in source.rglob("*"):
            if p.is_file():
                archive.write(p, p.relative_to(source))
    with httpx.Client(timeout=120) as client:
        config = "http://127.0.0.1:19071"
        deadline = time.monotonic() + 180
        while True:
            try:
                if client.get(config + "/state/v1/health", timeout=3).is_success:
                    break
            except httpx.HTTPError:
                pass
            if time.monotonic() > deadline:
                raise SystemExit(
                    "Vespa config server is unavailable. Check its profile logs and port 19071."
                )
            time.sleep(2)
        existing = client.get(config + "/application/v2/tenant/default/application/")
        existing.raise_for_status()
        if existing.json():
            current = client.get(
                "http://127.0.0.1:8081/document/v1/marlowe/product/docid/course-schema-check"
            )
            if current.status_code == 404 and "product" in current.text:
                print("Course schema already reachable")
                return
            raise RuntimeError(
                "An application already exists; use a fresh dedicated course Vespa profile"
            )
        response = client.post(
            config + "/application/v2/tenant/default/prepareandactivate",
            content=buffer.getvalue(),
            headers={"Content-Type": "application/zip"},
        )
        if not response.is_success:
            raise RuntimeError(response.text)
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            try:
                if client.get("http://127.0.0.1:8081/ApplicationStatus").is_success:
                    print("Vespa application ready")
                    return
            except httpx.HTTPError:
                pass
            time.sleep(2)
        raise TimeoutError("Course Vespa application is starting; check container logs")


if __name__ == "__main__":
    main()
