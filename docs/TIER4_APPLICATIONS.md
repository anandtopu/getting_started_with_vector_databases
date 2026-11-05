# Run Marlowe Search v2–v5

Tier 4 connects product search, help-center retrieval and local generation, similar-item recommendations, duplicate review, and image/text search. All use one selected database backend. The reference checkpoint uses one Qdrant local client with separate collections for distinct embedding spaces. Photo records use native named vectors. TinyVec and SQLite use separate modality collections explicitly.

## Start from included artifacts

```text
uv sync --extra apps --extra qdrant
uv run --no-sync streamlit run playground/marlowe.py
```

Choose TinyVec, Qdrant local, or SQLite in the sidebar. SQLite also needs `--extra embedded`. Saved queries, help retrieval, similar items, duplicate comparisons and saved gallery images use included real-model vectors. No model download or server is needed for those flows. Release application data in the sidebar when finished.

The local API uses the same service:

```text
uv run --extra apps uvicorn common.apps.marlowe_api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`. Endpoints are `/search`, `/help`, `/similar/{product_id}`, `/duplicates`, and `/photos`. The API supports saved gallery photos and custom text descriptions. The UI also accepts uploaded images. Set `MARLOWE_APP_BACKEND=qdrant-local` in `.env` to use Qdrant for the API. Sessions recreate disposable owned collections and close them on shutdown. This is a local teaching application. Authentication and durable operational service design are Phase 7 topics.

## Custom queries and model preparation

```text
uv sync --extra apps --extra qdrant --extra models --extra rag --extra notebooks
uv run --no-sync python scripts/prepare_tier4.py --all --download
```

`--all` prepares each model in a separate process. Omit `--download` after initial preparation to require cached weights. Select `--rag`, `--reviews`, `--queries`, `--multilingual`, `--image`, or `--reranker` individually. `scripts/embed_data.py --download` prepares the baseline text model for arbitrary search queries if needed. All calls use the immutable model revisions in `common/embeddings.py`. Weights stay in the shared course cache and are not included as source artifacts.

MiniLM is the default English product and help encoder. Qwen multilingual search uses its own 500-product comparison catalog. The UI makes this scope visible. SigLIP uses its own text and image towers for the 200-product gallery. Dimensions alone do not establish compatible spaces. Images and text descriptions longer than the configured model limits are preprocessed/truncated by the declared encoder configuration.

## Local generation

With native Ollama installed:

```text
ollama pull qwen3:0.6b
uv run --extra rag python modules/18_rag/examples/04_generation.py
```

Alternatively start just the pinned Compose service:

```text
docker compose -f docker/compose.yaml --profile weaviate-generation up -d ollama
docker compose -f docker/compose.yaml exec ollama ollama pull qwen3:0.6b
```

The helper checks the pinned digest, uses `think=False`, 2,048 context tokens, at most 160 output tokens and four CPU threads. It never pulls automatically. `MARLOWE_OLLAMA_URL` defaults to `http://127.0.0.1:11434`. An initial run with unconstrained thread allocation timed out on this host; bounded threads completed the measured calls. Local verification used a dedicated rootless Podman container because the host's Docker setup was unavailable.

The small model's raw drafts are not reliable enough for direct support answers. The application records them for evaluation, accepts only an exact approved source excerpt or explicit abstention, and otherwise serves a cited extractive fallback. The UI shows sources. This verifies textual support, not question answerability or source correctness. [Review the observed failures](RAG_REVIEW.md).

## Reproduce results

```text
uv run --extra qdrant python scripts/checkpoint_tier4.py --backend qdrant-local
uv run --extra qdrant --extra models --extra rag python scripts/checkpoint_tier4.py --backend qdrant-local --rerank --generate
uv run python scripts/report_tier4.py
uv run --extra qdrant --extra models --extra rag python scripts/verify_tier4.py --ollama
```

Every checkpoint part writes a new raw JSON under `results/tier4/`. `--part search`, `multilingual`, `rag`, `recommendations`, or `photo` runs just that part. The report selects the newest run per part, so inspect the recorded backend/command when comparing runs. Features have executable profiles in `configs/bench/` and separate leaderboard anchors.

The 10k search evaluation includes all 250 text queries, reporting the 50 held-out queries by type. Five repeated timing passes produce 250 latency samples. This falls short of the preferred 100 independent timed queries because the supplied test split contains only 50 text queries. Generation, reranking, ingestion and embedding timings are separate diagnostics. Multilingual comparison uses 500 products, photo search 200 drawings, and RAG 80 passages. Never compare these timings as vendor rankings.

## Notebooks and cleanup

```text
uv run --extra notebooks --extra qdrant --extra models --extra rag python scripts/run_notebooks.py --module 17_product_search
```

For Module 18's generation cell, set `MARLOWE_NOTEBOOK_PROFILES=ollama` in the process environment after starting Ollama. Without it, the cell reports a skip. Source notebooks are cleared; executed copies go to `.cache/marlowe/tier4/executed-notebooks`.

Stop only resources you started. For the course Compose service use `docker compose -f docker/compose.yaml --profile weaviate-generation stop ollama`. For native Ollama, `ollama stop qwen3:0.6b` unloads the model. The checkpoint closes database collections automatically. `scripts/cleanup.py` previews owned cache cleanup. Do not delete included `data/tier4/` artifacts when clearing runtime data.
