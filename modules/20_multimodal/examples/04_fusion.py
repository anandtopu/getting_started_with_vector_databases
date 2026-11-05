"""Inspect weighted rank fusion without adding incompatible raw scores.

Run: uv run  python modules/20_multimodal/examples/04_fusion.py
Expected: changing weights changes which item ranks first.
CPU: seconds to one minute. Needs: base, NumPy. No implicit downloads.
"""

from common.apps.multimodal import weighted_fusion


def main() -> None:
    ranks = {"image": ["red-mug", "blue-mug"], "text": ["blue-mug", "red-mug"]}
    for weight in [0.0, 0.5, 1.0]:
        # KEY IDEA: ranks have a common interpretation; raw model scores need calibration.
        print(weight, weighted_fusion(ranks, {"image": weight, "text": 1 - weight}))
    assert weighted_fusion(ranks, {"image": 1, "text": 0})[0][0] == "red-mug"


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
