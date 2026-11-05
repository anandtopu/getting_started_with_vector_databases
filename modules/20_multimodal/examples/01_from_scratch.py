"""Score genuine image and text vectors in the same SigLIP space.

Run: uv run  python modules/20_multimodal/examples/01_from_scratch.py
Expected: a ranked image gallery for a text query.
CPU: seconds to one minute. Needs: base, prepared image vectors. No implicit downloads.
"""

from common.apps.artifacts import load_artifact
from common.embeddings import normalize


def main() -> None:
    ids, images, model = load_artifact("image_gallery")
    _, queries, query_model = load_artifact("image_queries")
    assert model["space"] == query_model["space"]
    # KEY IDEA: normalize before a cosine dot product. MiniLM is a different space.
    scores = normalize(images) @ normalize(queries[0])
    ranking = sorted(range(len(ids)), key=lambda i: (-float(scores[i]), ids[i]))[:5]
    print([(ids[i], float(scores[i])) for i in ranking])


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
