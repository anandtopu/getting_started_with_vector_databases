"""Render seven editable Markdown sheets as verified one-page PDFs.

Run: python scripts/build_cheatsheets.py
CPU: seconds. Authoring-only dependencies: reportlab and pypdf; no network or models.
"""

from html import escape
from pathlib import Path


def main() -> None:
    from pypdf import PdfReader
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    root = Path(__file__).resolve().parents[1]
    output = root / "output/pdf"
    output.mkdir(parents=True, exist_ok=True)
    styles = {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#15384a"),
            spaceAfter=12,
        ),
        "heading": ParagraphStyle(
            "heading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#15616d"),
            spaceBefore=9,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#172b36"),
            spaceAfter=4,
        ),
    }

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#b5c7cf"))
        canvas.line(42, 38, 570, 38)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#536773"))
        canvas.drawString(42, 25, "MARLOWE MARKET / VECTOR DATABASES / 1.0 / 2026-11-05")
        canvas.drawRightString(570, 25, str(doc.page))
        canvas.restoreState()

    for path in sorted((root / "cheatsheets").glob("*.md")):
        if path.name == "README.md":
            continue
        story = []
        for block in path.read_text(encoding="utf8").strip().split("\n\n"):
            kind = (
                "heading"
                if block.startswith("## ")
                else "title"
                if block.startswith("# ")
                else "body"
            )
            value = block.removeprefix("## ").removeprefix("# ")
            story.append(Paragraph(escape(value).replace("\n", "<br/>"), styles[kind]))
        story.append(Spacer(1, 4))
        target = output / (path.stem + ".pdf")
        SimpleDocTemplate(
            str(target),
            pagesize=letter,
            leftMargin=42,
            rightMargin=42,
            topMargin=38,
            bottomMargin=48,
            title=path.stem,
            author="Marlowe Market course",
        ).build(story, onFirstPage=footer, onLaterPages=footer)
        reader = PdfReader(target)
        if len(reader.pages) != 1:
            raise ValueError(f"{path.name} must fit one page; found {len(reader.pages)}")
        if len(reader.pages[0].extract_text()) < 500:
            raise ValueError(f"Missing extracted content: {path.name}")
        print(f"PASS {target.name}: one page, extractable text")


if __name__ == "__main__":
    main()
