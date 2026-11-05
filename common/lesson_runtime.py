"""Optional packages and local profiles used by standalone lesson and notebook runners."""

import re
import socket
from urllib.parse import urlsplit

from common.errors import CourseError, run_cli
from common.settings import setting

PACKAGES = {
    "ops": "cryptography",
    "embedded": "chromadb",
    "libs": "faiss",
    "hnswlib": "hnswlib",
    "models": "sentence_transformers",
    "pgvector": "psycopg",
    "qdrant": "qdrant_client",
    "weaviate": "weaviate",
    "milvus": "pymilvus",
    "landscape": "elasticsearch",
    "apps": "fastapi",
    "rag": "ollama",
}


def requirements(source):
    extra = re.search(r"^# course-extra: ([\w,]+)", source, re.M)
    profile = re.search(r"^# course-profile: ([\w-]+)", source, re.M)
    return (extra[1].split(",") if extra else []), (profile[1] if profile else None)


def run_server_lesson(main, profile):
    """Fail early with a useful startup command if the advertised port is unavailable."""

    def checked():
        urls = {
            "ollama": ("OLLAMA_URL", "http://127.0.0.1:11434"),
            "pgvector": ("POSTGRES_URL", "postgresql://127.0.0.1:5432"),
            "qdrant-secure": ("SECURE_QDRANT_URL", "https://localhost:6333"),
            "qdrant": ("QDRANT_URL", "http://127.0.0.1:6333"),
            "milvus": ("MILVUS_URL", "http://127.0.0.1:19530"),
            "elasticsearch": ("ELASTICSEARCH_URL", "http://127.0.0.1:9200"),
            "redis": ("REDIS_URL", "redis://127.0.0.1:6379"),
            "mongodb": ("MONGODB_URL", "mongodb://127.0.0.1:27017"),
            "vespa": ("VESPA_URL", "http://127.0.0.1:8081"),
        }
        if profile in urls:
            url = urlsplit(setting(*urls[profile]))
            host, port = url.hostname, url.port or urlsplit(urls[profile][1]).port
        else:
            host = setting("WEAVIATE_HOST", "127.0.0.1")
            port = int(
                setting("GENERATION_PORT", setting("WEAVIATE_PORT", "8080"))
                if profile == "weaviate-generation"
                else setting("WEAVIATE_PORT", "8080")
            )
        try:
            with socket.create_connection((host, port), timeout=2):
                pass
        except OSError as exc:
            raise CourseError(
                f"Cannot reach {profile} at {host}:{port}. Run docker compose -f docker/compose.yaml --profile {profile} up -d and wait for readiness."
            ) from exc
        main()

    run_cli(checked)
