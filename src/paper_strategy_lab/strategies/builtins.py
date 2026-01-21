from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Rebalance:
    kind: str  # "daily" | "monthly"


def _normalize_weights(weights: object) -> pd.DataFrame:
    w = pd.DataFrame(weights).copy()
    w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    row_sum = w.sum(axis=1)
    safe = row_sum.where(row_sum.abs() > 0, 1.0)
    w = w.div(safe, axis=0)
    w = w.where(row_sum.abs() > 0, 0.0)
    return w


def _month_ends(index: pd.Index) -> pd.DatetimeIndex:
    idx = pd.DatetimeIndex(index)
    s = idx.to_series()
    month_end = s.groupby(s.dt.to_period("M")).max().sort_index()
    return pd.DatetimeIndex(month_end.values)


def _apply_monthly_rebalance(
    weights_on_rebalance_days: pd.DataFrame, index: pd.Index
) -> pd.DataFrame:
    w = weights_on_rebalance_days.reindex(pd.DatetimeIndex(index))
    w = w.replace(0.0, np.nan).ffill().fillna(0.0)
    return _normalize_weights(w)


def buy_and_hold(prices: pd.DataFrame | pd.Series, **_params: object) -> pd.DataFrame:
    px0 = prices.copy()
    px: pd.DataFrame = px0.to_frame() if isinstance(px0, pd.Series) else px0
    w = px.notna().astype(float)
    return _normalize_weights(w)


def sma_crossover(
    prices: pd.DataFrame | pd.Series, fast: int = 20, slow: int = 100, **_params: object
) -> pd.DataFrame:
    px0 = prices.copy()
    px: pd.DataFrame = px0.to_frame() if isinstance(px0, pd.Series) else px0
    if fast <= 0 or slow <= 0 or fast >= slow:
        raise ValueError("Expected 0 < fast < slow")
    fast_sma = px.rolling(fast).mean()
    slow_sma = px.rolling(slow).mean()
    w = (fast_sma > slow_sma).astype(float)
    return _normalize_weights(w)


def single_moving_average(
    prices: pd.DataFrame | pd.Series, window: int = 200, **_params: object
) -> pd.DataFrame:
    px0 = prices.copy()
    px: pd.DataFrame = px0.to_frame() if isinstance(px0, pd.Series) else px0
    if window <= 0:
        raise ValueError("Expected window > 0")
    w = (px > px.rolling(window).mean()).astype(float)
    return _normalize_weights(w)


def two_moving_averages(
    prices: pd.DataFrame | pd.Series, fast: int = 50, slow: int = 200, **_params: object
) -> pd.DataFrame:
    return sma_crossover(prices, fast=fast, slow=slow, **_params)


def three_moving_averages(
    prices: pd.DataFrame | pd.Series,
    fast: int = 20,
    mid: int = 50,
    slow: int = 200,
    **_params: object,
) -> pd.DataFrame:
    px0 = prices.copy()
    px: pd.DataFrame = px0.to_frame() if isinstance(px0, pd.Series) else px0
    if not (0 < fast < mid < slow):
        raise ValueError("Expected 0 < fast < mid < slow")
    f = px.rolling(fast).mean()
    m = px.rolling(mid).mean()
    s = px.rolling(slow).mean()
    w = ((f > m) & (m > s)).astype(float)
    return _normalize_weights(w)


def channel_breakout(
    prices: pd.DataFrame | pd.Series,
    entry_days: int = 20,
    exit_days: int = 10,
    **_params: object,
) -> pd.DataFrame:
    px0 = prices.copy()
    px: pd.DataFrame = px0.to_frame() if isinstance(px0, pd.Series) else px0
    if entry_days <= 1 or exit_days <= 1:
        raise ValueError("Expected entry_days and exit_days > 1")

    hi: pd.DataFrame = pd.DataFrame(px.rolling(entry_days).max().shift(1))
    lo: pd.DataFrame = pd.DataFrame(px.rolling(exit_days).min().shift(1))

    w: pd.DataFrame = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    for col in px.columns:
        pos = 0.0
        for i in range(len(px)):
            p = px[col].iat[i]
            h = hi[col].iat[i]
            low = lo[col].iat[i]
            if np.isnan(p) or np.isnan(h) or np.isnan(low):
                pos = 0.0
            elif pos == 0.0 and p > h:
                pos = 1.0
            elif pos == 1.0 and p < low:
                pos = 0.0
            w[col].iat[i] = pos

    return _normalize_weights(w)


