from __future__ import annotations

from pathlib import Path

import yaml

from .spec import StrategySpec


def load_strategy_specs(yaml_path: Path) -> list[StrategySpec]:
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    items = data.get("strategies", [])
    specs: list[StrategySpec] = []
    for item in items:
        paper = dict(item.get("paper") or {})
        universe_obj = item.get("universe") or {}
        universe_type = None
        universe_config = {}
        universe: list[str] = []

        if isinstance(universe_obj, dict):
            universe_type = universe_obj.get("type")
            universe_config = dict(universe_obj.get("config") or {})
            universe = list(universe_obj.get("tickers") or [])
        else:
            universe = list(universe_obj or [])

        params = dict(item.get("params") or {})
        kind = str(item.get("kind") or params.get("kind") or "").strip()
        if "kind" in params:
            params.pop("kind", None)

        specs.append(
            StrategySpec(
                id=str(item["id"]),
                name=str(item["name"]),
                description=item.get("description"),
                paper_section=paper.get("section"),
                paper_title=paper.get("title"),
                kind=kind,
                universe=[str(t).strip().upper() for t in universe if str(t).strip()],
                universe_type=str(universe_type).strip() if universe_type else None,
                universe_config=universe_config,
                params=params,
            )
        )
    return specs
