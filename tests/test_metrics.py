from __future__ import annotations

import pandas as pd

from paper_strategy_lab.backtest.metrics import (
    annualized_return,
    annualized_volatility,
    calmar_ratio,
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
)


def test_metrics_empty_inputs_are_zero() -> None:
    s = pd.Series(dtype=float)
    assert annualized_return(s) == 0.0
    assert annualized_volatility(s) == 0.0
    assert sharpe_ratio(s) == 0.0
    assert sortino_ratio(s) == 0.0
    assert calmar_ratio(s) == 0.0
    assert max_drawdown(s) == 0.0


def test_max_drawdown_basic() -> None:
    equity = pd.Series([1.0, 1.2, 0.9, 1.1])
    # peak=1.2 -> trough=0.9 => -25%
    assert abs(max_drawdown(equity) - (-0.25)) < 1e-9


def test_sharpe_positive_for_constant_positive_returns() -> None:
    r = pd.Series([0.001] * 300)
    assert sharpe_ratio(r) > 0.0
    # No downside returns => downside deviation is 0 => Sortino defined as 0 here.
    assert sortino_ratio(r) == 0.0


def test_calmar_zero_when_no_drawdown() -> None:
    r = pd.Series([0.001] * 300)
    # With strictly positive constant returns, max drawdown is 0 (monotone equity),
    # so Calmar is defined as 0 in our implementation.
    assert calmar_ratio(r) == 0.0
