# Results

Generated: `2026-01-21 14:23:13`

## Inputs & Assumptions

- Data: Sharadar (SFP/SEP/DAILY as needed) via `SHARADAR_DIR` or `data/sharadar` symlink.
- Window: start=`2005-01-01`
- Frequency: daily close-to-close; positions applied with a 1-day lag.
- Costs: fee=0.0 bps, slippage=0.0 bps (applied to turnover).

## Leaderboard (Calmar-ranked)

| paper_section | id | name | kind | universe | start_date | end_date | days | sharpe | sortino | calmar | cagr | vol | maxdd | avg_exposure | avg_turnover | bench_id | bench_sharpe | bench_sortino | bench_calmar | bench_cagr | bench_vol | bench_maxdd | sharpe_vs_bh | sortino_vs_bh | calmar_vs_bh | cagr_vs_bh | maxdd_vs_bh |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.11 | 3.11-single-ma | 3.11 Single moving average (SPY, SMA200) | single_moving_average | SPY | 2005-01-03 | 2026-01-08 | 5288 | 0.78 | 1.06 | 0.42 | 8.58% | 11.40% | -20.50% | 0.76 | 0.02 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.15 | +0.18 | +0.22 | -2.13% | +34.70% |
| 3.3 | 3.3-value-us-equities | 3.3 Value (US equities, low PE) | equity_value | sharadar_us_equities_liquid(n=300) | 2005-01-03 | 2026-01-08 | 5288 | 0.88 | 1.25 | 0.36 | 17.29% | 20.40% | -48.68% | 1.00 | 0.00 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.25 | +0.37 | +0.16 | +6.58% | +6.52% |
| 3.14 | 3.14-support-resistance | 3.14 Support & resistance (SPY, 50d breakout) | support_resistance_breakout | SPY | 2005-01-03 | 2026-01-08 | 5288 | 0.71 | 0.97 | 0.35 | 7.38% | 10.96% | -20.82% | 0.70 | 0.01 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.08 | +0.08 | +0.16 | -3.32% | +34.38% |
| 3.7 | 3.7-residual-momentum-us-equities | 3.7 Residual momentum (US equities, vs SPY) | equity_residual_momentum | sharadar_us_equities_liquid(n=300) | 2005-01-03 | 2026-01-08 | 5288 | 0.86 | 1.21 | 0.35 | 15.63% | 19.09% | -44.52% | 0.90 | 0.00 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.23 | +0.33 | +0.16 | +4.92% | +10.68% |
| 3.1 | 3.1-cs-momentum-us-equities | 3.1 Price-momentum (US equities, cross-sectional) | equity_cs_momentum | sharadar_us_equities_liquid(n=300) | 2005-01-03 | 2026-01-08 | 5288 | 0.85 | 1.21 | 0.34 | 17.05% | 21.09% | -50.50% | 0.95 | 0.00 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.22 | +0.32 | +0.14 | +6.34% | +4.70% |
| 3.4 | 3.4-low-vol-us-equities | 3.4 Low-volatility anomaly (US equities) | equity_low_vol | sharadar_us_equities_liquid(n=300) | 2005-01-03 | 2026-01-08 | 5288 | 0.82 | 1.17 | 0.32 | 14.77% | 18.90% | -46.08% | 0.95 | 0.00 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.19 | +0.28 | +0.13 | +4.06% | +9.12% |
| 3.6 | 3.6-multifactor-us-equities | 3.6 Multifactor portfolio (US equities) | equity_multifactor | sharadar_us_equities_liquid(n=300) | 2005-01-03 | 2026-01-08 | 5288 | 0.83 | 1.17 | 0.32 | 15.84% | 20.31% | -49.91% | 0.95 | 0.00 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.20 | +0.28 | +0.12 | +5.13% | +5.29% |
| 4.6 | 4.6-multi-asset-trend | 4.6 Multi-asset trend following (mom>0, equal-weight) | multi_asset_trend_equal | SPY,QQQ,IWM,EFA,EEM,TLT,IEF,LQD,HYG,GLD | 2005-01-03 | 2026-01-08 | 5288 | 0.75 | 1.07 | 0.29 | 7.82% | 10.78% | -26.83% | 0.95 | 0.00 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.12 | +0.19 | +0.10 | -2.89% | +28.37% |
| 10.4 | 10.4-trend-following-mom-invvol | 10.4 Trend following (momentum, inv-vol) | trend_follow_invvol | SPY,QQQ,IWM,EFA,EEM,TLT,IEF,LQD,HYG,GLD | 2005-01-03 | 2026-01-08 | 5288 | 0.83 | 1.20 | 0.29 | 6.62% | 8.10% | -22.75% | 0.95 | 0.01 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.20 | +0.31 | +0.10 | -4.09% | +32.45% |
| 3.13 | 3.13-three-ma | 3.13 Three moving averages (SPY, 20/50/200) | three_moving_averages | SPY | 2005-01-03 | 2026-01-08 | 5288 | 0.59 | 0.80 | 0.27 | 5.40% | 9.72% | -20.18% | 0.58 | 0.02 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | -0.04 | -0.09 | +0.07 | -5.31% | +35.02% |
| 3.12 | 3.12-two-ma | 3.12 Two moving averages (SPY, 50/200) | two_moving_averages | SPY | 2005-01-03 | 2026-01-08 | 5288 | 0.69 | 0.96 | 0.26 | 8.88% | 13.57% | -33.70% | 0.75 | 0.00 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.07 | +0.07 | +0.07 | -1.83% | +21.50% |
| 3.1 | 3.1-price-momentum | 3.1 Price-momentum (SPY) | time_series_momentum | SPY | 2005-01-03 | 2026-01-08 | 5288 | 0.62 | 0.84 | 0.25 | 7.74% | 13.46% | -31.17% | 0.79 | 0.01 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | -0.01 | -0.05 | +0.05 | -2.97% | +24.03% |
| 3.15 | 3.15-channel | 3.15 Channel (SPY, 20/10) | channel_breakout | SPY | 2005-01-03 | 2026-01-08 | 5288 | 0.62 | 0.88 | 0.21 | 5.34% | 9.13% | -25.44% | 0.54 | 0.05 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | -0.01 | -0.01 | +0.02 | -5.37% | +29.76% |
| 4.1 | 4.1-sector-mom-rotation | 4.1 Sector momentum rotation (top3, 6m, MA200) | sector_momentum_rotation | XLB,XLE,XLF,XLI,XLK,XLP,XLU,XLV,XLY,XLRE | 2005-01-03 | 2026-01-08 | 5288 | 0.62 | 0.87 | 0.20 | 9.91% | 17.86% | -50.21% | 0.96 | 0.00 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | -0.01 | -0.02 | +0.00 | -0.80% | +4.99% |
|  | bh-spy | Benchmark: Buy & Hold (SPY) | buy_and_hold | SPY | 2005-01-03 | 2026-01-08 | 5288 | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | 1.00 | 0.00 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | +0.00 | +0.00 | +0.00 | +0.00% | +0.00% |
| 3.9 | 3.9-mean-reversion | 3.9 Mean-reversion (SPY, 5d<-3%) | mean_reversion_drawdown | SPY | 2005-01-03 | 2026-01-08 | 5288 | 0.43 | 0.64 | 0.17 | 4.76% | 12.66% | -28.60% | 0.13 | 0.05 | bh-spy | 0.63 | 0.89 | 0.19 | 10.71% | 19.04% | -55.20% | -0.20 | -0.25 | -0.03 | -5.95% | +26.60% |
