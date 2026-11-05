"""Apply the bonus concept to Marlowe inventory and evaluation.
Run: uv run python modules/bonus/B4_whats_new/use_case/marlowe.py
Expected: protected invariants and an explained result. CPU: seconds.
Needs: included data; B1 additionally requires the prepared Node toolchain.
"""

import numpy as np
from threadpoolctl import threadpool_limits

from common.teaching import catalog
from tinyvec.rabitq import RaBitQ


def main() -> None:
    products, vectors, query, _ = catalog(500)
    with threadpool_limits(limits=1):
        index = RaBitQ(vectors)
        candidates = index.candidates(query, 100)
    scores = np.sum((vectors[candidates] - query) ** 2, axis=1)
    best = candidates[np.argsort(scores)[:5]]
    print(products.iloc[best][["id", "title"]].to_dict(orient="records"))
    print("Full vectors remain for rescoring; packed codes are not total memory.")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
