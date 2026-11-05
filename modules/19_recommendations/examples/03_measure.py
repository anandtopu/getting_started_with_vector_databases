"""Choose a duplicate threshold using development families only.

Run: uv run  python modules/19_recommendations/examples/03_measure.py
Expected: development threshold and held-out precision/recall.
CPU: seconds to one minute. Needs: base, duplicate pairs and catalog vectors. No implicit downloads.
"""

import pandas as pd

from common.apps.deduplication import calibrate, pair_scores, threshold_metrics
from common.settings import data_dir
from common.teaching import catalog, evidence


def main() -> None:
    products, matrix, _, _ = catalog(10000)
    vectors = dict(zip(products.id, matrix, strict=True))
    pairs = pd.read_parquet(data_dir() / "tier4/duplicates.parquet")
    pairs = pairs[pairs.source_id.isin(vectors) & pairs.duplicate_id.isin(vectors)]
    dev, test = pairs[pairs.split == "development"], pairs[pairs.split == "test"]
    assert not set(dev.group_id) & set(test.group_id)
    chosen = calibrate(pair_scores(dev.to_dict("records"), vectors), dev.label.tolist())
    # KEY IDEA: freeze the threshold before looking at held-out outcomes.
    measured = threshold_metrics(
        pair_scores(test.to_dict("records"), vectors), test.label.tolist(), chosen["threshold"]
    )
    print({"development": chosen, "test": measured})
    evidence("duplicates", {"development": chosen, "test": measured}, tier=4)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
