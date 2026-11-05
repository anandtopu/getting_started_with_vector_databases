"""Compare FAISS scalar and product quantizers.

Run: uv run --extra libs python modules/08_quantization/examples/04_native_codes.py
Expected: compare the reported ranking and verify the final assertion.
CPU: seconds, included data, no Docker or model downloads.
"""

# course-extra: libs
import faiss

from common.index_lessons import unit_catalog


def main():
    _, matrix, q = unit_catalog(640)
    faiss.omp_set_num_threads(1)
    for index in [
        faiss.IndexScalarQuantizer(
            matrix.shape[1], faiss.ScalarQuantizer.QT_8bit, faiss.METRIC_INNER_PRODUCT
        ),
        faiss.IndexPQ(matrix.shape[1], 8, 3, faiss.METRIC_INNER_PRODUCT),
    ]:
        index.train(matrix)
        index.add(matrix)
        _, labels = index.search(q[None, :], 10)
        print(type(index).__name__, "bytes per code", index.code_size, "first rows", labels[0])
        assert len(set(labels[0])) == 10


if __name__ == "__main__":
    main()
