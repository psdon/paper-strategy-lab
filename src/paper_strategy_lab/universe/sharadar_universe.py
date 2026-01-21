from __future__ import annotations

import hashlib
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from paper_strategy_lab.config import project_root
from paper_strategy_lab.data_sources.sharadar import resolve_paths


@dataclass(frozen=True)
class EquityUniverseConfig:
    start: str | None
    end: str | None
    exchanges: list[str]
    category: str
    isdelisted: str
    currency: str
    max_tickers: int
    min_price: float
    liquidity_lookback_days: int


def _cache_json_path(prefix: str, key: dict) -> Path:
    cache_dir = project_root() / "tmp" / "_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(repr(key).encode("utf-8")).hexdigest()[:16]
    return cache_dir / f"{prefix}_{digest}.json"


def _avg_dollar_volume_sep(
    sep_csv: Path, tickers: set[str], *, start: str | None, end: str | None
) -> dict[str, float]:
    usecols: object = ["ticker", "date", "closeadj", "volume"]
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}

    for chunk in pd.read_csv(  # type: ignore[call-overload, arg-type]
        sep_csv, usecols=usecols, chunksize=2_000_000  # pyright: ignore[reportArgumentType]
    ):
        chunk["ticker"] = chunk["ticker"].astype(str).str.upper()
        chunk = chunk[chunk["ticker"].isin(tickers)]
        if chunk.empty:
            continue

        chunk["date"] = pd.to_datetime(chunk["date"])
        if start:
            chunk = chunk[chunk["date"] >= pd.to_datetime(start)]
        if end:
            chunk = chunk[chunk["date"] <= pd.to_datetime(end)]
        if chunk.empty:
            continue

        chunk = chunk.dropna(subset=["closeadj", "volume"])
        if chunk.empty:
            continue

        dv = chunk["closeadj"].astype(float) * chunk["volume"].astype(float)
        chunk = chunk.assign(dv=dv)
        grouped = chunk.groupby("ticker")["dv"].agg(["sum", "count"])
        for t, row in grouped.iterrows():
            t = str(t)
            sums[t] = sums.get(t, 0.0) + float(row["sum"])
            counts[t] = counts.get(t, 0) + int(row["count"])

    out = {}
    for t, s in sums.items():
        c = counts.get(t, 0)
        if c > 0:
            out[t] = s / c
    return out


def build_us_equities_liquid(
    *,
    sharadar_dir: Path | None = None,
    start: str | None = None,
    end: str | None = None,
    exchanges: list[str] | None = None,
    category: str = "Domestic Common Stock",
    isdelisted: str = "N",
    currency: str = "USD",
    max_tickers: int = 500,
    min_price: float = 5.0,
    liquidity_lookback_days: int = 63,
) -> list[str]:
    """
    Build a liquid US equities universe based on Sharadar TICKERS metadata and SEP average dollar
    volume over the requested time window.
    """
    if exchanges is None:
        exchanges = ["NYSE", "NASDAQ"]

    paths = resolve_paths(sharadar_dir)
    key = {
        "t": "us_equities_liquid",
        "root": str(paths.root),
        "sep": str(paths.sep_prices),
        "sep_mtime": paths.sep_prices.stat().st_mtime_ns,
        "tickers_mtime": paths.tickers.stat().st_mtime_ns,
        "start": start or "",
        "end": end or "",
        "exchanges": exchanges,
        "category": category,
        "isdelisted": isdelisted,
        "currency": currency,
        "max_tickers": max_tickers,
        "min_price": min_price,
        "liq_days": liquidity_lookback_days,
    }
    cache_path = _cache_json_path("universe", key)
    if cache_path.exists():
        with suppress(Exception):
            return [t for t in cache_path.read_text(encoding="utf-8").splitlines() if t.strip()]

    meta: pd.DataFrame = pd.read_csv(paths.tickers)
    meta["ticker"] = meta["ticker"].astype(str).str.upper()
    meta = meta.loc[(meta["currency"] == currency) & (meta["isdelisted"] == isdelisted)].copy()
    meta = meta.loc[meta["category"] == category].copy()
    meta = meta.loc[meta["exchange"].isin(exchanges)].copy()

    candidates = set(meta["ticker"].dropna().astype(str).str.upper().tolist())
    if not candidates:
        return []

    # Liquidity ranking via average dollar volume (static over full window for now).
    adv = _avg_dollar_volume_sep(paths.sep_prices, candidates, start=start, end=end)
    ranked = sorted(adv.items(), key=lambda kv: kv[1], reverse=True)
    tickers = [t for t, _ in ranked[: max_tickers * 3]]
    if not tickers:
        return []

    # Apply a simple price filter using last available closeadj in the window.
    # This avoids penny stocks without building a full dynamic filter.
    last_prices = {}
    usecols: object = ["ticker", "date", "closeadj"]
    tick_set = set(tickers)
    for chunk in pd.read_csv(  # type: ignore[call-overload, arg-type]
        paths.sep_prices, usecols=usecols, chunksize=2_000_000  # pyright: ignore[reportArgumentType]
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
        chunk = chunk.dropna(subset=["closeadj"])
        if chunk.empty:
            continue
        # keep last seen by date
        chunk = chunk.sort_values("date")
        for t, sub in chunk.groupby("ticker"):
            last_prices[str(t)] = float(sub["closeadj"].iloc[-1])

    filtered = [t for t in tickers if last_prices.get(t, 0.0) >= min_price]
    final = filtered[:max_tickers]

    cache_path.write_text("\n".join(final) + "\n", encoding="utf-8")
    return final
