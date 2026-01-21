from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from paper_strategy_lab.market_data import MarketData


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


def buy_and_hold(data: MarketData, **_params: object) -> pd.DataFrame:
    px = data.prices
    w = px.notna().astype(float)
    return _normalize_weights(w)


def sma_crossover(
    data: MarketData, fast: int = 20, slow: int = 100, **_params: object
) -> pd.DataFrame:
    px = data.prices
    if fast <= 0 or slow <= 0 or fast >= slow:
        raise ValueError("Expected 0 < fast < slow")
    fast_sma = px.rolling(fast).mean()
    slow_sma = px.rolling(slow).mean()
    w = (fast_sma > slow_sma).astype(float)
    return _normalize_weights(w)


def single_moving_average(
    data: MarketData, window: int = 200, **_params: object
) -> pd.DataFrame:
    px = data.prices
    if window <= 0:
        raise ValueError("Expected window > 0")
    w = (px > px.rolling(window).mean()).astype(float)
    return _normalize_weights(w)


def two_moving_averages(
    data: MarketData, fast: int = 50, slow: int = 200, **_params: object
) -> pd.DataFrame:
    return sma_crossover(data, fast=fast, slow=slow, **_params)


def three_moving_averages(
    data: MarketData,
    fast: int = 20,
    mid: int = 50,
    slow: int = 200,
    **_params: object,
) -> pd.DataFrame:
    px = data.prices
    if not (0 < fast < mid < slow):
        raise ValueError("Expected 0 < fast < mid < slow")
    f = px.rolling(fast).mean()
    m = px.rolling(mid).mean()
    s = px.rolling(slow).mean()
    w = ((f > m) & (m > s)).astype(float)
    return _normalize_weights(w)


def channel_breakout(
    data: MarketData,
    entry_days: int = 20,
    exit_days: int = 10,
    **_params: object,
) -> pd.DataFrame:
    px = data.prices
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
    data: MarketData, window_days: int = 50, **_params: object
) -> pd.DataFrame:
    return channel_breakout(data, entry_days=window_days, exit_days=window_days, **_params)


def time_series_momentum(
    data: MarketData, lookback_days: int = 252, **_params: object
) -> pd.DataFrame:
    px = data.prices
    if lookback_days <= 0:
        raise ValueError("Expected lookback_days > 0")
    mom = px.pct_change(lookback_days, fill_method=None)
    w = (mom > 0).astype(float)
    return _normalize_weights(w)


def mean_reversion_drawdown(
    data: MarketData,
    lookback_days: int = 5,
    entry_return: float = -0.03,
    exit_return: float = 0.0,
    **_params: object,
) -> pd.DataFrame:
    px = data.prices
    if lookback_days <= 0:
        raise ValueError("Expected lookback_days > 0")

    r = px.pct_change(lookback_days, fill_method=None)
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
    data: MarketData,
    lookback_days: int = 126,
    top_k: int = 3,
    ma_filter_days: int | None = 200,
    **_params: object,
) -> pd.DataFrame:
    px = data.prices

    if lookback_days <= 0:
        raise ValueError("Expected lookback_days > 0")
    if top_k <= 0:
        raise ValueError("Expected top_k > 0")

    mom = px.pct_change(lookback_days, fill_method=None)
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
    data: MarketData,
    lookback_days: int = 252,
    **_params: object,
) -> pd.DataFrame:
    px = data.prices

    mom = px.pct_change(lookback_days, fill_method=None)
    rebalance_dates = _month_ends(px.index)
    w_reb = pd.DataFrame(0.0, index=rebalance_dates, columns=px.columns)
    for d in rebalance_dates:
        eligible = list(mom.loc[d][lambda s: s > 0].dropna().index)
        if eligible:
            w_reb.loc[d, eligible] = 1.0 / len(eligible)

    return _apply_monthly_rebalance(w_reb, px.index)


def trend_following_momentum_inv_vol(
    data: MarketData,
    lookback_days: int = 252,
    vol_days: int = 63,
    **_params: object,
) -> pd.DataFrame:
    px = data.prices

    mom = px.pct_change(lookback_days, fill_method=None)
    vol = px.pct_change(fill_method=None).rolling(vol_days).std() * np.sqrt(252)

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


def _cross_sectional_topk_monthly(
    scores: pd.DataFrame,
    *,
    top_n: int,
    ascending: bool,
) -> pd.DataFrame:
    if top_n <= 0:
        raise ValueError("Expected top_n > 0")

    rebalance_dates = _month_ends(scores.index)
    w_reb = pd.DataFrame(0.0, index=rebalance_dates, columns=scores.columns)

    for d in rebalance_dates:
        row = scores.loc[d].dropna()
        if row.empty:
            continue
        picks = row.sort_values(ascending=ascending).head(top_n).index.tolist()
        if picks:
            w_reb.loc[d, picks] = 1.0 / len(picks)

    return _apply_monthly_rebalance(w_reb, scores.index)


