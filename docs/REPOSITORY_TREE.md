# Repository structure

This is the structural guide. The [machine inventory](../results/bonus/delivery-inventory.json) lists delivered lesson and capstone files; the [final audit](DEFINITION_OF_DONE.md) records verification boundaries. See the [Phase 2 report](PHASE_2_REPORT.md) for the delivered foundation and the [Phase 3 report](PHASE_3_REPORT.md) for Tier 1, and the [Phase 4 report](PHASE_4_REPORT.md) for Tier 2, and the [Phase 5 report](PHASE_5_REPORT.md) for Tier 3, and the [Phase 6 report](PHASE_6_REPORT.md) for Tier 4, and the [Phase 7 report](PHASE_7_REPORT.md) for Tier 5. Braces below enumerate separate files; `<module>` and `<run-id>` are naming schemas, not literal filenames or unfinished source code. The module expansion lists every core and bonus directory. Each module has the complete contents shown in the module schema.

```text
getting_started_with_vector_databases/
├── README.md
├── PLAN.md
├── LEARNING_PATH.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── .github/
│   ├── workflows/{ci,integration,live,links}.yml
│   ├── ISSUE_TEMPLATE/{bug,content_error,feature_request}.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── common/
│   ├── __init__.py
│   ├── {data,embeddings,llm,pretty,settings,errors}.py
│   ├── stores/
│   │   ├── __init__.py
│   │   ├── {protocol,types,filters,capabilities,registry}.py
│   │   ├── {tinyvec,faiss,usearch,hnswlib}.py
│   │   ├── {chroma,lancedb,sqlite_vec,duckdb}.py
│   │   ├── {pgvector,qdrant,weaviate,milvus}.py
│   │   └── {elasticsearch,redis,mongodb,vespa}.py
│   ├── bench/
│   │   ├── __init__.py
│   │   └── {config,ground_truth,metrics,runner,resources,hardware,sweep,plots,leaderboard}.py
│   ├── search/{__init__,bm25,fusion,multivector,rerank,query_parser}.py
│   ├── apps/{__init__,product_search,rag,recommendations,deduplication,clustering,multimodal}.py
│   ├── ops/{__init__,ingestion,tenancy,migration,backup,capacity,cache,replication}.py
│   └── security/{__init__,identity,audit,deletion}.py
├── tinyvec/
│   ├── __init__.py
│   ├── {store,storage,metrics,filters,persistence}.py
│   ├── {lsh,ivf,hnsw,quantization,pq,mmap,hybrid}.py
│   └── {wal,service}.py
├── docker/
│   ├── compose.yaml
│   ├── init/{pgvector.sql,redis.conf,milvus.yaml}
│   ├── prometheus/prometheus.yml
│   ├── grafana/provisioning/{datasources.yaml,dashboards.yaml}
│   ├── grafana/dashboards/marlowe.json
│   └── vespa/{services.xml,hosts.xml,schemas/products.sd}
├── configs/
│   ├── models.yaml
│   ├── data.yaml
│   ├── applications/{search,rag,recommendations,deduplication,multimodal}.yaml
│   ├── bench/<feature-id>.yaml
│   ├── sweeps/{ivf,hnsw,pq,filters,hybrid,capacity}.yaml
│   └── load/{locustfile.py,small.yaml}
├── data/
│   ├── README.md
│   ├── manifest.json
│   ├── {products_10k,embeddings_10k,query_embeddings}.parquet
│   ├── sellers.json
│   ├── help_center/<article-id>.md
│   ├── eval/{search_qrels,rag_qa}.jsonl
│   ├── eval/judging_worksheet.csv
│   ├── fixtures/{products,queries,events,duplicates}.jsonl
│   ├── fixtures/images/<product-id>.png
│   ├── {products,reviews,events,duplicates}.parquet       [generated, ignored]
│   ├── images/<product-id>.png                          [generated, ignored]
│   ├── generated/                                      [generated, ignored]
│   └── benchmarks/                                     [downloaded, ignored]
├── modules/
│   ├── 00_setup/
│   ├── 01_vectors_similarity/
│   ├── 02_embeddings/
│   ├── 03_tinyvec/
│   ├── 04_benchmarking/
│   ├── 05_ann_lsh/
│   ├── 06_ivf/
│   ├── 07_hnsw/
│   ├── 08_quantization/
│   ├── 09_disk_scale/
│   ├── 10_filtering_hybrid/
│   ├── 11_embedded/
│   ├── 12_pgvector/
│   ├── 13_qdrant/
│   ├── 14_weaviate/
│   ├── 15_milvus/
│   ├── 16_landscape/
│   ├── 17_product_search/
│   ├── 18_rag/
│   ├── 19_recommendations/
│   ├── 20_multimodal/
│   ├── 21_operations/
│   ├── 22_performance/
│   ├── 23_security_reliability/
│   └── bonus/
│       ├── B1_other_languages/
│       ├── B2_tinyvec_service/
│       ├── B3_research_benchmarks/
│       └── B4_whats_new/
├── checkpoints/{tier_1,tier_2,tier_3,tier_4,tier_5}.md
├── playground/
│   ├── app.py
│   └── pages/{01_catalog_map,02_search,03_index_tuning,04_hnsw_graph,05_applications}.py
├── results/
│   ├── README.md
│   ├── leaderboard.md
│   ├── runs/<run-id>.json
│   └── plots/<feature-id>_<dataset-hash>_<hardware-id>.png
├── capstones/
│   ├── 01_tinyvec/
│   ├── 02_database_bakeoff/
│   ├── 03_rag_assistant/
│   ├── 04_multitenant_search/
│   └── 05_marlowe_search/
├── cheatsheets/
│   ├── {tier_1,tier_2,tier_3,tier_4,tier_5}.md
│   ├── index_types.md
│   └── database_apis.md
├── docs/
│   ├── FEATURE_MAP.md
│   ├── REPOSITORY_TREE.md
│   ├── MENTAL_MODEL.md
│   ├── CHOOSING_A_VECTOR_DATABASE.md
│   ├── INDEX_TUNING_GUIDE.md
│   ├── TERMS_ACROSS_DATABASES.md
│   ├── MEMORY_MATH.md
│   ├── GLOSSARY.md
│   ├── READING_LIST.md
│   ├── TROUBLESHOOTING.md
│   ├── VERIFICATION_NOTES.md
│   ├── DEFINITION_OF_DONE.md
│   └── benchmark_datasets.json
├── scripts/
│   ├── {build_data,embed_data,download_benchmarks,check_env}.py
│   ├── {run_bench,cleanup,run_all_examples}.py
│   ├── {memory_calculator,check_course,check_links,run_notebooks}.py
│   ├── {prepare_offline,export_requirements,verify_artifacts}.py
│   └── {backup,restore,migrate,evaluate}.py
├── tests/
│   ├── conftest.py
│   ├── unit/test_<component>.py
│   ├── contracts/{conftest,test_vector_store,test_capabilities}.py
│   ├── integration/test_<database>.py
│   ├── live/test_<model_or_application>.py
│   └── content/test_course_contract.py
└── research/
    ├── pypi-2026-11-04.json
    ├── docker-tags-2026-11-04.json
    ├── exact-images-2026-11-04.json
    ├── models-2026-11-04.json
    ├── upstream-checks-2026-11-04.json
    ├── milvus-upstream-compose.yaml
    ├── ollama-model-digest.json
    ├── ollama-qwen3-0.6b.json
    ├── source-urls.json
    └── source-link-check.json
```

