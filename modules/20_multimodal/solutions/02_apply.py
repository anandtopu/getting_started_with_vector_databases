"""Apply: rank fusion endpoints.

Combine image/text rankings with the supplied image weight. Return IDs in score order. A zero-weight branch must not introduce extra IDs.
Run: uv run python modules/20_multimodal/solutions/02_apply.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(image, text, weight):
    # KEY IDEA: Combine image/text rankings with the supplied image weight.
    from common.apps.multimodal import weighted_fusion

    return [
        key
        for key, _ in weighted_fusion(
            {"image": image, "text": text}, {"image": weight, "text": 1 - weight}
        )
    ]


def main() -> None:
    print(solve(*[["a", "b"], ["b", "a"], 0]))


if __name__ == "__main__":
    main()
