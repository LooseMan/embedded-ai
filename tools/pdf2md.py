# 以下はcodexで生成されたコードです。python3.12で動作確認を実施しました。

"""Convert PDFs to Markdown while preserving headings, lists, and tables."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path
from typing import Iterable

import pdfplumber


HEADING_FONT_SIZES = {18, 21}
TOP_LEVEL_HEADING_SIZE = 21
PDF_BULLET_MAX_X = 50
PDF_BULLET_MAX_SIZE = 6
PDF_BULLET_Y_TOLERANCE = 3


def normalize_text(text: str) -> str:
    """Normalize compatibility characters for comparisons only."""
    return unicodedata.normalize("NFKC", text).strip()


def markdown_table(table: list[list[str | None]]) -> str:
    """Render a pdfplumber table as a GitHub-Flavored Markdown table."""
    rows = [[(cell or "").strip() for cell in row] for row in table]
    rows = [row for row in rows if any(row)]
    if len(rows) < 2:
        return ""

    column_count = max(len(row) for row in rows)
    rows = [row + [""] * (column_count - len(row)) for row in rows]

    def render_row(row: list[str]) -> str:
        return "| " + " | ".join(row) + " |"

    header, *body = rows
    separator = ["---"] * column_count
    return "\n".join(
        [render_row(header), render_row(separator)]
        + [render_row(row) for row in body]
    )


def heading_levels(words: list[dict]) -> dict[str, int]:
    """Return normalized heading text mapped to Markdown heading levels."""
    return {
        normalize_text(word["text"]): (
            2 if round(word["size"]) >= TOP_LEVEL_HEADING_SIZE else 3
        )
        for word in words
        if round(word["size"]) in HEADING_FONT_SIZES
    }


def vector_bullet_lines(page, words: list[dict]) -> set[str]:
    """Find text lines preceded by small filled vector bullets.

    Some PDFs display ``・`` as a vector circle rather than a text glyph. Such
    bullets are absent from ``extract_text()`` but remain available as curves.
    """
    lines: set[str] = set()

    for curve in page.curves:
        is_bullet = (
            curve.get("fill")
            and curve.get("x1", 0) <= PDF_BULLET_MAX_X
            and curve.get("width", 0) <= PDF_BULLET_MAX_SIZE
            and curve.get("height", 0) <= PDF_BULLET_MAX_SIZE
        )
        if not is_bullet:
            continue

        bullet_center = (curve["top"] + curve["bottom"]) / 2
        line_words = [
            word
            for word in words
            if word["x0"] > curve["x1"]
            and abs((word["top"] + word["bottom"]) / 2 - bullet_center)
            <= PDF_BULLET_Y_TOLERANCE
        ]
        line_words.sort(key=lambda word: word["x0"])
        if line_words:
            lines.add(normalize_text(" ".join(word["text"] for word in line_words)))

    return lines


def markdownize_lines(
    lines: Iterable[str],
    headings: dict[str, int],
    bullet_lines: set[str],
) -> list[str]:
    """Restore headings and list markers without changing list semantics."""
    source_lines = list(lines)
    result: list[str] = []
    index = 0

    while index < len(source_lines):
        line = source_lines[index]
        stripped = line.strip()
        normalized = normalize_text(stripped)

        if normalized in headings:
            result.append(f"{'#' * headings[normalized]} {stripped}")
            index += 1
            continue

        if normalized in bullet_lines:
            result.append(f"- {stripped}")
            index += 1
            continue

        # Keep numbered lists numbered because their order may be meaningful.
        if re.fullmatch(r"\d+\.", stripped) and index + 1 < len(source_lines):
            next_line = source_lines[index + 1].strip()
            if next_line:
                result.append(f"{stripped} {next_line}")
                index += 2
                continue

        if re.match(r"^\d+\.\s+.+$", stripped):
            result.append(stripped)
            index += 1
            continue

        text_bullet = re.match(r"^[・●]\s*(.+)$", stripped)
        if text_bullet:
            result.append(f"- {text_bullet.group(1)}")
            index += 1
            continue

        result.append(line)
        index += 1

    return result


def split_table_rows(table: list[list[str | None]]) -> list[list[str | None]]:
    """Remove a trailing paragraph accidentally captured as a table row."""
    body = list(table)
    while body:
        non_empty = [cell for cell in body[-1] if cell and cell.strip()]
        if len(non_empty) == 1 and "\n" in non_empty[0]:
            body.pop()
        else:
            break
    return body


def extract_page_markdown(page) -> str:
    """Extract one page, replacing detected tables with Markdown tables."""
    plain_lines = (page.extract_text() or "").splitlines()
    words = page.extract_words(extra_attrs=["size"])
    headings = heading_levels(words)
    bullet_lines = vector_bullet_lines(page, words)
    tables = page.extract_tables()

    if not tables:
        lines = markdownize_lines(plain_lines, headings, bullet_lines)
        return "\n".join(lines).strip()

    table_outputs: list[tuple[str, str]] = []
    table_cells: set[str] = set()
    table_rows: set[str] = set()

    for table in tables:
        if not table:
            continue

        first_row = [cell.strip() for cell in table[0] if cell and cell.strip()]
        body = table[1:] if len(first_row) == 1 else table
        body = split_table_rows(body)
        rendered = markdown_table(body)
        if not rendered:
            continue

        title = first_row[0] if len(first_row) == 1 else ""
        table_outputs.append((title, rendered))
        for row in body:
            values = [cell.strip() for cell in row if cell and cell.strip()]
            table_cells.update(values)
            if values:
                table_rows.add(" ".join(values))

    filtered_lines = [
        line
        for line in plain_lines
        if line.strip() not in table_cells
        and " ".join(line.split()) not in table_rows
    ]

    for title, rendered in table_outputs:
        if title and title in filtered_lines:
            insert_at = filtered_lines.index(title) + 1
            filtered_lines[insert_at:insert_at] = ["", rendered]
        else:
            filtered_lines.extend(["", rendered])

    lines = markdownize_lines(filtered_lines, headings, bullet_lines)
    return "\n".join(lines).strip()


def convert_pdf(path: Path) -> str:
    """Convert a PDF file to Markdown."""
    with pdfplumber.open(path) as pdf:
        pages = [extract_page_markdown(page) for page in pdf.pages]
    return "\n\n".join(page for page in pages if page)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PDF to Markdown while preserving document structure."
    )
    parser.add_argument("input_pdf", type=Path, help="Path to the input PDF file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path: Path = args.input_pdf

    if not input_path.is_file():
        raise SystemExit(f"入力ファイルが見つかりません: {input_path}")
    if input_path.suffix.lower() != ".pdf":
        raise SystemExit(f"PDFファイルを指定してください: {input_path}")

    print(convert_pdf(input_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
