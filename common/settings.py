"""Settings are resolved lazily so importing a module has no filesystem side effects."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def setting(name: str, default: str) -> str:
    load_dotenv(ROOT / ".env", override=False)
    return os.environ.get(f"MARLOWE_{name}", default)


def course_path(name: str, default: str) -> Path:
    path = Path(setting(name, default)).expanduser()
    return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()


def data_dir() -> Path:
    return course_path("DATA_DIR", "data")


def cache_dir() -> Path:
    return course_path("CACHE_DIR", ".cache/marlowe")
