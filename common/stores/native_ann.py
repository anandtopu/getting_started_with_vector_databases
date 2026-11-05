"""Optional native candidate generators. All searches use normalized cosine vectors."""

import numpy as np

from common.errors import CourseError


class NativeANN:
    def __init__(
        self,
        matrix,
        kind,
        nlist=16,
        nprobe=4,
        M=8,
        efConstruction=40,
        efSearch=32,
        parts=8,
        bits=4,
        seed=42,
    ):
        self.kind = kind
        self.size = len(matrix)
        if not 1 <= nprobe <= nlist or M < 2 or efConstruction < M or efSearch < 1 or bits < 1:
            raise ValueError("Invalid native index parameters")
        dim = matrix.shape[1]
        if kind == "usearch":
            from usearch.index import Index

            self.index = Index(
                ndim=dim,
                metric="cos",
                dtype="f32",
                connectivity=M,
                expansion_add=efConstruction,
                expansion_search=efSearch,
            )
            self.index.add(np.arange(self.size, dtype=np.uint64), matrix, threads=1)
        elif kind == "hnswlib":
            try:
                import hnswlib
            except ImportError as exc:
                raise CourseError("Install --extra hnswlib with a C++ build toolchain") from exc
            self.index = hnswlib.Index(space="cosine", dim=dim)
            self.index.init_index(
                max_elements=len(matrix), ef_construction=efConstruction, M=M, random_seed=seed
            )
            self.index.add_items(matrix, num_threads=1)
            self.index.set_ef(efSearch)
        else:
            import faiss

            faiss.omp_set_num_threads(1)
            lists = min(nlist, len(matrix))
            if kind == "faiss-ivf":
                self.index = faiss.IndexIVFFlat(
                    faiss.IndexFlatIP(dim), dim, lists, faiss.METRIC_INNER_PRODUCT
                )
            elif kind == "faiss-hnsw":
                self.index = faiss.IndexHNSWFlat(dim, M, faiss.METRIC_INNER_PRODUCT)
                self.index.hnsw.efConstruction = efConstruction
                self.index.hnsw.efSearch = efSearch
            elif kind == "faiss-lsh":
                self.index = faiss.IndexLSH(dim, bits)
            elif kind == "faiss-ivfpq":
                if parts < 1 or dim % parts or not 1 <= bits <= 8 or len(matrix) < 2**bits:
                    raise ValueError(
                        "IVF-PQ requires parts dividing the dimension and enough rows to train every codeword"
                    )
                self.index = faiss.IndexIVFPQ(
                    faiss.IndexFlatIP(dim), dim, lists, parts, bits, faiss.METRIC_INNER_PRODUCT
                )
                self.index.pq.cp.seed = seed
            else:
                raise ValueError(f"Unknown native index: {kind}")
            if hasattr(self.index, "cp"):
                self.index.cp.seed = seed
            if not self.index.is_trained:
                self.index.train(matrix)
            self.index.add(matrix)
            if hasattr(self.index, "nprobe"):
                self.index.nprobe = min(nprobe, lists)

    def candidates(self, q, count):
        count = min(count, self.size)
        if self.kind == "usearch":
            return self.index.search(q, count, threads=1).keys
        if self.kind == "hnswlib":
            return self.index.knn_query(q, k=count, num_threads=1)[0][0]
        labels = self.index.search(q[None, :], count)[1][0]
        return labels[labels >= 0]

    @property
    def payload_bytes(self):
        if self.kind == "usearch":
            return int(self.index.serialized_length)
        if self.kind == "hnswlib":
            return self.index.index_file_size()
        import faiss

        return faiss.serialize_index(self.index).nbytes
