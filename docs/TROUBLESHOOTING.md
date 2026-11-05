# Troubleshooting

Start with `uv run python scripts/check_env.py`; add `--services` for local ports and Ollama. Run commands from the repository root. Use the [Tier 5 runbook](TIER5_RUNBOOK.md) for engine-specific recovery procedures.

| Symptom | Check and fix |
|---|---|
| Unsupported Python version | Use Python 3.12. `uv sync --locked` follows `.python-version`; do not delete the lock to solve an interpreter mismatch. |
| Missing `common` import | Install the editable project with uv or the pip instructions in [setup](SETUP.md); do not run a copied example outside its checkout. |
| Model not cached | Saved queries need no model. For custom queries, run `uv run --extra models python scripts/embed_data.py --download` once, then use local loading. |
| Missing SQLite/Streamlit package | Include `--extra embedded` or `--extra apps` on the uv command. A later plain `uv run` synchronizes back to base extras. |
| Dimension or embedding-space mismatch | Product/query vectors must share model revision, preprocessing, and normalization. Re-embed both sides rather than padding or truncating vectors. |
| Checksum or stale text error | Restore the included artifacts together or regenerate matching products and embeddings. Do not manually edit the manifest to accept corrupt bytes. |
| Empty filtered result | Check spelling, field types, stock/region constraints, and selected catalog size. Missing fields do not match. A strict filter may legitimately exclude every record. |
| Low filtered neighbor recall | Compare against exact neighbors inside the eligible set, not the unfiltered top k. Later approximate indexes may need more candidates or prefiltering. |
| Strict ID recall below 1 on exact scans | Inspect duplicate/tied vectors and numeric precision. Primary recall accepts only ties at the cutoff and still requires strictly closer neighbors. |
| Slow build or high memory | Start with the included 10k subset. Full generation and embedding use batches. Install one model/profile at a time; do not load all optional engines. |
| Docker cannot connect / missing named pipe | Start Docker Desktop or your chosen Linux engine and inspect `docker context ls`. The selected context may point to an engine that is stopped. |
| Windows WSL2 startup problem | Confirm your engine's WSL2 requirements and virtualization settings using its official troubleshooting guide. Keep the no-Docker path working while fixing the host. |
| `netavark` says `nft` failed | This was observed with the local Podman engine before PostgreSQL started. Repair that engine's networking or select a working Docker engine. Do not disable host firewall protections or repeatedly rebuild course volumes as a workaround. |
| Port already allocated | Inspect the owning application. Change the host mapping and matching `.env` endpoint together, or intentionally stop your own conflicting service. Never kill an unknown service. |
| Container exits / out of memory | Read that service's Compose logs and engine resource limits. Start one profile. Milvus includes multiple services; a single container's limit is not the whole budget. |
| Client/server incompatibility | Use exact lock and image pins. Image availability is not runtime compatibility; consult [verification notes](VERIFICATION_NOTES.md) before upgrading either side. |
| Windows paths or cleanup access denied | Quote paths with spaces, use repository-relative commands, and close processes holding files. Cleanup rejects junctions and external roots. |
| `asyncio.run()` fails in Jupyter | Jupyter already runs an event loop. Use top-level `await` for async clients or execute the synchronous scripts from a terminal. |
| Native engine test waits indefinitely in a restricted process | Windows event-loop socketpairs may require local loopback access. Run the same local test in a normal terminal; keep external-host blocking enabled. |

No example should silently install a model or contact a remote database. If an error is unexpected, include the command, platform, installed versions, and a redacted traceback in a bug report. Do not include `.env` values or private records.

## Bonus lessons and final capstone

| Symptom | Check and fix |
|---|---|
| Qdrant rejects a 150 MB JSON payload | Use the corrected bounded upsert batches in the shared adapter. A 10k-vector payload can exceed the server limit even though local mode accepts it. Individual unusually large records still need an explicit size policy. |
| TypeScript cannot find native.js or the vector fixture | From B1, run `npm ci --ignore-scripts` and `npm run build`; from the repository root, run `python scripts/prepare_bonus.py`. Node 22+ is required; 24.18.0 was tested. |
| TLS verification fails | Start the secure profile, trust only the generated local CA, and use localhost as specified. Regenerate expired local certificates with the preparation procedure; do not disable verification. Plain HTTP Qdrant and TLS Qdrant cannot share port 6333. |
| Another writer owns TinyVec | Close the existing service and use one worker. Do not remove writer.lock to bypass a live process lock. |
| WAL checksum/sequence corruption | Preserve the log and restore a verified backup. Only an incomplete final frame is automatically truncated; complete corrupt records fail closed. |
| Notebook skips a native bonus cell | Prepare its optional package/service, then list its profile in MARLOWE_NOTEBOOK_PROFILES. A skipped cell is not native verification. |
| Public benchmark subset missing | Run `python scripts/download_benchmarks.py --download` explicitly. The license/checksum manifest is part of the experiment. |
| Capstone starter fails acceptance | Expected until implemented. Use `scripts/check_capstone.py <starter-path> --smoke` first, then complete the documented contract. |

The B2 service binds to loopback in its documented launch command and has no authentication. Its lock makes simultaneous callers safe by serializing access; it is not a multiworker server. Native Podman verification helpers remove their owned pods in finally blocks; `cleanup.py` handles the documented Docker Compose projects and generated data, not arbitrary Podman resources or installed toolchains.
