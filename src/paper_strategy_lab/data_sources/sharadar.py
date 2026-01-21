from __future__ import annotations

import hashlib
import re
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from paper_strategy_lab.config import project_root, resolve_sharadar_dir


@dataclass(frozen=True)
class SharadarPaths:
    root: Path
    sfp_prices: Path
    tickers: Path


def _find_first(root: Path, pattern: re.Pattern[str]) -> Path:
    for p in sorted(root.glob("*.csv")):
        if pattern.match(p.name):
            return p
    raise FileNotFoundError(f"Could not find {pattern.pattern!r} under {root}")


def resolve_paths(sharadar_dir: Path | None = None) -> SharadarPaths:
    root = resolve_sharadar_dir(sharadar_dir)
    if not root.exists():
        raise FileNotFoundError(
            f"Sharadar dir not found at {root}. Set SHARADAR_DIR or symlink data/sharadar."
        )

    sfp = _find_first(root, re.compile(r"^SHARADAR_SFP_.*\.csv$"))
    tickers = _find_first(root, re.compile(r"^SHARADAR_TICKERS_.*\.csv$"))
    return SharadarPaths(root=root, sfp_prices=sfp, tickers=tickers)


def load_prices(
    tickers: list[str],
    *,
    start: str | None = None,
    end: str | None = None,
    sharadar_dir: Path | None = None,
    field: str = "closeadj",
) -> pd.DataFrame:
    """
    Load adjusted-close (or another OHLCV field) for `tickers` from Sharadar SFP.

    Returns a pandas.DataFrame indexed by date with one column per ticker.
    """
    paths = resolve_paths(sharadar_dir)
    cache_dir = project_root() / "tmp" / "_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    usecols: object = ["ticker", "date", field]
    tick_set = {t.strip().upper() for t in tickers if t.strip()}
    if not tick_set:
        return pd.DataFrame()

    key = {
        "file": str(paths.sfp_prices),
        "mtime": paths.sfp_prices.stat().st_mtime_ns,
        "field": field,
        "start": start or "",
        "end": end or "",
        "tickers": sorted(tick_set),
    }
    key_bytes = repr(key).encode("utf-8")
    digest = hashlib.sha256(key_bytes).hexdigest()[:16]
    cache_path = cache_dir / f"sfp_prices_{digest}.pkl"
    if cache_path.exists():
        with suppress(Exception):
            cached = pd.read_pickle(cache_path)
            if isinstance(cached, pd.DataFrame):
                return cached

    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(  # type: ignore[call-overload, arg-type]
        paths.sfp_prices, usecols=usecols, chunksize=2_000_000  # pyright: ignore[reportArgumentType]
    ):
        chunk["ticker"] = chunk["ticker"].astype(str).str.upper()
        chunk = chunk[chunk["ticker"].isin(tick_set)]
        if chunk.empty:
            continue
        chunk["date"] = pd.to_datetime(chunk["date"])
        if start:
            chunk = chunk[chunk["date"] >= pd.to_datetime(start)]
        if end:
            chunk = chunk[chunk["date"] <= pd.to_datetime(end)]
        if chunk.empty:
            continue
        chunks.append(chunk)

    if not chunks:
        return pd.DataFrame()

    df = pd.concat(chunks, ignore_index=True)
    df = df.dropna(subset=[field])
    df = df.pivot_table(index="date", columns="ticker", values=field, aggfunc="last").sort_index()
    df.columns.name = None
    with suppress(Exception):
        df.to_pickle(cache_path)
    return df


def load_tickers_metadata(sharadar_dir: Path | None = None) -> pd.DataFrame:
    """
    Load the Sharadar tickers metadata table.
    """
    paths = resolve_paths(sharadar_dir)
    return pd.read_csv(paths.tickers)
