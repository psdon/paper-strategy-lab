from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PortfolioBacktestResult:
    equity_curve: pd.Series
    daily_returns: pd.Series
    turnover: pd.Series


def run_portfolio_backtest(
    prices: pd.DataFrame,
    weights: pd.DataFrame,
    *,
    fee_bps: float = 0.0,
    slippage_bps: float = 0.0,
    lag_days: int = 1,
) -> PortfolioBacktestResult:
    """
    Vectorized daily backtest for a long-only (or long/short) weights panel.

    - `prices`: DataFrame indexed by date with columns as tickers
    - `weights`: DataFrame indexed by date, same columns; weights should sum to <= 1
    - execution: apply weights with `lag_days` delay (default 1)
    - costs: proportional to daily turnover (sum abs(delta weights))
    """
    px = prices.copy()
    w = weights.copy()

    if px.empty:
        return PortfolioBacktestResult(
            equity_curve=pd.Series(dtype=float),
            daily_returns=pd.Series(dtype=float),
            turnover=pd.Series(dtype=float),
        )

    px = px.sort_index()
    w = w.sort_index().reindex(px.index).fillna(0.0)
    w = w.reindex(columns=px.columns).fillna(0.0)

    rets = (
        px.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    )

    w_exec = w.shift(lag_days).fillna(0.0)

    delta = w_exec.diff().abs().sum(axis=1).fillna(0.0)
    cost_rate = (fee_bps + slippage_bps) / 10_000.0
    costs = delta * cost_rate

    port_rets = (w_exec * rets).sum(axis=1) - costs
    equity = (1.0 + port_rets).cumprod()

    return PortfolioBacktestResult(equity_curve=equity, daily_returns=port_rets, turnover=delta)
