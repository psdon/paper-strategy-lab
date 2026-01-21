from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StrategySpec:
    id: str
    name: str
    description: str | None
    paper_section: str | None
    paper_title: str | None
    kind: str
    universe: list[str]
    params: dict[str, Any]
