"""Stretch: separate citation validity and support.

Return invalid IDs, whether every claim has a supporting source according to supplied review labels, and whether the answer lacks citations. Valid IDs cannot substitute for claim support.
Run: uv run python modules/18_rag/solutions/03_stretch.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(citations, allowed, claim_supported):
    # KEY IDEA: Return invalid IDs, whether every claim has a supporting source according to supplied review labels, and whether the answer lacks citations.
    return {
        "invalid": sorted(set(citations) - set(allowed)),
        "supported": bool(claim_supported) and all(claim_supported),
        "missing": not bool(citations),
    }


def main() -> None:
    print(solve(*[["p1"], ["p1"], [False]]))


if __name__ == "__main__":
    main()
