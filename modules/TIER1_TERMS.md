# Tier 1 vocabulary

These terms cover the first five lessons. The full course glossary is a later deliverable.

| Term | Meaning in this course |
|---|---|
| Vector / coordinate | An ordered list of numbers; a coordinate is one entry. A designed coordinate can represent a known feature. |
| Dimension / shape | Dimension is the number of entries per vector; a matrix with shape `(N, D)` stores N D-dimensional vectors. |
| Embedding / space | A model’s numeric representation of an input; the model, revision, and preparation recipe define the compatible space. |
| Dot product | Sum of matching-coordinate products; both direction and magnitude affect it. |
| Norm / normalization | A norm measures length. Unit normalization divides a nonzero vector by its length. |
| Cosine / L2 | Cosine compares direction; L2 is straight-line Euclidean distance. |
| Top k / neighbor | A neighbor is a nearby item under a specified metric. Top k is the first k ranked items. |
| Exact / approximate | Exact search examines the eligible items to obtain the true nearest neighbors; approximate search can trade accuracy for cost. |
| Metadata / filter | Ordinary attributes such as stock or region; a filter defines which records are eligible. |
| Insert / upsert | Insert adds only new IDs. Upsert inserts a missing ID or replaces an existing record. |
| Snapshot | A saved set of vectors, records, and schema that can be loaded together. |
| Batch / cache | A batch processes several inputs together. A cache reuses a result only when its complete key matches. |
| PCA | A linear projection onto directions of high variation; two dimensions cannot preserve all original information. |
| Ground truth / qrels | Ground truth here means exact eligible neighbors for index evaluation. Qrels are independent query-to-product relevance grades. |
| Recall@k / precision@k | Neighbor recall measures recovered exact neighbors; judged precision measures unique useful hits per requested k. |
| MRR / nDCG | Mean reciprocal rank rewards an early first useful answer. Normalized discounted cumulative gain rewards higher grades near the top. |
| Latency / throughput | Latency is time for one request. Throughput counts completed requests per wall-clock second. |
| Percentile / RSS | A percentile describes a location in ordered observations. RSS is resident process memory, not just index size. |
| Library / embedded database / server | A library supplies code in your process; an embedded database also manages records locally; a server exposes a separate service. |
| RAG | Retrieval-augmented generation: fetch relevant evidence before asking a model to answer. |
