# Setup, reproducibility, and cleanup

Use a terminal in the repository root. Python 3.12 is the verified minor version. `uv sync --locked` installs the base course and development tools; first installation needs network access. After installation, `uv run --offline pytest` and all three foundation examples work without downloading anything.

## Run Tier 1

For the five [Tier 1 lessons](../modules/00_setup/README.md), start with `uv run python modules/00_setup/examples/01_from_scratch.py`. To run every example and notebook against the installed native libraries, use:

```sh
uv run --extra libs --extra embedded python scripts/run_all_examples.py
uv run --extra libs --extra embedded --extra notebooks python scripts/run_notebooks.py
uv run --extra apps python scripts/checkpoint_tier1.py --playground
```

These commands use included vectors and local files; after dependency installation, they need no accounts or network downloads. The optional live embedding experiment in [Module 02](../modules/02_embeddings/README.md) also needs the models extra and cached model weights.

## Run Tier 2

For Tier 2 start with the [hashing lesson](../modules/05_ann_lsh/README.md). Scratch examples use the base environment. To run native examples, notebooks and a short checkpoint selection:

```sh
uv run --extra libs --extra embedded python scripts/run_all_examples.py
uv run --extra libs --extra embedded --extra notebooks python scripts/run_notebooks.py
uv run --extra libs python scripts/checkpoint_tier2.py --family ivf --output .cache/marlowe/tier2/checkpoint
```

Add `--extra hnswlib` to include that native implementation. Windows may require the C++ build tools for its pinned source distribution. For the graph explorer use `uv run --extra apps streamlit run playground/app.py` and open **Index lab**. All normal lesson runs use local files. The [model sample](../data/tier2/README.md) documents optional regeneration.

## pip / venv fallback

`requirements.txt` is exported from the lock, including hashes. Use an existing Python 3.12 installation.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install --no-deps -e .
.venv\Scripts\python.exe examples/01_quickstart.py
```

macOS / Linux:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python examples/01_quickstart.py
```

The editable installation uses the pinned build backend in `pyproject.toml` and initially needs internet access. Contributors can export other combinations with `uv run python scripts/export_requirements.py --extra embedded --output requirements-embedded.txt`. Prefer uv for the CPU-only model index configuration.

## Data and models

The included 10k product and query artifacts make saved semantic search independent of model installation. To regenerate all synthetic source data and 50k text vectors:

```sh
uv run python scripts/build_data.py
uv run --extra models python scripts/embed_data.py --full --download
```

For the included 10k vectors, omit `--full`. Once cached, omit `--download` for strictly local model loading. The generator uses a fixed seed and reference date. Model inference and parquet serialization can differ across dependency/platform changes, so retain manifests and do not assume identical bytes across environments.

`uv run python scripts/download_benchmarks.py --download` explicitly prepares the optional licensed Fashion-MNIST subset. Later runs without the flag verify cached checksums. It is not needed for the foundation leaderboard.

`common.embeddings.ImageTextEncoder(download=True)` is the explicit SigLIP preparation entry point; it does not share MiniLM's vector space. The optional Ollama helper neither installs Ollama nor pulls a model. Image inference and Ollama generation are not yet validated with downloaded weights in this phase.

## Configuration

Defaults work without an `.env`. To customize, copy `.env.example` to `.env` using `Copy-Item .env.example .env` in PowerShell or `cp .env.example .env` on macOS/Linux. Keep credentials local. Changing embedding model settings requires rebuilding matching vectors; changing an endpoint does not start a service.

Run `uv run python scripts/check_env.py --services` to inspect Python, disk, RAM, Docker, cached models, and listening ports. A listening port does not prove it belongs to the intended database.

## Containers

Install a Linux container engine with Compose. From the repository root:

```sh
docker compose -f docker/compose.yaml --profile pgvector config --quiet
docker compose -f docker/compose.yaml --profile pgvector up -d
docker compose -f docker/compose.yaml --profile pgvector ps
docker compose -f docker/compose.yaml --profile pgvector down
```

Other profiles include `qdrant`, `weaviate`, `milvus`, `elasticsearch`, `redis`, `mongodb`, `vespa`, `weaviate-generation` and `monitoring`. Milvus starts etcd and MinIO. The optional generation profile starts Ollama. Deploy Vespa's included schema with `uv run python scripts/deploy_vespa_schema.py` after starting its profile. All images have exact tags and digests and published ports bind to loopback.

Phase 5 executed all database images through a rootless Podman network on the development host. Its default Docker connection and rootful bridge still failed. The portable Compose topology and the tested host-specific route are described in [Tier 3 runtime notes](TIER3_RUNTIME.md).

## Run Tier 3

The first four-database comparison uses only embedded libraries.

```sh
uv run --extra embedded python scripts/checkpoint_tier3.py
```

For a server lesson install its extra, start the profile, then run `scripts/check_profile.py BACKEND` and the module's examples. The [Tier 3 checkpoint](../checkpoints/tier3/README.md) gives the shared comparison command. Native PostgreSQL archive recovery, optional local generation and platform-specific details are in [the runtime guide](TIER3_RUNTIME.md).

Notebook server cells require explicit profile selection. In PowerShell set `$env:MARLOWE_NOTEBOOK_PROFILES='pgvector,qdrant'` before launching Jupyter or `scripts/run_notebooks.py`. On macOS/Linux use `export MARLOWE_NOTEBOOK_PROFILES=pgvector,qdrant`. Include only the profiles you have started.

## Cleanup

```sh
uv run python scripts/cleanup.py
uv run python scripts/cleanup.py --remove
```

The first command previews paths, sizes, containers, networks, and volumes. The second repeats the preview and requires typing `DELETE`. It can remove generated source data, full vectors, downloaded benchmark data, and `.cache/marlowe`, including models downloaded specifically into that cache. It only targets the explicitly named `marlowe-vector-course` and `marlowe-tier5` Compose projects. No global prune is used.

Included 10k artifacts, source, results, `.venv`, shared model caches, uv's shared package cache, Docker images, and unrelated resources are preserved. Custom external data/cache paths are rejected. Junctions/symlinks are rejected rather than followed. Stop programs using course files first. Select the intended Docker context before cleanup; an unavailable engine is reported and left unchanged.

Multiple TinyVec saves retain older versioned vector files to keep snapshot replacement crash-safe. Their temporary example/benchmark directories are removed as a unit. For your own persistent store, retain the entire snapshot directory until you have backed it up and intentionally retired it.


## Tier 4 applications

See [Marlowe Search setup](TIER4_APPLICATIONS.md) for the local API/UI, included frozen vectors, optional real-model inference, local Ollama generation, and one-backend evaluation commands.

## Tier 5 operations

Read the [v6 runbook](TIER5_RUNBOOK.md) for random local credentials, verified TLS, the secure UI, optional native database/monitoring stack, load testing and cleanup. The `ops` extra pins cryptography for local certificates. Notebook native cells require `MARLOWE_NOTEBOOK_PROFILES=qdrant-secure`; load/cluster/monitoring cells remain separately opt-in.
