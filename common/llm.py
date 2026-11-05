"""Local Ollama helper; no hosted-provider fallback and no automatic model pull."""

import httpx

from common.errors import CourseError
from common.settings import setting

OLLAMA_DIGEST = "7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435"


def chat(messages: list[dict[str, str]], *, verify_digest: bool = True) -> str:
    host = setting("OLLAMA_URL", "http://127.0.0.1:11434")
    model = setting("OLLAMA_MODEL", "qwen3:0.6b")
    try:
        import ollama
    except ImportError as exc:
        raise CourseError("Install the local LLM helper: uv sync --extra rag") from exc
    client = ollama.Client(host=host, timeout=120)
    try:
        if verify_digest:
            available = client.list().models
            selected = next((item for item in available if item.model == model), None)
            if selected is None:
                raise CourseError(
                    f"Model missing. Run ollama pull {model} once, then check its digest."
                )
            if model == "qwen3:0.6b" and selected.digest.removeprefix("sha256:") != OLLAMA_DIGEST:
                raise CourseError(
                    "Ollama model digest changed. Reverify it before recording results."
                )
        response = client.chat(
            model=model,
            messages=messages,
            stream=False,
            think=False,
            options={
                "temperature": 0,
                "seed": 20261104,
                "num_ctx": 2048,
                "num_predict": 160,
                "num_thread": 4,
            },
        )
        return response.message.content
    except (httpx.HTTPError, ConnectionError, ollama.ResponseError) as exc:
        raise CourseError(
            f"Cannot use local Ollama at {host}. Start Ollama and inspect scripts/check_env.py --services."
        ) from exc
