"""Check local Markdown links; optionally check public HTTP links separately.

Run: uv run python scripts/check_links.py [--online]
No network by default. Future plan paths are code spans, not fabricated links.
"""

import argparse
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

import httpx

from common.io import atomic_json
from common.settings import ROOT


def local_link_errors(root: Path) -> tuple[list[str], set[str]]:
    failures = []
    urls = set()
    files = [
        *root.glob("*.md"),
        *root.glob("docs/**/*.md"),
        *root.glob("examples/**/*.md"),
        *root.glob("data/README.md"),
        *root.glob("results/**/*.md"),
        *root.glob(".github/**/*.md"),
        *root.glob("modules/**/*.md"),
        *root.glob("docker/*.md"),
        *root.glob("common/**/*.md"),
        *root.glob("tinyvec/**/*.md"),
        *root.glob("checkpoints/**/*.md"),
        *root.glob("capstones/**/*.md"),
        *root.glob("cheatsheets/**/*.md"),
    ]
    for path in files:
        if {"node_modules", "dist", "__pycache__"}.intersection(path.parts):
            continue
        text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip("<>")
            if target.startswith(("https://", "http://")):
                urls.add(target)
            elif not target.startswith("mailto:"):
                parsed = urlparse(target)
                local = unquote(parsed.path)
                destination = path.parent / local if local else path
                if not destination.exists():
                    failures.append(f"{path.relative_to(root)}: {target}")
                elif parsed.fragment and destination.suffix == ".md":
                    source = destination.read_text(encoding="utf-8")
                    explicit = set(re.findall(r'<a\s+id="([^"]+)"', source))
                    headings = re.findall(r"^#+ (.+)$", source, re.M)
                    anchors = {
                        re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
                        for heading in headings
                    }
                    if unquote(parsed.fragment) not in anchors | explicit:
                        failures.append(f"{path.relative_to(root)}: missing anchor {target}")
    return failures, urls


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args()
    failures, urls = local_link_errors(ROOT)
    if args.online:
        with httpx.Client(follow_redirects=True, timeout=15) as client:

            def check(url):
                try:
                    response = client.head(url)
                    status = response.status_code
                    if status in {403, 405}:
                        # Some documentation hosts refuse HEAD but serve normal GET requests.
                        with client.stream("GET", url) as response:
                            status = response.status_code
                    return {"url": url, "status": status, "ok": status < 400}
                except httpx.HTTPError as exc:
                    return {"url": url, "error": str(exc), "ok": False}

            with ThreadPoolExecutor(max_workers=6) as pool:
                observations = list(pool.map(check, sorted(urls)))
        atomic_json(
            ROOT / "results/bonus/online-links.json",
            {
                "created_at": datetime.now(UTC).isoformat(),
                "observations": observations,
                "scope": "HTTP reachability from this host; access denial does not prove a missing page",
            },
        )
        failures.extend(
            f"HTTP {row.get('status', row.get('error'))}: {row['url']}"
            for row in observations
            if not row["ok"]
        )
    if failures:
        raise SystemExit("\n".join(failures))
    print(
        f"Local Markdown links passed; {len(urls)} external sources {'checked' if args.online else 'not checked (use --online)'}."
    )


if __name__ == "__main__":
    main()
