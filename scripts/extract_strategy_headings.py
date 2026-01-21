from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage: python scripts/extract_strategy_headings.py <pdf> <out.json>",
            file=sys.stderr,
        )
        return 2

    pdf_path = Path(sys.argv[1]).expanduser()
    out_path = Path(sys.argv[2]).expanduser()

    heading_re = re.compile(r"^\\s*(\\d+\\.\\d+)\\s+Strategy:\\s*(.+?)\\s*$")
    dots_re = re.compile(r"\\.{2,}|\\s\\.\\s\\.")
    trail_page_re = re.compile(r"\\s\\d{1,4}\\s*$")

    reader = PdfReader(str(pdf_path))
    rows = []
    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for line in text.splitlines():
            m = heading_re.match(line)
            if not m:
                continue
            title = m.group(2).strip()
            if dots_re.search(title) and trail_page_re.search(title):
                continue
            rows.append({"section": m.group(1), "title": title, "page_index": page_index})

    # de-dup preserve order
    seen = set()
    dedup = []
    for r in rows:
        key = (r["section"], r["title"])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(dedup, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(dedup)} headings -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
