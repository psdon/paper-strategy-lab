from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PdfPageText:
    page_index: int
    text: str


def extract_pages(pdf_path: Path) -> list[PdfPageText]:
    reader = PdfReader(str(pdf_path))
    pages: list[PdfPageText] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append(PdfPageText(page_index=i, text=text))
    return pages


def iter_pages(pdf_path: Path) -> Iterable[PdfPageText]:
    yield from extract_pages(pdf_path)
