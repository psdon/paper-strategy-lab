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
    sep_prices: Path
    sfp_prices: Path
    daily_metrics: Path
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

    sep = _find_first(root, re.compile(r"^SHARADAR_SEP_.*\.csv$"))
    sfp = _find_first(root, re.compile(r"^SHARADAR_SFP_.*\.csv$"))
    daily = _find_first(root, re.compile(r"^SHARADAR_DAILY_.*\.csv$"))
    tickers = _find_first(root, re.compile(r"^SHARADAR_TICKERS_.*\.csv$"))
    return SharadarPaths(
        root=root, sep_prices=sep, sfp_prices=sfp, daily_metrics=daily, tickers=tickers
    )


def _cache_path(prefix: str, key: dict) -> Path:
    cache_dir = project_root() / "tmp" / "_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(repr(key).encode("utf-8")).hexdigest()[:16]
    return cache_dir / f"{prefix}_{digest}.pkl"


def _load_prices_from_file(
    csv_path: Path,
    tickers: list[str],
    *,
    start: str | None,
    end: str | None,
    field: str,
) -> pd.DataFrame:
    usecols: object = ["ticker", "date", field]
    tick_set = {t.strip().upper() for t in tickers if t.strip()}
    if not tick_set:
        return pd.DataFrame()

    key = {
        "file": str(csv_path),
        "mtime": csv_path.stat().st_mtime_ns,
        "field": field,
        "start": start or "",
        "end": end or "",
        "tickers": sorted(tick_set),
    }
    cache_path = _cache_path("prices", key)
    if cache_path.exists():
        with suppress(Exception):
            cached = pd.read_pickle(cache_path)
            if isinstance(cached, pd.DataFrame):
                return cached

    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(  # type: ignore[call-overload, arg-type]
        csv_path, usecols=usecols, chunksize=2_000_000  # pyright: ignore[reportArgumentType]
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
    sep = _load_prices_from_file(paths.sep_prices, tickers, start=start, end=end, field=field)
    sfp = _load_prices_from_file(paths.sfp_prices, tickers, start=start, end=end, field=field)
    if sep.empty:
        return sfp
    if sfp.empty:
        return sep
    return sep.combine_first(sfp).sort_index()


def load_equity_prices(
    tickers: list[str],
    *,
    start: str | None = None,
    end: str | None = None,
    sharadar_dir: Path | None = None,
    field: str = "closeadj",
) -> pd.DataFrame:
    paths = resolve_paths(sharadar_dir)
    return _load_prices_from_file(paths.sep_prices, tickers, start=start, end=end, field=field)


def load_etf_prices(
    tickers: list[str],
    *,
    start: str | None = None,
    end: str | None = None,
    sharadar_dir: Path | None = None,
    field: str = "closeadj",
) -> pd.DataFrame:
    paths = resolve_paths(sharadar_dir)
    return _load_prices_from_file(paths.sfp_prices, tickers, start=start, end=end, field=field)


def load_daily_metrics(
    tickers: list[str],
    *,
    fields: list[str],
    start: str | None = None,
    end: str | None = None,
    sharadar_dir: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Load DAILY metrics (e.g., pe/pb/ps/marketcap) into per-field DataFrames.
    """
    paths = resolve_paths(sharadar_dir)
    tick_set = {t.strip().upper() for t in tickers if t.strip()}
    if not tick_set:
        return {f: pd.DataFrame() for f in fields}

    out: dict[str, pd.DataFrame] = {}
    for field in fields:
        usecols: object = ["ticker", "date", field]
        key = {
            "file": str(paths.daily_metrics),
            "mtime": paths.daily_metrics.stat().st_mtime_ns,
            "field": field,
            "start": start or "",
            "end": end or "",
            "tickers": sorted(tick_set),
        }
        cache_path = _cache_path(f"daily_{field}", key)
        if cache_path.exists():
            with suppress(Exception):
                cached = pd.read_pickle(cache_path)
                if isinstance(cached, pd.DataFrame):
                    out[field] = cached
                    continue

        chunks: list[pd.DataFrame] = []
        for chunk in pd.read_csv(  # type: ignore[call-overload, arg-type]
            paths.daily_metrics, usecols=usecols, chunksize=2_000_000  # pyright: ignore[reportArgumentType]
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
            out[field] = pd.DataFrame()
            continue

        df = pd.concat(chunks, ignore_index=True)
        df = df.dropna(subset=[field])
        df = df.pivot_table(
            index="date", columns="ticker", values=field, aggfunc="last"
        ).sort_index()
        df.columns.name = None
        with suppress(Exception):
            df.to_pickle(cache_path)
        out[field] = df

    return out


def load_tickers_metadata(sharadar_dir: Path | None = None) -> pd.DataFrame:
    """
    Load the Sharadar tickers metadata table.
    """
    paths = resolve_paths(sharadar_dir)
    return pd.read_csv(paths.tickers)
