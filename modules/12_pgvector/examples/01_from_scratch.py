"""Join eligible sellers to independently ranked vector neighbors.

Run: uv run python modules/12_pgvector/examples/01_from_scratch.py
Concepts: Join eligible sellers to independently ranked vector neighbors.
Expected: eligible seller and product.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

import numpy as np

from common.teaching import catalog


def main() -> None:
    # KEY IDEA: Join eligible sellers to independently ranked vector neighbors.
    rows, matrix, q, _ = catalog(160)
    allowed = {r.seller_id for r in rows.itertuples() if r.region == "north"}
    eligible = [
        i for i, r in enumerate(rows.itertuples()) if r.seller_id in allowed and r.price < 35
    ]
    scores = matrix[eligible] @ q / (np.linalg.norm(matrix[eligible], axis=1) * np.linalg.norm(q))
    winner = eligible[int(np.argmax(scores))]
    print(rows.iloc[winner][["id", "seller_id", "price"]].to_dict())
    assert rows.iloc[winner].seller_id in allowed


if __name__ == "__main__":
    main()
