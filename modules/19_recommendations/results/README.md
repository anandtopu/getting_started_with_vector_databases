# Measured application results: 19_recommendations

[recommendations raw JSON](../../../results/tier4/recommendations-f7e95363.json)

| MMR relevance | Users | Future purchase recall@10 | Mean pairwise distance | Seen leaks |
|---|---|---|---|---|
| 1.0000 | 100 | 0.0100 | 0.0076 | 0 |
| 0.7000 | 100 | 0.0200 | 0.0131 | 0 |
| 0.3000 | 100 | 0.0100 | 0.0169 | 0 |

| Duplicate split | Pairs | Threshold | Precision | Recall | F1 |
|---|---|---|---|---|---|
| development | 320 | 0.9349 | 1.0000 | 1.0000 | 1.0000 |
| test | 80 | 0.9349 | 1.0000 | 1.0000 | 1.0000 |

The original generator's first 100-user audit had zero evaluable unseen-purchase cases. The final run uses the separately labeled 700-event temporal fixture. Duplicate evaluation includes only 400 pairs with both IDs in the committed 10k catalog, excluding 1,600 unavailable pairs. The same-kind recommendation fixture and planted duplicates are easy synthetic tasks. Six review themes and ten outlier candidates are in the raw result, without human topic or anomaly labels.


Backend: **qdrant-local**, a single owned local Qdrant client per application evaluation. Hardware and package versions are embedded in every raw JSON. Model identities and content hashes are in the linked run's artifact manifests. Judgments are synthetic. No hosted service was used.

[Comparison plot](../../../checkpoints/tier4/results/comparison.png) · [Method and reproduction](../../../checkpoints/tier4/README.md)