Every module expands as follows. Additional examples are required where three would not cover the module's distinct concepts. Database modules have separate native API examples for each covered database.

```text
<module>/
├── README.md
├── examples/
│   ├── 01_from_scratch.py
│   ├── 02_production.py
│   └── 03_measure.py
├── use_case/marlowe.py
├── exercises/{01_practice,02_apply,03_stretch}.py
├── solutions/{01_practice,02_apply,03_stretch}.py
├── notebook.ipynb
├── results/README.md
├── quiz.md
└── tests/{test_examples,test_exercises}.py
```

Each feature-map production-example target refers to `02_production.py` in this schema unless a more specific filename is named. A module can have several configs and many leaderboard runs. Module result pages link to raw central runs rather than copying inconsistent numbers. Exercise tests accept a selected implementation path and run against both learner code and the reference package.

Every capstone expands to `README.md`, `architecture.md`, `starter/`, `solution/`, `tests/`, `evaluation.yaml`, `rubric.md`, and `extensions.md`. Runnable baseline starter code is separate from the full solution. B1 additionally contains `package.json`, its verified package lock, `tsconfig.json`, and `src/`; npm packages and APIs will be verified immediately before that optional phase is implemented.

## Naming and ownership rules

- `common/` and `tinyvec/` are installed packages; module directories are not import targets. Run examples by path.
- Each feature ID in the feature map owns `configs/bench/<feature-id>.yaml` and the future `results/leaderboard.md#<feature-id>` section. Non-retrieval experiments use typed operation metrics in the same runner and are not ranked as ANN throughput.
- Generated caches use `.cache/marlowe/`. Only paths declared in the data manifest may be deleted by cleanup, even where a generated Parquet file sits directly under `data/`.
- `docker/compose.yaml` contains the beginner/database profiles; `docker/compose.tier5.yaml` is the separate credential-required TLS/monitoring deployment introduced in Phase 7. Do not bind both Qdrant profiles to port 6333. The file in `research/` is untouched upstream evidence, not a second supported deployment.
- Empty future folders or placeholder files are not created merely to make this tree appear complete. Actual files arrive with their implementation phase.
