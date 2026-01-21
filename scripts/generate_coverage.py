from __future__ import annotations

import json
from pathlib import Path

import yaml


def load_specs(spec_path: Path) -> dict[str, dict]:
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    specs: dict[str, list[dict]] = {}
    for s in data.get("strategies", []):
        paper = s.get("paper") or {}
        section = paper.get("section")
        if section:
            specs.setdefault(str(section), []).append(s)
    return specs


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    headings_path = root / "docs" / "ssrn-3247865.strategy_headings.json"
    spec_path = root / "strategies" / "ssrn-3247865.yaml"
    out_path = root / "docs" / "COVERAGE.md"

    headings = json.loads(headings_path.read_text(encoding="utf-8"))
    specs_by_section = load_specs(spec_path)

    lines = []
    lines.append("# Coverage (ssrn-3247865)")
    lines.append("")
    lines.append("This table tracks which paper strategies are implemented in code/specs.")
    lines.append("")
    lines.append(
        "- `implemented`: runnable via `paper-strategy-lab leaderboard "
        "strategies/ssrn-3247865.yaml`"
    )
    lines.append("- `planned`: mapped but not yet implemented")
    lines.append(
        "- `blocked`: needs data not currently wired (options chains, futures curves, "
        "OTC quotes, etc.)"
    )
    lines.append("")
    lines.append("| Paper Section | Title | Status | Strategy ID | Notes |")
    lines.append("|---|---|---|---|---|")

    def classify_default(section: str) -> tuple[str, str]:
        """
        Heuristic only. Prefer explicit status once a strategy is implemented/mapped.
        """
        major = section.split(".", 1)[0]
        if major in {"2", "7"}:
            return "blocked", "Options strategy; needs options chain data."
        if major in {"5", "6"}:
            return "blocked", "Rates strategy; needs yield curves / bond data."
        if major in {"8", "9"}:
            return "blocked", "Needs futures/FX + carry inputs not wired yet."
        if major in {"10", "11", "12", "13", "14", "15", "22"}:
            return "blocked", "Specialized/institutional data not wired yet."
        return "planned", "Not yet implemented."

    for h in headings:
        section = h["section"]
        title = h["title"]
        specs = specs_by_section.get(section) or []
        if not specs:
            status, notes = classify_default(section)
            sid = ""
        else:
            status = "implemented"
            sid = ", ".join([str(s.get("id", "")) for s in specs if s.get("id")])
            kinds = sorted({str(s.get("kind", "")) for s in specs if s.get("kind")})
            notes = f"kinds={','.join(kinds)}"
        lines.append(f"| {section} | {title} | {status} | {sid} | {notes} |")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
