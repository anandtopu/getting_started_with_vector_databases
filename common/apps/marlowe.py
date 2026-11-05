"""One database session connects all five Marlowe application capabilities."""

import time

from common.apps.artifacts import load_artifact
from common.apps.database import AppDatabase
from common.apps.deduplication import pair_scores
from common.apps.product_search import ProductSearch
from common.apps.recommendations import recommend
from common.data import search_queries
from common.embeddings import ImageTextEncoder, TextEncoder, cached_texts, frozen_query
from common.search.query_parser import parse_query
from common.settings import data_dir
from common.tier4 import open_photos, open_rag


class MarloweSearch:
    def __init__(self, backend="tinyvec", limit=1000, seller_id=None, excluded_ids=()):
        self.seller_id, self.excluded_ids = seller_id, set(excluded_ids)
        self.database = AppDatabase(backend)
        try:
            self.products = ProductSearch(
                self.database, limit, seller_id=seller_id, excluded_ids=excluded_ids
            )
            self.rag, self.qa, self.rag_vectors = open_rag(self.database)
            self.photos, self.image_vectors, _ = open_photos(self.database, seller_id, excluded_ids)
            texts = [
                parse_query(q["text"]).text or q["text"]
                for q in search_queries()
                if q["type"] != "photo"
            ]
            ids, vectors, _ = load_artifact("queries_parsed", contents=texts)
            self.query_vectors = dict(zip(ids, vectors, strict=True))
        except Exception:
            self.database.close()
            raise

    def search(self, *, query_id="q000", text=None, k=5, filter=None, multilingual=False):
        embedding_ms = 0.0
        search = self.products
        if multilingual:
            if not hasattr(self, "multilingual_search"):
                self.multilingual_search = ProductSearch(
                    self.database,
                    model="qwen",
                    seller_id=self.seller_id,
                    excluded_ids=self.excluded_ids,
                )
            search = self.multilingual_search
        if text:
            from common.embeddings import multilingual_spec
            from common.search.query_parser import parse_query

            start = time.perf_counter()
            vector = cached_texts(
                [parse_query(text).text or text],
                TextEncoder(multilingual_spec() if multilingual else None),
                "query",
            )[0]
            embedding_ms = (time.perf_counter() - start) * 1000
        else:
            queries = {q["id"]: q for q in search_queries() if q["type"] != "photo"}
            if query_id not in queries:
                raise ValueError("Choose a saved text query")
            text = queries[query_id]["text"]
            vector = self.query_vectors.get(query_id)
            if multilingual:
                from common.embeddings import multilingual_spec

                ids, values, _ = load_artifact("multilingual_queries")
                vector = (
                    values[ids.index(query_id)]
                    if query_id in ids
                    else cached_texts([text], TextEncoder(multilingual_spec()), "query")[0]
                )
            if vector is None:
                vector, _ = frozen_query(query_id, data_dir())
        result = search.search(text, vector, k=k, filter=filter, typo=not multilingual)
        result.timings_ms["embedding"] = embedding_ms
        return result

    def help(self, *, question_id="rag-000", text=None, generate=False):
        if text:
            vector = cached_texts([text], TextEncoder(), "query")[0]
        else:
            question = next((q for q in self.qa if q["id"] == question_id), None)
            if question is None:
                raise ValueError("Unknown saved help question")
            text, vector = question["question"], self.rag_vectors[question_id]
        hits = self.rag.retrieve(text, vector)
        return {"passages": hits, "generation": self.rag.answer(text, hits) if generate else None}

    def similar(self, product_id="p0000000", k=5, relevance=0.7):
        if product_id not in self.products.by_id:
            raise ValueError("Product is outside the loaded catalog")
        query = self.products.by_id[product_id].vector
        ids = recommend(self.products, query, exclude=[product_id], k=k, relevance=relevance)
        return [{"id": key, **self.products.by_id[key].metadata} for key in ids]

    def duplicate(self, first, second, threshold):
        if first not in self.products.by_id or second not in self.products.by_id:
            raise ValueError("Both products must be in the loaded catalog")
        if not -1 <= threshold <= 1:
            raise ValueError("Cosine threshold must be in [-1, 1]")
        score = float(
            pair_scores(
                [{"source_id": first, "duplicate_id": second}],
                {key: self.products.by_id[key].vector for key in [first, second]},
            )[0]
        )
        return {
            "score": score,
            "threshold": threshold,
            "review_candidate": score >= threshold,
            "action": "Review both listings before merging",
        }

    def photo(self, *, product_id="p0000000", text=None, image=None, k=5, image_weight=0.7):
        exclude = []
        if image is not None:
            vector = ImageTextEncoder().encode([image], "image")[0]
        elif text:
            vector = ImageTextEncoder().encode([text], "text")[0]
        else:
            if product_id not in self.photos.ids:
                raise ValueError("Photo is outside the prepared gallery")
            vector = self.image_vectors[self.photos.ids.index(product_id)]
            exclude = [product_id]
        return self.photos.search(
            vector, space=self.photos.space, k=k, image_weight=image_weight, exclude=exclude
        )

    def close(self):
        try:
            self.photos.close()
        finally:
            self.database.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
