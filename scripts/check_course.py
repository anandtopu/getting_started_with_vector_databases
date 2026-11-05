"""Audit the delivered modules, runnable-file metadata, and cleared notebooks.

Run: uv run python scripts/check_course.py
No network, model, or Docker. Completeness checks supplement, not replace, execution.
"""

import ast
import json

from common.settings import ROOT

SECTIONS = [
    "Prerequisites",
    "Learning objectives",
    "The big idea",
    "How it works",
    "Build it yourself",
    "Now in a real database",
    "Walkthrough",
    "Measure it",
    "When to use it, and when not to",
    "Real-world use case",
    "Common mistakes",
    "Exercises",
    "Quiz",
    "Key takeaways",
    "Clean up",
    "Go deeper",
    "Next: Module",
]


def main() -> None:
    modules = sorted((ROOT / "modules").glob("[0-9][0-9]_*"))
    assert [int(module.name[:2]) for module in modules] == list(range(24)), "Expected modules 00–23"
    bonus = sorted((ROOT / "modules/bonus").glob("B[1-4]_*"))
    assert len(bonus) == 4, "Expected bonus modules B1–B4"
    modules += bonus
    for module in modules:
        text = (module / "README.md").read_text(encoding="utf-8")
        for section in SECTIONS:
            assert f"## {section}" in text, f"{module.name}: missing {section}"
        assert "```mermaid" in text and text.count("<details>") >= 5
        for folder, count in [
            ("examples", 3),
            ("use_case", 1),
            ("exercises", 3),
            ("solutions", 3),
            ("tests", 1),
        ]:
            paths = list((module / folder).glob("*.py"))
            assert len(paths) >= count, f"{module.name}: missing {folder} files"
            if folder != "tests":
                for path in paths:
                    source = path.read_text(encoding="utf-8")
                    doc = ast.get_docstring(ast.parse(source)) or ""
                    assert "Run:" in doc and "CPU:" in doc, f"Missing runnable metadata: {path}"
                    assert "def main()" in source and "__main__" in source
                    if folder == "exercises":
                        assert "# YOUR CODE HERE" in source
        assert (module / "results/README.md").exists()
        notebook = json.loads((module / "notebook.ipynb").read_text(encoding="utf-8"))
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                assert cell["execution_count"] is None and not cell["outputs"], (
                    "Clear notebook outputs before committing"
                )
        print(f"PASS {module.name}: structure, quiz, metadata, cleared notebook")


if __name__ == "__main__":
    main()
