"""Lazy CPU encoders and a content/model/preprocessing-addressed disk cache.

Nothing is downloaded implicitly. Pass download=True during explicit preparation.
HashEncoder exists for offline tests; it is not a semantic model.
"""

import hashlib
import os
import re
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from common.errors import CourseError
from common.io import digest
from common.settings import cache_dir

TEXT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TEXT_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
IMAGE_MODEL = "google/siglip2-base-patch16-224"
IMAGE_REVISION = "75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
RERANK_REVISION = "233902d25c440f23af6f7d6e94d2946bac0bee0a"


def normalize(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=-1, keepdims=True)
    return np.divide(matrix, norms, out=np.zeros_like(matrix), where=norms != 0)


@dataclass(frozen=True)
class EmbeddingSpec:
    model: str = TEXT_MODEL
    revision: str = TEXT_REVISION
    dimensions: int = 384
    normalized: bool = True
    modality: str = "text"
    query_prefix: str = ""
    document_prefix: str = ""
    max_length: int = 256
    dtype: str = "float32"

    @property
    def space(self) -> str:
        return f"{self.model}@{self.revision}:{digest(asdict(self))[:16]}"


class HashEncoder:
    def __init__(self, dimensions: int = 64) -> None:
        if dimensions < 1:
            raise ValueError("dimensions must be positive")
        self.spec = EmbeddingSpec(model="marlowe/hash", revision="sha256-v1", dimensions=dimensions)

    def encode(self, texts: Sequence[str], role: str = "document") -> np.ndarray:
        output = np.zeros((len(texts), self.spec.dimensions), dtype=np.float32)
        for row, text in enumerate(texts):
            for token in re.findall(r"\w+", text.lower()) or ["<empty>"]:
                hashed = hashlib.sha256(token.encode()).digest()
                output[row, int.from_bytes(hashed[:4], "little") % self.spec.dimensions] += (
                    1 if hashed[4] & 1 else -1
                )
            if not np.any(output[row]):
                output[row, 0] = 1
        return normalize(output)


class EmbeddingCache:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or cache_dir() / "embeddings"

    def key(self, text: str, spec: EmbeddingSpec, role: str) -> str:
        if role not in {"query", "document"}:
            raise ValueError("role must be query or document")
        return digest({"spec": asdict(spec), "role": role, "content": text})

    def encode(
        self, texts: Sequence[str], spec: EmbeddingSpec, role: str, encode: Callable
    ) -> np.ndarray:
        if not texts:
            return np.empty((0, spec.dimensions), dtype=np.float32)
        keys = [self.key(text, spec, role) for text in texts]
        values: dict[str, np.ndarray] = {}
        missing: dict[str, str] = {}
        for key, text in zip(keys, texts, strict=True):
            path = self.directory / key[:2] / f"{key}.npy"
            if path.exists():
                value = np.load(path, allow_pickle=False)
                if value.shape != (spec.dimensions,) or not np.isfinite(value).all():
                    raise CourseError(
                        f"Corrupt embedding cache entry: {path}; remove it and retry."
                    )
                values[key] = value
            else:
                missing[key] = text
        if missing:
            encoded = np.asarray(encode(list(missing.values()), role), dtype=np.float32)
            if encoded.shape != (len(missing), spec.dimensions) or not np.isfinite(encoded).all():
                raise ValueError("Encoder returned an invalid shape or non-finite values")
            for key, vector in zip(missing, encoded, strict=True):
                path = self.directory / key[:2] / f"{key}.npy"
                path.parent.mkdir(parents=True, exist_ok=True)
                fd, temp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
                try:
                    with os.fdopen(fd, "wb") as stream:
                        np.save(stream, vector, allow_pickle=False)
                    os.replace(temp, path)
                finally:
                    Path(temp).unlink(missing_ok=True)
                values[key] = vector
        return np.stack([values[key] for key in keys])


class TextEncoder:
    def __init__(
        self, spec: EmbeddingSpec | None = None, *, download: bool = False, batch_size: int = 32
    ) -> None:
        self.spec = spec or EmbeddingSpec()
        self.download = download
        self.batch_size = batch_size
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                import torch
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise CourseError("Install CPU encoders: uv sync --extra models") from exc
            torch.set_num_threads(min(4, os.cpu_count() or 1))
            os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
            try:
                self._model = SentenceTransformer(
                    self.spec.model,
                    revision=self.spec.revision,
                    device="cpu",
                    cache_folder=str(cache_dir() / "models"),
                    local_files_only=not self.download,
                    trust_remote_code=False,
                )
            except OSError as exc:
                raise CourseError(
                    "Model not available locally. Run: uv run --extra models python scripts/embed_data.py --download"
                ) from exc
            self._model.max_seq_length = self.spec.max_length
        return self._model

    def encode(self, texts: Sequence[str], role: str = "document") -> np.ndarray:
        if role not in {"query", "document"}:
            raise ValueError("role must be query or document")
        if not texts:
            return np.empty((0, self.spec.dimensions), dtype=np.float32)
        prefix = self.spec.query_prefix if role == "query" else self.spec.document_prefix
        values = self._load().encode(
            list(texts),
            prompt=prefix,
            batch_size=self.batch_size,
            normalize_embeddings=self.spec.normalized,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100,
        )
        return np.asarray(values[:, : self.spec.dimensions], dtype=np.float32)


