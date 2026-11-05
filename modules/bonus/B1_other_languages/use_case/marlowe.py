"""Apply the bonus concept to Marlowe inventory and evaluation.
Run: uv run python modules/bonus/B1_other_languages/use_case/marlowe.py
Expected: protected invariants and an explained result. CPU: seconds.
Needs: prepared Node toolchain, exported MiniLM fixture and local Qdrant profile.
"""
# course-profile: qdrant

from common.bonus import typescript
from common.research import record


def main() -> None:
    # KEY IDEA: the seller workflow preserves business IDs through native CRUD operations.
    result = typescript("qdrant")
    assert result["scoped"] and result["replacement"] and result["deletion"]
    print("Seller inventory search returned", result["ids"])
    print("Replacing a listing did not duplicate it; withdrawing it removed it from retrieval.")
    print(
        record(
            "seller-typescript",
            result,
            "python modules/bonus/B1_other_languages/use_case/marlowe.py",
        )
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
