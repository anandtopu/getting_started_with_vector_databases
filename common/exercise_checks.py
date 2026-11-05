"""The same acceptance cases run against a learner-selected file or reference solution."""

import importlib.util
import json
from pathlib import Path

import numpy as np

from common.stores.types import Record


def load(path: Path):
    spec = importlib.util.spec_from_file_location("selected_exercise", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load exercise: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def smoke(module) -> None:
    module.main()


def rejects(call) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Invalid input must raise ValueError")


def check(module: str, name: str, solve, temporary: Path) -> None:
    key = (module[:2], name[:2])
    if module.startswith("B"):
        cases = json.loads(
            Path(__file__).with_name("bonus_exercises.json").read_text(encoding="utf8")
        )
        for args, expected in cases["-".join(key)]:
            assert solve(*args) == expected, f"Input {args!r} should return {expected!r}"
        return
    if 5 <= int(module[:2]) <= 23:
        tier = (
            2
            if int(module[:2]) <= 10
            else 3
            if int(module[:2]) <= 16
            else 4
            if int(module[:2]) <= 20
            else 5
        )
        cases = json.loads(Path(__file__).with_name(f"tier{tier}_exercises.json").read_text())
        for args, expected in cases["-".join(key)]:
            actual = solve(*args)
            assert actual == expected, f"Input {args!r} should return {expected!r}, got {actual!r}"
        return
    if key == ("00", "01"):
        rows = [{"id": "a", "text": "Warm MUG"}, {"id": "b", "text": "chair"}]
        assert solve(rows, "mug") == ["a"], "Match without case sensitivity"
        assert solve(rows, "boots") == []
    elif key == ("00", "02"):
        assert solve([{"id": "a"}, {"id": "a"}, {"id": "b"}]) == {"rows": 3, "unique_ids": 2}, (
            "Count unique IDs, not rows"
        )
        assert solve([]) == {"rows": 0, "unique_ids": 0}
    elif key == ("00", "03"):
        assert solve(1000, False, False) == "library", "A fixed local experiment needs no server"
        assert solve(1000, True, False) == "embedded"
        assert solve(1000, True, True) == "server"
    elif key == ("01", "01"):
        assert np.isclose(solve([3, 4], [6, 8]), 1), "Divide the dot product by both lengths"
        assert np.isclose(solve([1, 0], [0, 1]), 0)
        rejects(lambda: solve([0, 0], [1, 0]))
    elif key == ("01", "02"):
        assert solve([[0, 1], [1, 0], [1, 0]], [1, 0], ["z", "b", "a"], 2) == ["a", "b"], (
            "Rank by similarity, then ID"
        )
        assert solve([[1, 0]], [1, 0], ["a"], 5) == ["a"]
    elif key == ("01", "03"):
        np.testing.assert_allclose(solve([[3, 4], [0, 2]]), [[0.6, 0.8], [0, 1]])
        rejects(lambda: solve([[0, 0]]))
    elif key == ("02", "01"):
        base = {"revision": "one", "dimensions": 3, "normalized": True}
        changed = {**base, "revision": "two"}
        assert solve("mug", base, "query") != solve("mug", changed, "query"), (
            "A model revision belongs in the cache key"
        )
        assert solve("mug", base, "query") != solve("mug", base, "document")
        assert solve("mug", base, "query") == solve(
            "mug", dict(reversed(list(base.items()))), "query"
        )
    elif key == ("02", "02"):
        assert solve(list("abcde"), 2) == [["a", "b"], ["c", "d"], ["e"]], (
            "Preserve order and cap each batch"
        )
        assert solve([], 2) == []
        rejects(lambda: solve(["a"], 0))
    elif key == ("02", "03"):
        assert solve({"dimensions": 384}, {"dimensions": 384})
        assert not solve({"dimensions": 384}, {"dimensions": 384, "revision": "another"}), (
            "Same dimension does not establish the same space"
        )
        assert not solve({"dimensions": 384}, {"dimensions": 384, "query_prefix": "query: "})
    elif key == ("03", "01"):
        before = {"mug": {"price": 30}}
        metadata = {"price": 20}
        result = solve(before, "mug", metadata)
        assert result == {"mug": {"price": 20}}, "Upsert must replace an existing record"
        metadata["price"] = 99
        assert result["mug"]["price"] == 20 and before["mug"]["price"] == 30
    elif key == ("03", "02"):
        rows = [
            {"id": "a", "score": 1.0, "stock": 0},
            {"id": "c", "score": 0.9, "stock": 2},
            {"id": "b", "score": 0.9, "stock": 1},
        ]
        assert solve(rows, 1) == ["b"], "Filter before selecting k and break ties by ID"
        assert solve([], 3) == []
    elif key == ("03", "03"):
        records = [Record("mug", np.array([1.0, 0.2]), {"price": 20}, "warmer")]
        restored = solve(records, temporary / "snapshot")
        assert (temporary / "snapshot/snapshot.json").exists(), (
            "Use a complete TinyVec snapshot, not just IDs"
        )
        assert restored[0].metadata == {"price": 20} and restored[0].text == "warmer"
        np.testing.assert_allclose(restored[0].vector, records[0].vector)
        from tinyvec import TinyVec

        again = TinyVec.load(temporary / "snapshot")
        try:
            assert again.records()[0].id == "mug"
        finally:
            again.close()
    elif key == ("04", "01"):
        assert solve(["mug", "mug"], {"mug": 3}, 2) == 0.5, (
            "Duplicate IDs cannot earn repeated credit"
        )
        assert solve([], {}, 3) == 0
        rejects(lambda: solve([], {}, 0))
    elif key == ("04", "02"):
        assert np.isclose(solve([1.0, 2.0, 3.0, 4.0, 100.0], 95), 80.8), (
            "Interpolate ordered observations at (n-1)*p"
        )
        assert solve([7.0], 99) == 7
        rejects(lambda: solve([], 50))
    elif key == ("04", "03"):
        assert solve(2, 1.0, [10.0, 10.0]) == 2.0, (
            "Use wall time, including gaps, not summed request latency"
        )
        assert solve(0, 1.0, []) == 0
        rejects(lambda: solve(1, 0, [1.0]))
    else:
        raise ValueError(f"Unknown exercise: {module}/{name}")
