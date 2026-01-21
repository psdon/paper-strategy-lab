from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class PriceSeries:
    ticker: str
    prices: pd.Series


def get_adjusted_close(
    ticker: str, start: str | None = None, end: str | None = None
) -> PriceSeries:
    import yfinance as yf

    df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
    if df is None or df.empty:
        raise ValueError(f"No data returned for ticker={ticker!r}")
    if "Adj Close" in df.columns:
        col = df["Adj Close"]
    elif "Close" in df.columns:
        col = df["Close"]
    else:
        col = df.iloc[:, 0]

    prices = col.iloc[:, 0] if isinstance(col, pd.DataFrame) else col
    return PriceSeries(ticker=ticker, prices=prices)
