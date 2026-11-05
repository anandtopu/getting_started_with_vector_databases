"""Cluster real review embeddings and inspect high-distance outliers.

Run: uv run  python modules/19_recommendations/examples/04_review_themes.py
Expected: six themes, representative text and ten candidate outliers.
CPU: seconds to one minute. Needs: base, prepared review vectors. No implicit downloads.
"""

from common.apps.clustering import review_themes
from common.teaching import evidence
from common.tier4 import review_data


def main() -> None:
    reviews, vectors, _ = review_data()
    result = review_themes(reviews.text.tolist(), vectors)
    for theme in result["themes"]:
        print(theme)
    # KEY IDEA: distance is a review priority, not a fraud or correctness label.
    print(reviews.iloc[result["outliers"]][["id", "text"]].to_dict("records"))
    evidence("review-themes", result, tier=4)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
