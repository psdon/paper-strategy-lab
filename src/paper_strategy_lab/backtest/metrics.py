from __future__ import annotations

import numpy as np
import pandas as pd


def max_drawdown(equity_curve: pd.Series) -> float:
    s = pd.Series(equity_curve).astype(float)
    running_max = s.cummax()
    drawdown = s / running_max - 1.0
    return float(np.nanmin(drawdown))


def annualized_return(daily_returns: pd.Series, periods_per_year: int = 252) -> float:
    r = pd.Series(daily_returns).astype(float).dropna()
    if r.empty:
        return 0.0
    growth = float(np.prod(1.0 + r))
    years = len(r) / periods_per_year
    if years <= 0:
        return 0.0
    return growth ** (1.0 / years) - 1.0


def annualized_volatility(daily_returns: pd.Series, periods_per_year: int = 252) -> float:
    r = pd.Series(daily_returns).astype(float).dropna()
    if r.empty:
        return 0.0
    return float(np.std(r, ddof=1) * (periods_per_year**0.5))


def sharpe_ratio(
    daily_returns: pd.Series,
    risk_free_rate_annual: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    r = pd.Series(daily_returns).astype(float).dropna()
    if r.empty:
        return 0.0
    rf_daily = (1.0 + risk_free_rate_annual) ** (1.0 / periods_per_year) - 1.0
    excess = r - rf_daily
    vol = float(np.std(excess, ddof=1))
    if vol == 0:
        return 0.0
    return float((np.mean(excess) / vol) * (periods_per_year**0.5))
