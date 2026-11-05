"""Eligible bridge traversal.

Run: uv run python modules/07_hnsw/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py modules/07_hnsw/solutions/02_apply.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(graph, entry, eligible):
    seen = {entry}
    pending = [entry]
    while pending:
        for node in graph[pending.pop()]:
            if node not in seen:
                seen.add(node)
                pending.append(node)
    return sorted(seen.intersection(eligible))


def main():
    print(solve([[1], [2], []], 0, [2]))


if __name__ == "__main__":
    main()
