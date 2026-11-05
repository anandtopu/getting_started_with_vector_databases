# Measured application results: 20_multimodal

[photo raw JSON](../../../results/tier4/photo-2e6b43a8.json)

| Mode | Held-out nDCG@10 |
|---|---|
| text_to_image | 0.4937 |
| photo | 0.5500 |
| fused | 0.7104 |

The exact query image ID is excluded from retrieval and judgments. The gallery contains 200 Pillow illustrations and repeated drawing templates. Each mode has ten held-out query families. Fusion weight 0.7 is an illustrative fixed policy, not an optimized production setting. These results do not establish quality on photographs.


Backend: **qdrant-local**, a single owned local Qdrant client per application evaluation. Hardware and package versions are embedded in every raw JSON. Model identities and content hashes are in the linked run's artifact manifests. Judgments are synthetic. No hosted service was used.

[Comparison plot](../../../checkpoints/tier4/results/comparison.png) · [Method and reproduction](../../../checkpoints/tier4/README.md)
