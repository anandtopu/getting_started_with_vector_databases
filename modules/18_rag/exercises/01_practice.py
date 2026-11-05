"""Practice: overlapping windows.

Return word windows of at most size with overlap. Stop after the final complete tail to avoid repeated tiny suffixes.
Run: uv run python modules/18_rag/exercises/01_practice.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(words, size, overlap):
    # YOUR CODE HERE: improve the baseline to meet every criterion.
    return [words[i : i + size] for i in range(0, len(words), size)]


def main() -> None:
    print(solve(*[["a", "b", "c", "d", "e"], 3, 1]))


if __name__ == "__main__":
    main()
