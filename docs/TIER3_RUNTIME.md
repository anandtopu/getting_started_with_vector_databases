# Tier 3 runtime verification

The normal learner path uses the pinned services in [compose.yaml](../docker/compose.yaml). Start one profile, check readiness, run the lesson and stop that profile. A client library installation alone does not establish that the server is ready.

The Phase 5 development host had an unavailable Docker Desktop pipe and a rootful Podman nftables failure. The same pinned database images ran successfully through the existing rootless Podman connection with pasta networking. Published ports bound only to 127.0.0.1. PostgreSQL used 15432, set through MARLOWE_POSTGRES_URL. Milvus, MinIO and etcd shared a private pod and used loopback addresses inside that pod. The optional Weaviate generation check used a separate pod and ports 18080 and 15051.

This route is a host-specific verification arrangement. The portable Compose topology uses service DNS names. The [runtime record](../research/phase5-local-runtime.json) records the actual image digests, VM resources, local model identity and post-run memory samples. Benchmark files record the Windows client hardware, package versions, source hashes and commands.

On the verified Windows host, a single rootless Qdrant instance can be started with the pinned image from the Compose file:

```powershell
$courseImage = .venv\Scripts\python.exe -c "import yaml; print(yaml.safe_load(open('docker/compose.yaml'))['services']['qdrant']['image'])"
podman --connection podman-machine-default run --rm -d --name marlowe-local-qdrant --network pasta -p 127.0.0.1:6333:6333 $courseImage
uv run --extra qdrant python scripts/check_profile.py qdrant
podman --connection podman-machine-default stop marlowe-local-qdrant
```

Use this only with that existing rootless connection and a free local port. The explicit container name makes teardown specific to the example.

## Readiness

```sh
uv run --extra qdrant python scripts/check_profile.py qdrant
uv run --extra pgvector python scripts/check_profile.py pgvector
```

Use the corresponding client extra and backend name for another server. The check performs a private native write and search, then removes its probe collection. Vespa needs its application schema first.

## Native PostgreSQL archive recovery

The archive drill creates two uniquely named temporary databases inside the course PostgreSQL service, restores one from the other and removes both after checking the result.

PowerShell:

```powershell
Get-Content docker/init/pg_restore_drill.sh -Raw | docker compose -f docker/compose.yaml exec -T pgvector sh -s
```

macOS or Linux:

```sh
docker compose -f docker/compose.yaml exec -T pgvector sh -s < docker/init/pg_restore_drill.sh
```

The script is stored with LF endings. It uses pg_dump and pg_restore from the same pinned PostgreSQL image.

## Optional local generation

```sh
docker compose -f docker/compose.yaml --profile weaviate-generation up -d
docker compose -f docker/compose.yaml exec ollama ollama pull qwen3:0.6b
docker compose -f docker/compose.yaml exec ollama ollama create marlowe-caption -f /course/Modelfile
uv run --extra weaviate python modules/14_weaviate/examples/06_local_generation.py
docker compose -f docker/compose.yaml --profile weaviate-generation down
```

The caption preset uses the pinned Qwen base model with a small context, deterministic sampling and bounded output. Initial model loading can take longer than a warm query. The server module and client use explicit timeouts.

## Cleanup

The example adapters drop only their randomly named collections or tables when the session ends. Native backups and provider weights remain in the named profile volumes until the course cleanup is explicitly requested. Use `uv run python scripts/cleanup.py` to preview those resources before its removal option. The development-only rootless verification resources are removed separately after the final checks.
