"""Sparse lexical ranking, rank fusion, and late-interaction scoring."""

import math
import re
from collections import Counter, defaultdict

import numpy as np


def tokens(text):
    return re.findall(r"[\w-]+", text.casefold())


class BM25:
    def __init__(self, texts):
        self.postings = defaultdict(list)
        self.lengths = []
        for row, text in enumerate(texts):
            words = tokens(text)
            self.lengths.append(len(words))
            for term, freq in Counter(words).items():
                self.postings[term].append((row, freq))
        self.mean = sum(self.lengths) / max(1, len(self.lengths))

    def rank(self, text, eligible=None, k=10):
        scores = defaultdict(float)
        for term in set(tokens(text)):
            posting = self.postings.get(term, [])
            idf = math.log1p((len(self.lengths) - len(posting) + 0.5) / (len(posting) + 0.5))
            for row, freq in posting:
                if eligible is None or row in eligible:
                    norm = 0.25 + 0.75 * self.lengths[row] / max(self.mean, 1)
                    scores[row] += idf * freq * 2.2 / (freq + 1.2 * norm)
        return sorted(scores, key=lambda i: (-scores[i], i))[:k]


def fuse(rankings, constant=60):
    if constant < 1:
        raise ValueError("Rank constant must be positive")
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, key in enumerate(dict.fromkeys(ranking), 1):
            scores[key] += 1 / (constant + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))


def maxsim(query_tokens, document_tokens):
    q = np.asarray(query_tokens, dtype=np.float32)
    d = np.asarray(document_tokens, dtype=np.float32)
    if (
        q.ndim != 2
        or d.ndim != 2
        or not len(q)
        or not len(d)
        or q.shape[1] != d.shape[1]
        or not np.isfinite(q).all()
        or not np.isfinite(d).all()
    ):
        raise ValueError("Expected nonempty finite token matrices in the same space")
    return float((q @ d.T).max(axis=1).sum())