def equity_cross_sectional_momentum(
    data: MarketData,
    lookback_days: int = 252,
    top_n: int = 100,
    **_params: object,
) -> pd.DataFrame:
    """
    Long-only cross-sectional momentum: hold top-N tickers by trailing return.
    """
    px = data.prices
    mom: pd.DataFrame = pd.DataFrame(px.pct_change(lookback_days, fill_method=None))
    return _cross_sectional_topk_monthly(mom, top_n=top_n, ascending=False)


def equity_value_long_only(
    data: MarketData,
    value_field: str = "pe",
    top_n: int = 100,
    **_params: object,
) -> pd.DataFrame:
    """
    Long-only value: hold top-N cheapest by `value_field` (lower is better).

    Requires DAILY feature present in `data.features[value_field]`.
    """
    px = data.prices
    v: pd.DataFrame = pd.DataFrame(data.feature(value_field)).reindex(px.index).ffill()
    v = v.reindex(columns=px.columns)

    if value_field.lower() in {"pe", "pb", "ps"}:
        v = v.where(v > 0)

    return _cross_sectional_topk_monthly(v, top_n=top_n, ascending=True)


def equity_low_volatility_long_only(
    data: MarketData,
    lookback_days: int = 252,
    top_n: int = 100,
    **_params: object,
) -> pd.DataFrame:
    """
    Long-only low-vol anomaly: hold top-N lowest realized volatility.
    """
    px = data.prices
    rets: pd.DataFrame = pd.DataFrame(px.pct_change(fill_method=None))
    vol: pd.DataFrame = pd.DataFrame(rets.rolling(lookback_days).std())
    return _cross_sectional_topk_monthly(vol, top_n=top_n, ascending=True)


def equity_residual_momentum(
    data: MarketData,
    lookback_days: int = 252,
    beta_window_days: int = 252,
    top_n: int = 100,
    **_params: object,
) -> pd.DataFrame:
    """
    Long-only residual momentum: compute CAPM residual returns vs SPY and rank by residual momentum.

    Requires `data.features['benchmark_spy']` containing SPY closeadj prices (single-column DF).
    """
    px = data.prices
    spy_px = data.feature("benchmark_spy").reindex(px.index).ffill()
    spy = spy_px.iloc[:, 0]

    rs: pd.DataFrame = pd.DataFrame(px.pct_change(fill_method=None)).fillna(0.0)
    rm: pd.Series = spy.pct_change(fill_method=None).fillna(0.0)

    # Rolling beta via moments to avoid per-ticker regressions.
    rm_mean = rm.rolling(beta_window_days).mean()
    rm2_mean = (rm * rm).rolling(beta_window_days).mean()
    var_m = rm2_mean - rm_mean * rm_mean
    var_m = var_m.replace(0.0, np.nan)

    rs_mean: pd.DataFrame = pd.DataFrame(rs.rolling(beta_window_days).mean())
    rsm_mean: pd.DataFrame = pd.DataFrame(rs.mul(rm, axis=0).rolling(beta_window_days).mean())
    cov_sm: pd.DataFrame = pd.DataFrame(rsm_mean - rs_mean.mul(rm_mean, axis=0))
    beta: pd.DataFrame = pd.DataFrame(cov_sm.div(var_m, axis=0))

    residual: pd.DataFrame = pd.DataFrame(rs - beta.mul(rm, axis=0))

    # Residual momentum via rolling sum of log(1+r).
    log1p: pd.DataFrame = pd.DataFrame(np.log1p(residual.replace(-1.0, np.nan)))
    score: pd.DataFrame = pd.DataFrame(log1p.rolling(lookback_days).sum())
    return _cross_sectional_topk_monthly(score, top_n=top_n, ascending=False)


def equity_multifactor_long_only(
    data: MarketData,
    lookback_days: int = 252,
    vol_lookback_days: int = 252,
    value_field: str = "pe",
    top_n: int = 100,
    w_mom: float = 1.0,
    w_val: float = 1.0,
    w_low_vol: float = 1.0,
    **_params: object,
) -> pd.DataFrame:
    """
    Simple multifactor: z(mom) + z(-value) + z(-vol), then long top-N.
    """
    px = data.prices
    mom: pd.DataFrame = pd.DataFrame(px.pct_change(lookback_days, fill_method=None))
    rets: pd.DataFrame = pd.DataFrame(px.pct_change(fill_method=None))
    vol: pd.DataFrame = pd.DataFrame(rets.rolling(vol_lookback_days).std())
    val: pd.DataFrame = (
        pd.DataFrame(data.feature(value_field)).reindex(px.index).ffill().reindex(columns=px.columns)
    )
    if value_field.lower() in {"pe", "pb", "ps"}:
        val = val.where(val > 0)

    def zscore(frame: pd.DataFrame) -> pd.DataFrame:
        mu = frame.mean(axis=1)
        sd = pd.Series(frame.std(axis=1)).replace(0.0, np.nan)
        return frame.sub(mu, axis=0).div(sd, axis=0)

    score = (
        w_mom * zscore(mom)
        + w_val * zscore(-val)
        + w_low_vol * zscore(-vol)
    )
    return _cross_sectional_topk_monthly(score, top_n=top_n, ascending=False)
