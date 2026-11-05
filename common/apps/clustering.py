"""Review themes and distance-based outliers, with no invented semantic ground truth."""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from common.embeddings import normalize


def review_themes(texts, vectors, clusters=6):
    if len(texts) != len(vectors) or not 2 <= clusters < len(texts):
        raise ValueError("Aligned rows and 2 <= clusters < review count required")
    matrix = normalize(vectors)
    model = KMeans(n_clusters=clusters, n_init=10, random_state=20261104).fit(matrix)
    distances = np.linalg.norm(matrix - model.cluster_centers_[model.labels_], axis=1)
    # Outliers are far from their assigned theme. This is a heuristic, not a fraud label.
    lexical = TfidfVectorizer(stop_words="english", min_df=2)
    terms = lexical.fit_transform(texts)
    vocabulary = lexical.get_feature_names_out()
    themes = []
    for label in range(clusters):
        members = np.flatnonzero(model.labels_ == label)
        scores = np.asarray(terms[members].mean(axis=0)).ravel()
        words = vocabulary[np.argsort(-scores, kind="stable")[:5]].tolist()
        exemplar = int(members[np.argmin(distances[members])])
        themes.append(
            {
                "cluster": label,
                "count": len(members),
                "words": words,
                "exemplar": exemplar,
                "text": texts[exemplar],
            }
        )
    return {
        "labels": model.labels_.tolist(),
        "themes": themes,
        "outlier_scores": distances.tolist(),
        "outliers": np.argsort(-distances, kind="stable")[:10].tolist(),
    }
