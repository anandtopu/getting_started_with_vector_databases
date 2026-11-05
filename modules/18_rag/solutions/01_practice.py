"""Practice: overlapping windows.

Return word windows of at most size with overlap. Stop after the final complete tail to avoid repeated tiny suffixes.
Run: uv run python modules/18_rag/solutions/01_practice.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(words, size, overlap):
    # KEY IDEA: Return word windows of at most size with overlap.
    if size < 1 or not 0 <= overlap < size:
        raise ValueError("Use size > overlap >= 0")
    output = []
    for start in range(0, len(words), size - overlap):
        output.append(words[start : start + size])
        if start + size >= len(words):
            break
    return output


def main() -> None:
    print(solve(*[["a", "b", "c", "d", "e"], 3, 1]))


if __name__ == "__main__":
    main()
