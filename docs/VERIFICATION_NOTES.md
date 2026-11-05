# Verification notes

## Phase 5 execution update — November 4–5, 2026

The [Phase 5 report](PHASE_5_REPORT.md) records twelve matched database runs, native API experiments and recovery drills. Shared adapters use the installed pinned clients and cosine collections. We verified Chroma reopen, Lance table restore and IVF-PQ, DuckDB VSS installation and HNSW execution, pgvector types and transactions, Qdrant Query API fusion and snapshots, Weaviate v4 tenants and backups, Milvus BM25 and full DISKANN coverage, Redis Search, Atlas Local, Elasticsearch and Vespa tensor retrieval.

The local Weaviate/Ollama generation check used Ollama 0.40.14, verified from the [official release](https://github.com/ollama/ollama/releases/tag/v0.40.14) and Docker Hub manifest before adding its pinned image. The Qwen API digest matches the earlier model pin. The [runtime record](../research/phase5-local-runtime.json) preserves container image identities and model metadata. It also labels the server-memory measurements as post-run samples.

Two API and lifecycle details affected the implementation. The installed Milvus client returns the declared primary-key name in each hit. Weaviate's package-version check contacts PyPI, so the offline adapter disables initialization checks and explicitly verifies local readiness. Atlas Local search can lag writes, so the adapter waits for a batch revision and excludes retired keys after deletion. SQLite snapshot connections now close explicitly on Windows before their temporary directory is removed.

Native server testing used rootless Podman and pasta because the default Docker pipe was unavailable and rootful nftables setup failed. The [runtime guide](TIER3_RUNTIME.md) describes this difference from portable Compose. Optional pgvectorscale was absent. Managed services were researched and documented without creating hosted resources.

## Phase 4 execution update — 2026-11-04

The [Tier 2 evidence](PHASE_4_REPORT.md) covers the installed FAISS 1.15.1, USearch 2.26.6, hnswlib 0.8.0, bm25s 0.3.16, LanceDB 0.41.0 and sqlite-vec 0.1.9 libraries. The Windows host built the hnswlib source distribution. We trained and queried FAISS IVF/PQ, deleted a live USearch item, marked an hnswlib item deleted, and reopened a mapped graph. LanceDB hybrid retrieval names its dense vector column explicitly because a second token-vector column is present. Source references include the [FAISS index catalogue](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes), [USearch](https://github.com/unum-cloud/usearch), [hnswlib](https://github.com/nmslib/hnswlib), and [LanceDB hybrid search](https://docs.lancedb.com/search/hybrid-search).

The [Qwen and reranker sample](../data/tier2/README.md) was generated from the previously pinned revisions. A real LanceDB query checked the shortened Qwen ranking against NumPy. Current low-bit options were checked against [Qdrant's quantization guide](https://qdrant.tech/documentation/manage-data/quantization/) and [Milvus IVF_RABITQ](https://milvus.io/docs/ivf-rabitq.md). Server-side support is documented separately from the local library experiments.

## Phase 3 execution update — 2026-11-04

The [Tier 1 report](PHASE_3_REPORT.md) records the executed lessons, notebooks, native libraries, and benchmark results. We checked native behavior on Windows 11 using the project lock and Python 3.12.13. FAISS flat used explicit vectors, Chroma reopened a local collection, and LanceDB searched a local table. The live embedding experiment used cached MiniLM weights offline. The Playground checkpoint used Streamlit's interaction runner. No container runtime or hosted account is needed for Tier 1.

Relevant upstream references: [FAISS flat search](https://github.com/facebookresearch/faiss/wiki/Getting-started), [scikit-learn PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html), [Sentence Transformers encoding](https://www.sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html), [Chroma clients](https://docs.trychroma.com/reference/python/client), and [LanceDB vector search](https://docs.lancedb.com/search/vector-search). The raw reports record installed versions. Linux CI is configured, but the local evidence does not establish a hosted CI pass, macOS compatibility, or timings on an 8 GB laptop.

## Phase 2 execution update — 2026-11-04

The [Phase 2 report](PHASE_2_REPORT.md) supersedes planning-only status for the delivered foundation. `uv.lock` resolved 276 distributions; a base installation installed 64. Python 3.12.13 was selected by uv; the previously observed system interpreter was 3.12.10. The additional direct benchmark-control dependency is `threadpoolctl==3.7.0`; availability evidence is in [the package check](../research/phase2-package-check.json). Actual installed versions accompany every raw benchmark.

MiniLM's pinned revision was downloaded explicitly and used for 10k included vectors, 300 saved queries, and a local full 50k vector artifact. The cached real-model semantic check passed offline. Float16 storage is explicit in manifests. SigLIP/LLM inference remains unverified with real weights; installed Transformers 5.22.1 exposes pooled features through `ModelOutput.pooler_output`, which the helper now uses.

All nine Compose profiles parse successfully. The local Podman engine failed on nftables networking before PostgreSQL startup; the isolated resources were removed. No image's registry existence is being counted as a successful runtime check. Milvus MinIO environment names and the need to explicitly disable etcd client authentication for the unauthenticated local etcd were checked against the [pinned Milvus configuration](https://raw.githubusercontent.com/milvus-io/milvus/v3.0.5/configs/milvus.yaml). Full runtime compatibility still needs a working engine.

CI action tags checked during implementation: `actions/checkout@v7.0.1`, `astral-sh/setup-uv@v10.3.3`, `actions/upload-artifact@v7.0.2`; CI selects uv 0.13.7, while local execution used 0.12.18. Workflow files are not evidence of a hosted CI pass. Optional dependency synchronization behavior follows [uv's official sync documentation](https://docs.astral.sh/uv/concepts/projects/sync/).

The optional Fashion-MNIST source revision, original MIT license, and exact byte checksums are recorded in [benchmark_datasets.json](benchmark_datasets.json). The original files were downloaded, validated, and transformed into the documented 10k/1k subset. Model weights and bulk datasets remain outside version control.

During local validation, Ruff initially traversed a workspace package cache before explicit excludes were added. The affected cache was removed and every installed optional-environment distribution was reinstalled cleanly without cache reuse. Subsequent tests and benchmarks used the restored environment. `.cache`, `.venv`, generated data, and research artifacts are now explicitly excluded from Ruff traversal.

Two methodology corrections are preserved in the raw evidence: tie-aware neighbor recall for equivalent boundary vectors, and relevance grades that do not penalize unrequested color. Old diagnostic reports remain in separate workload groups. Current results, machine details, exact commands, limitations, and six final run links are in the phase report.

Checked **November 4, 2026 (America/Chicago date)**. Phase 1 verifies public release metadata and selected documentation. It does **not** establish that packages resolve together, containers start, clients interoperate, model inference succeeds, or any performance target is met.

The package and image tables below are exact **candidate pins** for Phase 2. Preserve a tested lock once established; recheck candidates before first implementation if releases have changed. Any conflict must produce a documented compatibility decision, not a silent older pin. Transitive dependencies and platform-specific CPU wheels will be pinned in the generated `uv.lock`, not invented by hand.

## Source evidence and boundaries

- `research/pypi-2026-11-04.json`: direct PyPI project JSON, release version, Python requirement, published filenames, upload timestamps, and yanked flags.
- `research/docker-tags-2026-11-04.json`: Docker Hub tag-list snapshots. Last-updated order is not version order; development tags and partial version aliases are excluded from proposed pins.
- `research/exact-images-2026-11-04.json`: exact selected Docker Hub tag lookup and manifest digest/architectures. Use a version tag plus digest when authoring Compose.
- `research/upstream-checks-2026-11-04.json`: supplemental release/registry evidence, including Quay etcd and upstream project metadata.
- `research/models-2026-11-04.json`: Hugging Face immutable revisions and individual artifact sizes; do not download every duplicated model format.
- `research/milvus-upstream-compose.yaml`: exact deployment asset obtained from the current Milvus v3.0.5 release. It is evidence, not the course Compose file.
- `research/ollama-qwen3-0.6b.json` and `research/ollama-model-digest.json`: raw model manifest, layer sizes and SHA-256 of manifest bytes. This digest is not a Hugging Face commit.

## API and capability decisions

| System | Official source inspected | Decision and remaining verification |
|---|---|---|
| Chroma | [Python client](https://docs.trychroma.com/reference/python) | Plan persistent client and explicit vectors. Disable automatic embedding/model downloads in tests; verify CRUD/query signatures against installed version before coding calls. |
| LanceDB | [Python API](https://lancedb.github.io/lancedb/python/python/) | Native vector/text/hybrid APIs are documented. Confirm chosen index types, pre/post-filter behavior, local persistence and reranker arguments in runtime smoke tests. |
| sqlite-vec | [Python integration](https://alexgarcia.xyz/sqlite-vec/python.html) | Documented extension load/unload permission sequence and float32 serialization. Windows wheel exists. Current docs can show alpha features: only use features verified for stable 0.1.9. |
| DuckDB VSS | [2.0 VSS docs](https://duckdb.org/docs/2.0/core_extensions/vss), [source](https://github.com/duckdb/duckdb-vss) | Experimental HNSW extension is still documented; repository was not archived and had an October 2026 push. That is evidence of recent activity, not a maintenance guarantee. Keep exact ARRAY search available. Preinstall/cache matching signed extension artifacts before offline use; no hidden network installation during tests. Treat persistence as experimental, test recovery, and record extension version/hash. |
| pgvector | [upstream README](https://github.com/pgvector/pgvector) | Use vector/halfvec/bit, HNSW/IVFFlat, and explicit iterative-scan settings for selective filters. Teach query plans and parameterized SQL. Python package version and server extension version are different. |
| pgvectorscale | [upstream repository](https://github.com/timescale/pgvectorscale) | Release 0.9.1 observed. Optional: no matching prebuilt course image verified yet. Do not add unverified install commands or claim the pgvector image includes it. Verify a supported image or pinned build in Phase 5. |
| Qdrant | [Query API/hybrid](https://qdrant.tech/documentation/search/hybrid-queries/) | Plan current Query API (`query_points`) and explicit prefetch/fusion; distinguish sparse-vector fusion from native text indexing. Check model types and quantization options against the pinned client/server during implementation. |
| Weaviate | [v4 Python client](https://docs.weaviate.io/weaviate/client-libraries/python) | Use collections and current vector configuration APIs, not v3 examples. Expose HTTP and gRPC locally. Candidate server 1.40.3 is newer than the documented minimum. Test connection/context cleanup, native hybrid, tenants, and optional local generation. |
| Milvus | [Windows deployment](https://milvus.io/docs/install_standalone-windows.md), [BM25](https://milvus.io/docs/full-text-search.md) | Current release v3.0.5 and PyMilvus 3.0.2 are candidates. Native full-text BM25 is documented; configure analyzer/function/sparse field explicitly. Test actual current hybrid and disk-index APIs; client/server minor numbers need not match. |
| Milvus Lite | [current Lite docs](https://milvus.io/docs/milvus_lite.md) | Docs explicitly name Lite 3.2.2 and Windows/macOS/Linux subject to dependency wheels. It is an optional extra, not implicit in bare PyMilvus. Feature parity with server Milvus is not assumed. |
| FAISS / USearch / hnswlib | [FAISS](https://github.com/facebookresearch/faiss/wiki), [USearch](https://github.com/unum-cloud/usearch), [hnswlib](https://github.com/nmslib/hnswlib) | PyPI has CPython 3.12 Windows x64 wheels for current FAISS and USearch. hnswlib 0.8.0 is source-only: use USearch by default and retain optional hnswlib comparisons. Do not disguise one algorithm as the other. |
| Redis | [Redis Search docs](https://redis.io/docs/latest/interact/search-and-query/) | Current Redis Open Source includes Search features. Use the official Redis image and verify module/command availability; do not depend on an old Redis Stack assumption. |
| MongoDB | [local quickstart](https://www.mongodb.com/docs/search/self-managed/current/installation/quick-start/) | Use the versioned Atlas Local image for local development with explicit vectors. Do not infer production suitability or require the moving preview tag/paid automated embedding. Confirm local search index readiness and query support. |
| Ollama | [chat endpoint](https://docs.ollama.com/api/chat) | Local chat uses the pinned model manifest; select nonstreaming teaching calls and bounded context. Verify model digest before experiments and fail on unexpected drift. Native runtime release v0.40.14 was observed separately from Python client 0.6.3. |

Every call still requires installed-signature/official-example checks at implementation time. Landscape Elasticsearch/Vespa feature details, optional managed SDK calls/free access, cloud pricing, B1 npm packages, and B4's final method are intentionally not asserted as runtime verified in Phase 1.

## Compatibility issues and explicit substitutions

1. Use USearch instead of making hnswlib compilation a mandatory Windows prerequisite. hnswlib remains optional and its source-build requirement is visible.
2. DuckDB VSS is a real optional extension, not a dependency installed by `pip install duckdb`. Default offline testing has a working exact alternative and explicit VSS-specific status.
3. `minio/minio` on Docker Hub returned 404. The current Milvus release asset instead references `milvusdb/minio:RELEASE.2024-12-18T13-15-44Z`, whose tag and digest were verified. Use the upstream-supported mirror, not an invented tag.
4. Milvus's current deployment bundle specifies etcd v3.5.25 and the 2024 MinIO tag. These are **not claimed to be the newest standalone releases**. This is a documented compatibility exception to a literal all-components-newest policy. Before shipping, evaluate whether the current embedded Milvus deployment removes these dependencies, or validate the upstream bundle and disclose its age. Do not silently upgrade stateful dependencies beyond verified compatibility.
5. The instant quick start uses real frozen product **and query** vectors. A free-text query requires the same encoder revision; hashing is not an alternative semantic encoder.
6. SigLIP 2 and MiniLM produce different embedding spaces. Store separate named vectors or collections and fuse scores/ranks; never compare a MiniLM query directly against a SigLIP image.
7. Managed services without a verified free route remain optional explanatory material. No accounts, paid resources, remote data writes, or deployments have been created.

## Models and resource estimates

The following revisions and weight sizes come from the saved registry metadata. Peak CPU RAM budgets are estimates in the plan, to be measured with realistic batches. All five inspected Hugging Face model cards declare Apache-2.0; preserve notices when redistributing derived artifacts. Framework/environment disk use is additional.

| Model | Immutable revision | Selected weight bytes | Source |
|---|---|---:|---|
| `Qwen/Qwen3-0.6B` | `c1899de289a04d12100db370d81485cdf75e47ca` | 1,503,300,328 | [Revision](https://huggingface.co/Qwen/Qwen3-0.6B/tree/c1899de289a04d12100db370d81485cdf75e47ca) |
| `Qwen/Qwen3-Embedding-0.6B` | `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3` | 1,191,586,416 | [Revision](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B/tree/97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3) |
| `cross-encoder/ms-marco-MiniLM-L6-v2` | `233902d25c440f23af6f7d6e94d2946bac0bee0a` | 90,870,598 | [Revision](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/tree/233902d25c440f23af6f7d6e94d2946bac0bee0a) |
| `google/siglip2-base-patch16-224` | `75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2` | 1,500,800,904 | [Revision](https://huggingface.co/google/siglip2-base-patch16-224/tree/75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2) |
| `sentence-transformers/all-MiniLM-L6-v2` | `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` | 90,868,376 | [Revision](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/1110a243fdf4706b3f48f1d95db1a4f5529b4d41) |

Default roles: MiniLM for text; SigLIP 2 for image/text; Qwen embeddings for multilingual/Matryoshka experiments; cross-encoder MiniLM for optional reranking. The Qwen generation checkpoint is recorded for provenance, but the executable local LLM uses the separate quantized Ollama artifact below.

Ollama `qwen3:0.6b` manifest SHA-256: `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`. Its model layer is 522,640,096 bytes, digest `sha256:7f4030143c1c477224c5434f8272c662a8b042079a0a584f0a27a1684fe2e1fa`. Verify the local artifact matches before measuring; a tag alone is mutable. Source: [Ollama registry manifest](https://registry.ollama.ai/v2/library/qwen3/manifests/0.6b).

## Python packages: candidate exact pins

These are the versions reported by PyPI's project JSON endpoint on the checked date. Links go to the versioned release. `unspecified` means the project metadata lacks a Python constraint, not that every Python version works. Current-release availability is verified; dependency resolution is pending.

| Package | Candidate pin | Python requirement | Source |
|---|---|---|---|
| `bm25s` | `0.3.16` | `>=3.8` | [PyPI](https://pypi.org/project/bm25s/0.3.16/) |
| `chromadb` | `1.5.9` | `>=3.9` | [PyPI](https://pypi.org/project/chromadb/1.5.9/) |
| `duckdb` | `2.0.0` | `>=3.11.0` | [PyPI](https://pypi.org/project/duckdb/2.0.0/) |
| `elasticsearch` | `9.5.1` | `>=3.10` | [PyPI](https://pypi.org/project/elasticsearch/9.5.1/) |
| `faiss-cpu` | `1.15.1` | `>=3.10` | [PyPI](https://pypi.org/project/faiss-cpu/1.15.1/) |
| `faker` | `40.44.0` | `>=3.10` | [PyPI](https://pypi.org/project/faker/40.44.0/) |
| `fastapi` | `0.162.0` | `>=3.10` | [PyPI](https://pypi.org/project/fastapi/0.162.0/) |
| `h5py` | `3.16.0` | `>=3.10` | [PyPI](https://pypi.org/project/h5py/3.16.0/) |
| `hatchling` | `1.33.0` | `>=3.10` | [PyPI](https://pypi.org/project/hatchling/1.33.0/) |
| `hnswlib` | `0.8.0` | `unspecified` | [PyPI](https://pypi.org/project/hnswlib/0.8.0/) |
| `httpx` | `0.28.1` | `>=3.8` | [PyPI](https://pypi.org/project/httpx/0.28.1/) |
| `huggingface-hub` | `2.4.0` | `>=3.10.0` | [PyPI](https://pypi.org/project/huggingface-hub/2.4.0/) |
| `jupyter` | `1.1.1` | `unspecified` | [PyPI](https://pypi.org/project/jupyter/1.1.1/) |
| `lancedb` | `0.41.0` | `>=3.10` | [PyPI](https://pypi.org/project/lancedb/0.41.0/) |
| `locust` | `2.47.0` | `>=3.11` | [PyPI](https://pypi.org/project/locust/2.47.0/) |
| `matplotlib` | `3.11.2` | `>=3.11` | [PyPI](https://pypi.org/project/matplotlib/3.11.2/) |
| `milvus-lite` | `3.2.2` | `>=3.10` | [PyPI](https://pypi.org/project/milvus-lite/3.2.2/) |
| `nbstripout` | `0.9.1` | `>=3.10` | [PyPI](https://pypi.org/project/nbstripout/0.9.1/) |
| `numpy` | `2.5.4` | `>=3.12` | [PyPI](https://pypi.org/project/numpy/2.5.4/) |
| `ollama` | `0.6.3` | `>=3.8` | [PyPI](https://pypi.org/project/ollama/0.6.3/) |
| `pandas` | `3.1.1` | `>=3.11` | [PyPI](https://pypi.org/project/pandas/3.1.1/) |
| `pgvector` | `0.5.1` | `>=3.10` | [PyPI](https://pypi.org/project/pgvector/0.5.1/) |
| `pillow` | `13.0.0` | `>=3.11` | [PyPI](https://pypi.org/project/pillow/13.0.0/) |
| `pinecone` | `10.3.0` | `>=3.10` | [PyPI](https://pypi.org/project/pinecone/10.3.0/) |
| `pre-commit` | `4.7.0` | `>=3.11` | [PyPI](https://pypi.org/project/pre-commit/4.7.0/) |
| `prometheus-client` | `0.26.0` | `>=3.9` | [PyPI](https://pypi.org/project/prometheus-client/0.26.0/) |
| `psutil` | `7.2.2` | `>=3.6` | [PyPI](https://pypi.org/project/psutil/7.2.2/) |
| `psycopg` | `3.3.8` | `>=3.10` | [PyPI](https://pypi.org/project/psycopg/3.3.8/) |
| `pyarrow` | `26.0.1` | `>=3.11` | [PyPI](https://pypi.org/project/pyarrow/26.0.1/) |
| `pydantic` | `2.14.2` | `>=3.10` | [PyPI](https://pypi.org/project/pydantic/2.14.2/) |
| `pymilvus` | `3.0.2` | `>=3.9` | [PyPI](https://pypi.org/project/pymilvus/3.0.2/) |
| `pymongo` | `4.19.0` | `>=3.11` | [PyPI](https://pypi.org/project/pymongo/4.19.0/) |
| `pytest` | `9.2.0` | `>=3.10` | [PyPI](https://pypi.org/project/pytest/9.2.0/) |
| `pytest-socket` | `0.8.1` | `>=3.10` | [PyPI](https://pypi.org/project/pytest-socket/0.8.1/) |
| `python-dotenv` | `1.2.4` | `>=3.10` | [PyPI](https://pypi.org/project/python-dotenv/1.2.4/) |
| `pyvespa` | `1.2.10` | `<3.16,>=3.11` | [PyPI](https://pypi.org/project/pyvespa/1.2.10/) |
| `pyyaml` | `6.0.3` | `>=3.8` | [PyPI](https://pypi.org/project/pyyaml/6.0.3/) |
| `qdrant-client` | `1.20.0` | `>=3.10` | [PyPI](https://pypi.org/project/qdrant-client/1.20.0/) |
| `redis` | `8.1.0` | `>=3.10` | [PyPI](https://pypi.org/project/redis/8.1.0/) |
| `rich` | `15.0.0` | `>=3.9.0` | [PyPI](https://pypi.org/project/rich/15.0.0/) |
| `ruff` | `0.17.3` | `>=3.7` | [PyPI](https://pypi.org/project/ruff/0.17.3/) |
| `safetensors` | `0.8.0` | `>=3.10` | [PyPI](https://pypi.org/project/safetensors/0.8.0/) |
| `scikit-learn` | `1.9.1` | `>=3.11` | [PyPI](https://pypi.org/project/scikit-learn/1.9.1/) |
| `sentence-transformers` | `6.2.0` | `>=3.10` | [PyPI](https://pypi.org/project/sentence-transformers/6.2.0/) |
| `sqlite-vec` | `0.1.9` | `unspecified` | [PyPI](https://pypi.org/project/sqlite-vec/0.1.9/) |
| `streamlit` | `1.66.1` | `>=3.11` | [PyPI](https://pypi.org/project/streamlit/1.66.1/) |
| `torch` | `2.15.0` | `>=3.11` | [PyPI](https://pypi.org/project/torch/2.15.0/) |
| `transformers` | `5.22.1` | `>=3.11.0` | [PyPI](https://pypi.org/project/transformers/5.22.1/) |
| `turbopuffer` | `3.1.0` | `>=3.11` | [PyPI](https://pypi.org/project/turbopuffer/3.1.0/) |
| `usearch` | `2.26.6` | `>=3.11` | [PyPI](https://pypi.org/project/usearch/2.26.6/) |
| `uv` | `0.13.7` | `>=3.8` | [PyPI](https://pypi.org/project/uv/0.13.7/) |
| `uvicorn` | `0.54.0` | `>=3.10` | [PyPI](https://pypi.org/project/uvicorn/0.54.0/) |
| `weaviate-client` | `4.24.1` | `>=3.10` | [PyPI](https://pypi.org/project/weaviate-client/4.24.1/) |

Install design: base/core numerical data tools; `libs` FAISS/USearch; `hnswlib` optional compiler route; `embedded` Chroma/LanceDB/sqlite-vec/DuckDB; one extra per database server; `models` CPU text inference; `multimodal`; `rag`; `landscape`; `managed`; `apps`; `notebooks`; and `dev`. Use PCA instead of adding UMAP; use bm25s instead of rank-bm25; use Elasticsearch instead of OpenSearch. Learned sparse inference is optional and will need its own verified model pin if added. No unlisted package may be introduced without checking its release and documenting it.

## Container images: candidate exact tags

Each image below was checked at its registry. The source returns its manifest digest, recorded in the evidence file. This verifies existence, not successful pull/start/health, architecture runtime support, or client compatibility. Extra Milvus services inherit its one Compose profile. Proposed course profiles: `pgvector`, `qdrant`, `weaviate`, `milvus`, `elasticsearch`, `redis`, `mongodb`, `vespa`, and `monitoring`.

| Exact image tag | Manifest digest | Registry source |
|---|---|---|
| `grafana/grafana:13.3.0` | `sha256:488984b716c0862639f91a698adbe2862677a5a07bad42da5f03f3030883b205` | [Tag metadata](https://hub.docker.com/v2/repositories/grafana/grafana/tags/13.3.0) |
| `library/elasticsearch:9.5.5` | `sha256:764a939891119d97e130b4d5da196c330afb2338382ada9e1b9b7943ce6707df` | [Tag metadata](https://hub.docker.com/v2/repositories/library/elasticsearch/tags/9.5.5) |
| `library/redis:8.10.3` | `sha256:de1068af6f552240dfab67bcc9bfef99bfc60f776bb4580ef077ea4c8c97e848` | [Tag metadata](https://hub.docker.com/v2/repositories/library/redis/tags/8.10.3) |
| `milvusdb/milvus:v3.0.5` | `sha256:b9b79b4a284b41cd12d60abc418310f84621fa4c977d409b38f501519a7ccf8a` | [Tag metadata](https://hub.docker.com/v2/repositories/milvusdb/milvus/tags/v3.0.5) |
| `milvusdb/minio:RELEASE.2024-12-18T13-15-44Z` | `sha256:1dce27c494a16bae114774f1cec295493f3613142713130c2d22dd5696be6ad3` | [Tag metadata](https://hub.docker.com/v2/repositories/milvusdb/minio/tags/RELEASE.2024-12-18T13-15-44Z) |
| `mongodb/mongodb-atlas-local:8.3.11-20261103T091247Z` | `sha256:8886be3f095a801d22c294ca306e3821d34d39912c0839eea1df73a2ffdc1ed5` | [Tag metadata](https://hub.docker.com/v2/repositories/mongodb/mongodb-atlas-local/tags/8.3.11-20261103T091247Z) |
| `pgvector/pgvector:0.8.7-pg18-trixie` | `sha256:5895949dfcdf308eb0cd31c950c93c14895c77f33fbedfecf1fa511ab1d4bcd2` | [Tag metadata](https://hub.docker.com/v2/repositories/pgvector/pgvector/tags/0.8.7-pg18-trixie) |
| `prom/prometheus:v3.15.1` | `sha256:fa3302279710be2f21a8301ec17a8b4f2301fd829bd113839b3b6b02b6f191a2` | [Tag metadata](https://hub.docker.com/v2/repositories/prom/prometheus/tags/v3.15.1) |
| `qdrant/qdrant:v1.20.0` | `sha256:9bfc89f9914fc14876a88c05270685921a55b8877b254a98bcc1cc2f0a424cd2` | [Tag metadata](https://hub.docker.com/v2/repositories/qdrant/qdrant/tags/v1.20.0) |
| `semitechnologies/weaviate:1.40.3` | `sha256:e96e2e04ee6f401a8dcdf89adb80b610516e1491a33769dfed6d1318801e1129` | [Tag metadata](https://hub.docker.com/v2/repositories/semitechnologies/weaviate/tags/1.40.3) |
| `vespaengine/vespa:8.781.11` | `sha256:93268edd995b4e671be33babf7ebac55155fd0f330bb0b02123d1fbf3a9d1df0` | [Tag metadata](https://hub.docker.com/v2/repositories/vespaengine/vespa/tags/8.781.11) |
| `quay.io/coreos/etcd:v3.5.25` | `sha256:52f17f7e56e4f7239f0320dbfcbcc24721163d7d78ae710b466af3254ccf6366` | [Tag metadata](https://quay.io/api/v1/repository/coreos/etcd/tag/?specificTag=v3.5.25) |

The pgvector tag pins the extension and PostgreSQL major/OS variant; the recorded digest is needed to fix the PostgreSQL patch/base-image bytes too. No moving `latest`, `main`, `nightly`, or `preview` tags will enter the course Compose file. Ollama runs as a native optional local application by default, so it has no mandatory Compose image.

## Measurement and execution status

No leaderboard hardware exists yet because no benchmark has run. The planning environment reports Windows PowerShell 7.6.9, Python 3.12.10, and installed uv 0.12.18. That is not a performance record. CPU/RAM/storage and complete dependency/server metadata will be captured automatically for every actual run.

Not executed in Phase 1: `uv sync`, lock resolution, Ruff, pytest, embedded integration, Docker profile startup, live model inference, benchmark sweeps, notebook execution, CI, or publication. Phase 2 begins those checks. Final definition-of-done boxes remain unticked until backed by run evidence.


## Planning-document audit

Checked all five planning documents: 24 core modules, 81 unique feature IDs, both schedules totaling 58 hours, balanced code fences, and all local Markdown link targets. No implementation placeholders or unfinished table markers remain.

The initial public-source reachability check tested 144 URLs; 132 returned HTTP 200 directly. Corrected the sqlite-vec binary-quantization path using its official navigation. Replaced a stale Milvus compaction link that redirected to unrelated insertion documentation with pgvector's documented vacuum/reindex comparison. The browser research service could read Vespa, LanceDB, and the cited Milvus pages despite the direct check's DNS, timeout, or redirect-loop failures. Two ACM DOI destinations blocked automated requests; the PQ DOI returned HTTP 202. These are recorded as automated-check limitations, not claimed passing checks. The original status report is retained in `research/source-link-check.json`; its follow-up notes record corrections. Final publication will recheck external links and every then-implemented feature target.


## Phase 6 application verification (2026-11-05)

Pinned SigLIP 2 inference was exercised end to end with the installed Transformers 5.22.1 model-tower output API (`pooler_output`), as documented in the [official SigLIP 2 reference](https://huggingface.co/docs/transformers/model_doc/siglip2). Real Qwen and cross-encoder inference used the immutable revisions already recorded in the source. [CrossEncoder reference](https://www.sbert.net/docs/package_reference/cross_encoder/model.html) and [Qdrant named vectors](https://qdrant.tech/documentation/manage-data/vectors/) were checked against actual local behavior. Qdrant local mode supports the named-vector schema used here; server ANN/distribution is not implied.

Local Ollama generation used the existing pinned image/model, `think=False`, four CPU threads, 2,048 context tokens and at most 160 output tokens. Initial default-thread inference timed out, and one completed raw draft contradicted the retrieved credential policy. [The RAG review](RAG_REVIEW.md) records this evidence and the conservative source-excerpt delivery policy. [Phase 6 report](PHASE_6_REPORT.md) summarizes tests and limits.

## Phase 7 execution

[Phase 7 verification](PHASE_7_REPORT.md) records local tests, notebooks, native TLS, migration/snapshot recovery, real three-peer failure recovery, Locust and Prometheus/Grafana. Docker Compose and new hosted CI are supplied but were not executed on this host; equivalent pinned services ran under rootless Podman. No cloud deployments, new model downloads or legal compliance claims are involved.

## Phase 8 finishing verification (2026-11-05)

Python dependencies remain pinned by the 276-package uv lock; only the course version changed to 1.0.0. B1 separately pins @qdrant/js-client-rest 1.20.0, weaviate-client 3.15.3, TypeScript 7.0.2 and @types/node 26.6.6 in its npm manifest/lock. Node 24.18.0 compiled and ran both native clients. The added CI action [setup-node v7.1.0](https://github.com/actions/setup-node/releases/tag/v7.1.0) was checked against its official release; the hosted workflow itself remains unrun.

FAISS 1.15.1 executed Flat, RR384/RaBitQ and RR384/RaBitQ4. [FAISS factory syntax](https://github.com/facebookresearch/faiss/wiki/The-index-factory), [native RaBitQ header](https://github.com/facebookresearch/faiss/blob/main/faiss/IndexRaBitQ.h), the [original paper](https://arxiv.org/abs/2405.12497), [Qdrant TypeScript client](https://github.com/qdrant/qdrant-js), and [Weaviate TypeScript reference](https://weaviate.github.io/typescript-client/) were checked against the executed paths. Public-data checksums and license remain in the prepared Fashion-MNIST manifest.

The host reports Windows 11, Python 3.12.13, 24 logical cores and about 31.5 GiB RAM. Raw results retain exact hardware, versions and source hashes. Final provenance now includes capstone Python, TypeScript and npm manifests; older records retain their original narrower source inventory. The final delivery inventory separately hashes all lesson/capstone files. Several checks ran concurrently, so timing observations are local diagnostics rather than isolated hardware certification.

See [Phase 8](PHASE_8_REPORT.md), [definition of done](DEFINITION_OF_DONE.md), and the [HTTP reachability record](../results/bonus/online-links.json). Automated DNS/access-denial failures are retained; remote CI, paid services and public repository publication are not claimed.
