# Optional managed databases

The full course can run locally. This worksheet compares hosted offerings without creating accounts or resources. Provider pages were checked during Phase 5 on November 4–5, 2026. Recheck plan eligibility in the account before any optional deployment.

| Offering | What it supplies | Pricing units to inspect | Local learning equivalent |
|---|---|---|---|
| Pinecone | Managed dense and sparse indexes and inference options | Stored data, read/write usage, inference and plan minimums. The public Starter plan is free within its limits. | Qdrant named dense/sparse fields |
| Turbopuffer | Object-storage-backed search namespaces | Storage, query/write work and minimum usage commitments | LanceDB tables and the disk-page experiment |
| Zilliz Cloud | Managed Milvus-compatible service | Deployment mode, storage, request or compute units and Free Tier eligibility | Milvus standalone |
| Qdrant Cloud | Managed clusters and backups | Cluster memory/disk capacity, replicas and region. The advertised free cluster has resource limits. | Local Qdrant |
| Weaviate Cloud | Managed collections and model integrations | Cluster plan, indexed dimensions, storage and separately billed model use. Its public free plan has stated limits. | Local Weaviate |
| AWS OpenSearch | Provisioned and serverless search | Instance or serverless capacity, storage, replicas and transfer | Local Elasticsearch |
| Azure AI Search | Hosted search and vector indexing | Search units, storage limits and optional semantic/model usage | Local vector plus full-text comparisons |
| Google Vertex AI Vector Search | Managed index deployment and query serving | Index build, deployed capacity, storage and regional charges | Local FAISS or Milvus |

Sources for plans and billing units are [Pinecone](https://www.pinecone.io/pricing/), [Turbopuffer](https://turbopuffer.com/pricing), [Zilliz](https://zilliz.com/pricing), [Qdrant](https://qdrant.tech/pricing/), [Weaviate](https://weaviate.io/pricing), [AWS](https://aws.amazon.com/opensearch-service/pricing/), [Azure](https://azure.microsoft.com/en-us/pricing/details/search/) and [Google](https://cloud.google.com/vertex-ai/pricing).

Use an explicitly free plan if you choose an optional hosted exercise. Treat a paid minimum, a temporary credit or a trial requiring conversion as a separate purchasing decision. The repository has no cloud account setup or deployment step.

## Estimate before creating a resource

Write down row count, dimensions, precision, replicas, stored metadata bytes, queries per day and expected filters. Then identify each provider’s billed unit. A minimum monthly charge may dominate low usage. Query fan-out, model calls and transfer can add costs beyond vector storage.

Run `uv run python modules/16_landscape/examples/09_managed_cost.py` to inspect a hypothetical minimum-charge calculation. Its values are invented inputs for the arithmetic exercise. Replace them with the verified units for a chosen plan before using the estimate for a decision.

## Remove an optional experiment

Record every resource name when creating it. At the end, delete its indexes or namespaces and any snapshots or object-storage copies you created. For a cluster service, delete the cluster itself. For a cloud platform, also remove the associated deployment, storage and monitoring resources if they were created only for the experiment. Revoke the experiment’s key and inspect the provider console for remaining billable resources.

A deleted local configuration file does not remove the provider resource. Consult the provider’s current deletion workflow and verify its final state. No managed resource was created during Phase 5.