def cached_texts(
    texts: Sequence[str],
    encoder: TextEncoder | HashEncoder,
    role: str = "document",
    directory: Path | None = None,
) -> np.ndarray:
    return EmbeddingCache(directory).encode(texts, encoder.spec, role, encoder.encode)


def frozen_query(query_id: str, directory: Path) -> tuple[np.ndarray, dict]:
    import pyarrow.parquet as pq

    from common.data import load_vectors

    path = directory / "query_embeddings.parquet"
    vectors, metadata = load_vectors(path)
    ids = pq.read_table(path, columns=["id"])["id"].to_pylist()
    if query_id not in ids:
        raise CourseError(
            f"No frozen query {query_id}. Choose an ID from data/eval/search_qrels.jsonl."
        )
    return vectors[ids.index(query_id)], metadata


class ImageTextEncoder:
    """SigLIP 2 features share a space only with each other, not with MiniLM."""

    def __init__(self, *, download: bool = False) -> None:
        self.download = download
        self._model = None
        self._processor = None
        self.spec = EmbeddingSpec(
            model=IMAGE_MODEL,
            revision=IMAGE_REVISION,
            dimensions=768,
            modality="image-text",
            max_length=64,
        )

    def encode(self, inputs: Sequence, modality: str) -> np.ndarray:
        from PIL import Image

        if modality not in {"text", "image"}:
            raise ValueError("modality must be text or image")
        prepared = []
        keys = []
        for value in inputs:
            if modality == "text":
                prepared.append(str(value))
                keys.append("text:" + str(value))
            else:
                if isinstance(value, (str, Path)):
                    with Image.open(value) as source:
                        value = source.convert("RGB").copy()
                else:
                    value = value.convert("RGB")
                prepared.append(value)
                keys.append(
                    "image:"
                    + digest(
                        {"size": value.size, "pixels": hashlib.sha256(value.tobytes()).hexdigest()}
                    )
                )
        lookup = dict(zip(keys, prepared, strict=True))
        return EmbeddingCache().encode(
            keys,
            self.spec,
            "query" if modality == "text" else "document",
            lambda missing, role: self._encode_uncached([lookup[key] for key in missing], modality),
        )

    def _encode_uncached(self, inputs: Sequence, modality: str) -> np.ndarray:
        if modality not in {"text", "image"}:
            raise ValueError("modality must be text or image")
        try:
            import torch
            from transformers import AutoModel, AutoProcessor
        except ImportError as exc:
            raise CourseError("Install image/text inference: uv sync --extra models") from exc
        if self._model is None:
            torch.set_num_threads(min(4, os.cpu_count() or 1))
            kwargs = {
                "revision": IMAGE_REVISION,
                "cache_dir": str(cache_dir() / "models"),
                "local_files_only": not self.download,
            }
            try:
                self._model = AutoModel.from_pretrained(IMAGE_MODEL, **kwargs).eval().to("cpu")
                self._processor = AutoProcessor.from_pretrained(IMAGE_MODEL, **kwargs)
            except OSError as exc:
                raise CourseError(
                    "SigLIP 2 is not cached. Explicitly prepare it with ImageTextEncoder(download=True)."
                ) from exc
        if not inputs:
            return np.empty((0, self._model.config.vision_config.hidden_size), dtype=np.float32)
        batches = []
        for start in range(0, len(inputs), 4):
            batch = list(inputs[start : start + 4])
            with torch.inference_mode():
                if modality == "text":
                    prepared = self._processor(
                        text=batch,
                        padding="max_length",
                        max_length=64,
                        truncation=True,
                        return_tensors="pt",
                    )
                    features = self._model.get_text_features(
                        **prepared, return_dict=True
                    ).pooler_output
                else:
                    prepared = self._processor(images=batch, return_tensors="pt")
                    features = self._model.get_image_features(
                        **prepared, return_dict=True
                    ).pooler_output
                batches.append(features.cpu().numpy())
        return normalize(np.concatenate(batches))


def multilingual_spec() -> EmbeddingSpec:
    return EmbeddingSpec(
        model="Qwen/Qwen3-Embedding-0.6B",
        revision="97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3",
        dimensions=1024,
        query_prefix="Instruct: Given a product search query, retrieve relevant product listings\nQuery: ",
        max_length=256,
    )


class Reranker:
    """Joint query/document scoring, kept separate from embedding similarity."""

    def __init__(self, *, download: bool = False) -> None:
        self.download = download
        self._model = None

    def score(self, query: str, documents: Sequence[str]) -> np.ndarray:
        if not documents:
            return np.empty(0, dtype=np.float32)
        if self._model is None:
            try:
                import torch
                from sentence_transformers import CrossEncoder

                torch.set_num_threads(min(4, os.cpu_count() or 1))
                self._model = CrossEncoder(
                    RERANK_MODEL,
                    revision=RERANK_REVISION,
                    device="cpu",
                    cache_folder=str(cache_dir() / "models"),
                    local_files_only=not self.download,
                    trust_remote_code=False,
                )
            except (ImportError, OSError) as exc:
                raise CourseError(
                    "Prepare reranking: uv run --extra models python scripts/prepare_tier4.py --reranker --download"
                ) from exc
        return np.asarray(
            self._model.predict(
                [(query, text) for text in documents], batch_size=16, show_progress_bar=False
            ),
            dtype=np.float32,
        )
