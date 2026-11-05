# Tier 1 | Vectors to a working store

## The core contract

A Record has an ID, vector, metadata and optional text. A CollectionSpec fixes dimension, metric and model space. Validate finite values and reject zero vectors for cosine search. Equal dimensions do not imply equal model spaces.

## Three formulas

dot(x,q) = sum(x_i*q_i)
cosine(x,q) = dot(x,q)/(norm(x)*norm(q))
L2_squared(x,q) = sum((x_i-q_i)^2)
float32 vector bytes = rows * dimensions * 4

## Build TinyVec

Validate the complete batch, replace existing IDs, invalidate the derived index, then search only eligible records. Persist schema, vectors and metadata together; restore in a fresh process and compare IDs. Never load untrusted arbitrary-object serialization.

## Measure honestly

ANN recall compares retrieved neighbors with exact neighbors. Relevance uses human or synthetic judgments. State k, tie handling, filter eligibility and dtype. Time embedding, build and retrieval separately; report sample counts with percentiles.

## Run from the repository root

uv run python examples/01_quickstart.py
uv run python examples/02_filtered_search.py
uv run python scripts/checkpoint_tier1.py

## Before moving on

Explain why the mug-warmer query works without the exact phrase. Show replacement, deletion and restore. Confirm model revision/preprocessing in the vector manifest. Included real-model vectors let the first search run without downloading a model. See Modules 00-04 and docs/MENTAL_MODEL.md.
