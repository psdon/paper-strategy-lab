from __future__ import annotations

import pandas as pd

from paper_strategy_lab.backtest.portfolio import run_portfolio_backtest


def test_backtest_single_asset_buy_and_hold_matches_returns() -> None:
    idx = pd.date_range("2020-01-01", periods=5, freq="D")
    prices = pd.DataFrame({"AAA": [100.0, 110.0, 99.0, 99.0, 108.9]}, index=idx)
    weights = pd.DataFrame({"AAA": [1.0] * len(idx)}, index=idx)

    bt = run_portfolio_backtest(prices=prices, weights=weights, lag_days=1)

    # First day has 0 return due to pct_change fill and lag.
    assert bt.daily_returns.index.equals(idx)
    assert bt.equity_curve.index.equals(idx)
    assert bt.turnover.index.equals(idx)

    # With 1-day lag, the first executed rebalance happens on day 2 (0 -> 1).
    assert float(bt.turnover.sum()) == 1.0