def support_resistance_breakout(
    prices: pd.DataFrame | pd.Series, window_days: int = 50, **_params: object
) -> pd.DataFrame:
    return channel_breakout(prices, entry_days=window_days, exit_days=window_days, **_params)


def time_series_momentum(
    prices: pd.DataFrame | pd.Series, lookback_days: int = 252, **_params: object
) -> pd.DataFrame:
    px = prices.copy()
    if isinstance(px, pd.Series):
        px = px.to_frame()
    if lookback_days <= 0:
        raise ValueError("Expected lookback_days > 0")
    mom = px.pct_change(lookback_days)
    w = (mom > 0).astype(float)
    return _normalize_weights(w)


def mean_reversion_drawdown(
    prices: pd.DataFrame | pd.Series,
    lookback_days: int = 5,
    entry_return: float = -0.03,
    exit_return: float = 0.0,
    **_params: object,
) -> pd.DataFrame:
    px = prices.copy()
    if isinstance(px, pd.Series):
        px = px.to_frame()
    if lookback_days <= 0:
        raise ValueError("Expected lookback_days > 0")

    r = px.pct_change(lookback_days)
    w = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    for col in px.columns:
        pos = 0.0
        for i in range(len(px)):
            x = r[col].iat[i]
            if np.isnan(x):
                pos = 0.0
            elif pos == 0.0 and x <= entry_return:
                pos = 1.0
            elif pos == 1.0 and x >= exit_return:
                pos = 0.0
            w[col].iat[i] = pos

    return _normalize_weights(w)


def sector_momentum_rotation(
    prices: pd.DataFrame | pd.Series,
    lookback_days: int = 126,
    top_k: int = 3,
    ma_filter_days: int | None = 200,
    **_params: object,
) -> pd.DataFrame:
    px = prices.copy()
    if isinstance(px, pd.Series):
        px = px.to_frame()

    if lookback_days <= 0:
        raise ValueError("Expected lookback_days > 0")
    if top_k <= 0:
        raise ValueError("Expected top_k > 0")

    mom = px.pct_change(lookback_days)
    ok = pd.DataFrame(True, index=px.index, columns=px.columns)
    if ma_filter_days is not None:
        ok = px > px.rolling(ma_filter_days).mean()

    rebalance_dates = _month_ends(px.index)
    w_reb = pd.DataFrame(0.0, index=rebalance_dates, columns=px.columns)

    for d in rebalance_dates:
        scores = mom.loc[d]
        scores = scores.where(ok.loc[d])
        scores = scores.dropna().sort_values(ascending=False)
        picks = list(scores.head(top_k).index)
        if picks:
            w_reb.loc[d, picks] = 1.0 / len(picks)

    return _apply_monthly_rebalance(w_reb, px.index)


def multi_asset_trend_following_equal_weight(
    prices: pd.DataFrame | pd.Series,
    lookback_days: int = 252,
    **_params: object,
) -> pd.DataFrame:
    px = prices.copy()
    if isinstance(px, pd.Series):
        px = px.to_frame()

    mom = px.pct_change(lookback_days)
    rebalance_dates = _month_ends(px.index)
    w_reb = pd.DataFrame(0.0, index=rebalance_dates, columns=px.columns)
    for d in rebalance_dates:
        eligible = list(mom.loc[d][lambda s: s > 0].dropna().index)
        if eligible:
            w_reb.loc[d, eligible] = 1.0 / len(eligible)

    return _apply_monthly_rebalance(w_reb, px.index)


def trend_following_momentum_inv_vol(
    prices: pd.DataFrame | pd.Series,
    lookback_days: int = 252,
    vol_days: int = 63,
    **_params: object,
) -> pd.DataFrame:
    px = prices.copy()
    if isinstance(px, pd.Series):
        px = px.to_frame()

    mom = px.pct_change(lookback_days)
    vol = px.pct_change().rolling(vol_days).std() * np.sqrt(252)

    rebalance_dates = _month_ends(px.index)
    w_reb = pd.DataFrame(0.0, index=rebalance_dates, columns=px.columns)
    for d in rebalance_dates:
        m = mom.loc[d].dropna()
        v = vol.loc[d].dropna()
        eligible = [
            c for c in px.columns if c in m.index and c in v.index and v[c] > 0 and m[c] > 0
        ]
        if not eligible:
            continue
        inv = pd.Series({c: 1.0 / float(v[c]) for c in eligible})
        inv = inv / inv.sum()
        w_reb.loc[d, eligible] = inv.values

    return _apply_monthly_rebalance(w_reb, px.index)
