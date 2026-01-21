from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from paper_strategy_lab.market_data import MarketData

from .builtins import (
    buy_and_hold,
    channel_breakout,
    equity_cross_sectional_momentum,
    equity_low_volatility_long_only,
    equity_multifactor_long_only,
    equity_residual_momentum,
    equity_value_long_only,
    mean_reversion_drawdown,
    multi_asset_trend_following_equal_weight,
    sector_momentum_rotation,
    single_moving_average,
    sma_crossover,
    support_resistance_breakout,
    three_moving_averages,
    time_series_momentum,
    trend_following_momentum_inv_vol,
    two_moving_averages,
)
from .spec import StrategySpec


@dataclass(frozen=True)
class StrategyRunConfig:
    ticker: str
    start: str | None = None
    end: str | None = None


_BUILTIN_KINDS: dict[str, Callable[..., pd.DataFrame]] = {
    "buy_and_hold": buy_and_hold,
    "sma_crossover": sma_crossover,
    "single_moving_average": single_moving_average,
    "two_moving_averages": two_moving_averages,
    "three_moving_averages": three_moving_averages,
    "support_resistance_breakout": support_resistance_breakout,
    "channel_breakout": channel_breakout,
    "time_series_momentum": time_series_momentum,
    "mean_reversion_drawdown": mean_reversion_drawdown,
    "sector_momentum_rotation": sector_momentum_rotation,
    "multi_asset_trend_equal": multi_asset_trend_following_equal_weight,
    "trend_follow_invvol": trend_following_momentum_inv_vol,
    "equity_cs_momentum": equity_cross_sectional_momentum,
    "equity_value": equity_value_long_only,
    "equity_low_vol": equity_low_volatility_long_only,
    "equity_multifactor": equity_multifactor_long_only,
    "equity_residual_momentum": equity_residual_momentum,
}


def resolve_strategy_callable(kind: str) -> Callable[..., pd.DataFrame]:
    try:
        return _BUILTIN_KINDS[kind]
    except KeyError as e:
        raise KeyError(f"Unknown strategy kind={kind!r}. Known: {sorted(_BUILTIN_KINDS)}") from e


def run_strategy_weights(data: MarketData, spec: StrategySpec) -> pd.DataFrame:
    """
    Returns a weights DataFrame indexed like prices with columns like prices.
    """
    kind = str(spec.kind or "").strip()
    if not kind:
        raise ValueError(f"Strategy {spec.id!r} missing kind")
    fn = resolve_strategy_callable(kind)
    return fn(data, **spec.params)
