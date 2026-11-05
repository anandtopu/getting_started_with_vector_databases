"""Reconcile delivered teaching files, feature configs, raw results and reference guides.

Run: uv run python scripts/audit_delivery.py
CPU: seconds. Offline structural/evidence audit; not a substitute for execution or review.
"""

import json
import re
from datetime import UTC, datetime

import yaml

from common.io import atomic_json, file_hash
from common.settings import ROOT


def main() -> None:
    failures = []
    modules = [
        *sorted((ROOT / "modules").glob("[0-9][0-9]_*")),
        *sorted((ROOT / "modules/bonus").glob("B[1-4]_*")),
    ]
    capstones = sorted((ROOT / "capstones").glob("[0-9][0-9]_*"))
    inventory = {}
    for folder in [*modules, *capstones]:
        inventory[folder.relative_to(ROOT).as_posix()] = sorted(
            p.relative_to(ROOT).as_posix()
            for p in folder.rglob("*")
            if p.is_file() and not {"node_modules", "dist", "__pycache__"}.intersection(p.parts)
        )
    for folder in capstones:
        for name in [
            "README.md",
            "architecture.md",
            "starter/project.py",
            "solution/project.py",
            "evaluation.yaml",
            "rubric.md",
            "extensions.md",
            "results/README.md",
        ]:
            if not (folder / name).exists():
                failures.append(f"Missing {folder.name}/{name}")
        evaluation = yaml.safe_load((folder / "evaluation.yaml").read_text())
        if not (folder / evaluation["acceptance"]).exists():
            failures.append(f"Missing capstone acceptance: {folder.name}")
    feature_map = (ROOT / "docs/FEATURE_MAP.md").read_text(encoding="utf8")
    leaderboard = (ROOT / "results/leaderboard.md").read_text(encoding="utf8")
    coverage = {}
    for path in sorted((ROOT / "configs/bench").glob("*.yaml")):
        config = yaml.safe_load(path.read_text())
        if "feature" not in config:
            continue
        feature = config["feature"]
        evidence = sorted((ROOT / "results/features").glob(feature + "-*.json"))
        coverage[feature] = [p.relative_to(ROOT).as_posix() for p in evidence]
        if (
            not evidence
            or f"#{feature})" not in feature_map
            or f'id="{feature}"' not in leaderboard
        ):
            failures.append(f"Feature lacks config/map/result alignment: {feature}")
        for role in ["example", "native"]:
            if not (ROOT / "modules" / config["lesson"] / config[role]).exists():
                failures.append(f"Missing {feature} {role}")
        if evidence:
            latest = json.loads(evidence[-1].read_text(encoding="utf8"))
            if {r["role"] for r in latest["observations"]} != {"example", "native"}:
                failures.append(f"Incomplete observations: {feature}")
    terms = len(
        re.findall(r"^\*\*.+?\.\*\*", (ROOT / "docs/GLOSSARY.md").read_text(encoding="utf8"), re.M)
    )
    retrieval_coverage = {}
    runs = [
        (p, json.loads(p.read_text(encoding="utf8")))
        for p in (ROOT / "results/runs").glob("*.json")
    ]
    for name in sorted(set(re.findall(r"\.\./configs/bench/([^)#]+\.yaml)", feature_map))):
        config = yaml.safe_load((ROOT / "configs/bench" / name).read_text())
        if "feature" in config:
            continue
        matched = [
            p.relative_to(ROOT).as_posix()
            for p, run in runs
            if run.get("config", {}).get("name") == config.get("name")
        ]
        retrieval_coverage[name] = matched
        if not matched:
            failures.append(f"Mapped retrieval config lacks a raw run: {name}")
    if terms < 80:
        failures.append("Glossary needs at least 80 terms")
    sheets = ["tier_1", "tier_2", "tier_3", "tier_4", "tier_5", "index_types", "database_apis"]
    for sheet in sheets:
        if (
            not (ROOT / f"cheatsheets/{sheet}.md").exists()
            or not (ROOT / f"output/pdf/{sheet}.pdf").exists()
        ):
            failures.append(f"Missing printable sheet: {sheet}")
    report = {
        "created_at": datetime.now(UTC).isoformat(),
        "modules": len(modules),
        "capstones": len(capstones),
        "glossary_terms": terms,
        "printable_sheets": len(sheets),
        "files": inventory,
        "file_sha256": {
            name: file_hash(ROOT / name) for names in inventory.values() for name in names
        },
        "feature_evidence": coverage,
        "mapped_retrieval_evidence": retrieval_coverage,
        "failures": failures,
        "scope": "Offline structure and evidence reconciliation, not runtime or remote CI verification",
    }
    atomic_json(ROOT / "results/bonus/delivery-inventory.json", report)
    print(
        {
            k: v
            for k, v in report.items()
            if k not in {"files", "file_sha256", "feature_evidence", "mapped_retrieval_evidence"}
        }
    )
    if failures:
        raise SystemExit("Delivery audit found gaps")


if __name__ == "__main__":
    main()
