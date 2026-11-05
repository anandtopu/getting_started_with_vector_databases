"""Distinguish an acknowledged write from its visibility to a reader.

Run: uv run python modules/15_milvus/examples/01_from_scratch.py
Concepts: Distinguish an acknowledged write from its visibility to a reader.
Expected: a stale sale and a later retirement.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""


def visible(events, read_at, applied):
    state = {}
    for version, key, value in events:
        if version <= min(read_at, applied):
            state[key] = value
    return state


def main() -> None:
    # KEY IDEA: Distinguish an acknowledged write from its visibility to a reader.
    writes = [(1, "boot", "in stock"), (2, "boot", "retired")]
    stale = visible(writes, 2, 1)
    caught_up = visible(writes, 2, 2)
    assert stale["boot"] == "in stock" and caught_up["boot"] == "retired"
    print("reader applied through version 1", stale, "version 2", caught_up)


if __name__ == "__main__":
    main()
