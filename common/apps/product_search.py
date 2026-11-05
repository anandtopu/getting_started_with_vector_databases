"""Marlowe v2: eligibility before candidate selection, rank fusion and optional reranking."""

import difflib
import re
import time
from dataclasses import dataclass

from common.data import load_products, load_vectors, product_texts, records_from_products
from common.search.query_parser import combine, parse_query
from common.settings import data_dir
from common.stores.filters import matches, parse_filter
from common.stores.types import Hit
from tinyvec.hybrid import BM25, fuse, tokens


@dataclass
class SearchResult:
    hits: list[Hit]
    parsed_text: str
    filter: dict | None
    warnings: tuple[str, ...]
    corrections: dict[str, str]
    timings_ms: dict[str, float]


class ProductSearch:
    def __init__(
        self, database, limit: int = 10_000, model="minilm", seller_id=None, excluded_ids=()
    ) -> None:
        if model == "qwen":
            from common.apps.artifacts import load_artifact

            ids, self.vectors, meta = load_artifact("multilingual_products")
            self.products = load_products(limit=len(ids))
            load_artifact("multilingual_products", contents=product_texts(self.products))
            if ids != self.products.id.tolist():
                raise ValueError("Multilingual catalog IDs do not align")
        elif model == "minilm":
            self.products = load_products(limit=limit)
            self.vectors, meta = load_vectors(data_dir() / "embeddings_10k.parquet", self.products)
        else:
            raise ValueError("Choose minilm or qwen")
        self.space = meta["space"]
        if seller_id is not None or excluded_ids:
            mask = ~self.products.id.isin(excluded_ids)
            if seller_id is not None:
                mask &= self.products.seller_id == seller_id
            self.products = self.products.loc[mask].reset_index(drop=True)
            self.vectors = self.vectors[mask.to_numpy()]
        self.records = records_from_products(self.products, self.vectors)
        self.by_id = {r.id: r for r in self.records}
        self.store = database.collection(
            "products", self.records, self.space, dimensions=self.vectors.shape[1]
        )
        self.lexical = BM25([r.text + " " + r.metadata["sku"] for r in self.records])
        self.vocabulary = sorted({t for r in self.records for t in tokens(r.text) if len(t) > 3})

    def correct(self, text: str) -> tuple[str, dict[str, str]]:
        corrections = {}
        for word in tokens(text):
            if word not in self.vocabulary and len(word) > 3 and not re.search(r"\d", word):
                candidates = difflib.get_close_matches(word, self.vocabulary, n=1, cutoff=0.8)
                if candidates:
                    corrections[word] = candidates[0]
        fixed = re.sub(r"[\w-]+", lambda m: corrections.get(m[0].casefold(), m[0]), text)
        return fixed, corrections

    def search(
        self,
        text,
        vector,
        *,
        k=10,
        filter=None,
        mode="hybrid",
        typo=False,
        reranker=None,
        candidates=30,
        protect_sku=True,
    ):
        if k < 1 or candidates < k or mode not in {"dense", "lexical", "hybrid"}:
            raise ValueError("Use a known ranking mode and candidates >= k >= 1")
        start = time.perf_counter()
        parsed = parse_query(text)
        condition = combine(parsed.filter, filter)
        corrected, changes = self.correct(parsed.text) if typo else (parsed.text, {})
        eligibility = parse_filter(condition)
        eligible = {i for i, r in enumerate(self.records) if matches(r.metadata, eligibility)}
        # KEY IDEA: both branches use the same eligible set before truncation.
        dense = (
            self.store.search(vector, candidates, condition, space=self.space)
            if mode != "lexical"
            else []
        )
        lexical = (
            [self.records[i].id for i in self.lexical.rank(corrected, eligible, candidates)]
            if mode != "dense"
            else []
        )
        ranked = (
            fuse([[h.id for h in dense], lexical])
            if mode == "hybrid"
            else [(h.id, h.score) for h in dense]
            if mode == "dense"
            else [(key, 1 / (i + 1)) for i, key in enumerate(lexical)]
        )
        ranked = ranked[:candidates]
        retrieval_ms = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        if reranker is not None and ranked:
            scores = reranker.score(text, [self.by_id[key].text for key, _ in ranked])
            ranked = sorted(
                zip([key for key, _ in ranked], map(float, scores), strict=True),
                key=lambda x: (-x[1], x[0]),
            )
        if protect_sku and mode != "dense":
            # A literal identifier is a deterministic business rule, separate from model scores.
            literal = parsed.text.strip().casefold()
            exact = {
                self.records[i].id
                for i in eligible
                if self.records[i].metadata["sku"].casefold() == literal
            }
            ranked.sort(key=lambda item: item[0] not in exact)
        hits = [
            Hit(key, score, self.by_id[key].metadata, self.by_id[key].text)
            for key, score in ranked[:k]
        ]
        return SearchResult(
            hits,
            parsed.text,
            condition,
            parsed.warnings,
            changes,
            {"retrieval": retrieval_ms, "reranking": (time.perf_counter() - start) * 1000},
        )
