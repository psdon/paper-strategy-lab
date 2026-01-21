from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StrategyCandidate:
    page_index: int
    start_line: int
    end_line: int
    title_hint: str
    snippet: str


_TITLE_LINE_RE = re.compile(
    r"^\s*(?:strategy|trading strategy|investment strategy|rule|signal)s?\b[:\-]?\s*(.*)$",
    re.IGNORECASE,
)


def _normalize_lines(text: str) -> list[str]:
    raw_lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in raw_lines if ln]
    return lines


def extract_candidates_from_page(page_index: int, page_text: str) -> list[StrategyCandidate]:
    lines = _normalize_lines(page_text)
    candidates: list[StrategyCandidate] = []

    for i, line in enumerate(lines):
        match = _TITLE_LINE_RE.match(line)
        if not match:
            continue

        title_hint = (match.group(1) or "").strip()
        start = i
        end = min(len(lines), i + 18)
        snippet = "\n".join(lines[start:end])
        candidates.append(
            StrategyCandidate(
                page_index=page_index,
                start_line=start,
                end_line=end - 1,
                title_hint=title_hint,
                snippet=snippet,
            )
        )

    return candidates


def load_pages_jsonl(pages_jsonl_path: Path) -> Iterable[dict]:
    with pages_jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def extract_candidates_from_pages_jsonl(pages_jsonl_path: Path) -> list[StrategyCandidate]:
    all_candidates: list[StrategyCandidate] = []
    for row in load_pages_jsonl(pages_jsonl_path):
        page_index = int(row["page_index"])
        text = str(row.get("text", ""))
        all_candidates.extend(extract_candidates_from_page(page_index=page_index, page_text=text))
    return all_candidates

