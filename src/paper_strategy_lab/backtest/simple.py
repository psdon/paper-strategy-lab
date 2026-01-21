from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    equity_curve: pd.Series
    daily_returns: pd.Series


def run_long_only_backtest(prices: pd.Series, signal: pd.Series) -> BacktestResult:
    px = pd.Series(prices).astype(float).dropna()
    sig = pd.Series(signal).reindex(px.index).fillna(0.0).astype(float)
    sig = sig.clip(lower=0.0, upper=1.0)

    rets: pd.Series = px.pct_change(fill_method=None).fillna(0.0)
    strat_rets: pd.Series = rets * sig.shift(1).fillna(0.0)
    equity: pd.Series = pd.Series(1.0 + strat_rets).cumprod()
    return BacktestResult(equity_curve=equity, daily_returns=strat_rets)
