# Bonus and capstone evidence

All observations are from executed code. Records are append-only and include command, hardware and provenance. Whole-script feature timings are not database query latency. The final [validation](validation.json) and [delivery inventory](delivery-inventory.json) reconcile the release.

- [Qdrant TypeScript](typescript-qdrant-3139a021.json)
- [Weaviate TypeScript](typescript-weaviate-225861cf.json)
- [Durable service](durable-service-05459c2a.json)
- [Fashion-MNIST HNSW](public-benchmark-50dee323.json)
- [Corrected RaBitQ measurement](rabitq-native-0a6f1ea7.json)

## Superseded timing records

The following early RaBitQ records timed selection using precomputed reference distances instead of recomputing candidate distances. Their recall/byte observations remain valid, but do not use their scratch p95 as full rescoring latency. Corrected records contain query_sha256 and recompute candidate distances inside the timer.

- [rabitq-160cb3a2.json](rabitq-160cb3a2.json)
- [rabitq-native-05c7227c.json](rabitq-native-05c7227c.json)
- [rabitq-native-5cfbe00d.json](rabitq-native-5cfbe00d.json)
- [rabitq-scratch-5240e84b.json](rabitq-scratch-5240e84b.json)
- [rabitq-scratch-a6ebbb61.json](rabitq-scratch-a6ebbb61.json)

## Capstones

- [capstone-bakeoff-ae191d97](capstone-bakeoff-ae191d97.json)
- [capstone-flagship-6f5c96dc](capstone-flagship-6f5c96dc.json)
- [capstone-rag-e22797c1](capstone-rag-e22797c1.json)
- [capstone-tenants-c427a48d](capstone-tenants-c427a48d.json)

[Research plot](../plots/bonus_research.png) · [Phase 8 interpretation](../../docs/PHASE_8_REPORT.md)
