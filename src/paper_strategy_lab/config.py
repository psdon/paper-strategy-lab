from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def tmp_dir(self) -> Path:
        return self.root / "tmp"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_sharadar_dir(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()

    env = os.getenv("SHARADAR_DIR")
    if env:
        return Path(env).expanduser().resolve()

    root = project_root()
    in_repo = root / "data" / "sharadar"
    if in_repo.exists():
        return in_repo.resolve()

    return (Path.home() / "Downloads" / "sharadar").resolve()

