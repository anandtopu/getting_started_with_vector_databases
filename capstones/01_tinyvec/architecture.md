# Architecture

```mermaid
flowchart TD
    records --> validate --> index[HNSW or PQ candidates] --> rescore[Full-vector rescore] --> filter[Eligible hits]
    index --> snapshot[Versioned files] --> restore[Rebuild index]
```

The reference composes the tested shared implementations instead of maintaining a second copy. The learner owns the project contract; shared adapters own vector validation, filter translation and cleanup. IDs and model-space metadata must survive every boundary. Capture the exact command and environment with every measurement.

## Failure boundaries

IndexedTinyVec retains full vectors for rescoring. PQ code bytes are not total resident memory. The 100-row acceptance fixture tests behavior; the 500-row measured comparison is descriptive, not proof of large-scale ANN quality.

A failed assertion stops the run. Do not count incomplete runs as successful measurements. Database collections and temporary files belong to one session; source fixtures remain unchanged. Optional native operations require explicit setup and credentials from the ignored course cache.
