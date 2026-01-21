# Coverage (ssrn-3247865)

This table tracks which paper strategies are implemented in code/specs.

- `implemented`: runnable via `paper-strategy-lab leaderboard strategies/ssrn-3247865.yaml`
- `planned`: mapped but not yet implemented
- `blocked`: needs data not currently wired (options chains, futures curves, OTC quotes, etc.)

| Paper Section | Title | Status | Strategy ID | Notes |
|---|---|---|---|---|
| 2.2 | Covered call | blocked |  | Options strategy; needs options chain data. |
| 2.3 | Covered put | blocked |  | Options strategy; needs options chain data. |
| 2.4 | Protective put | blocked |  | Options strategy; needs options chain data. |
| 2.5 | Protective call | blocked |  | Options strategy; needs options chain data. |
| 2.6 | Bull call spread | blocked |  | Options strategy; needs options chain data. |
| 2.7 | Bull put spread | blocked |  | Options strategy; needs options chain data. |
| 2.8 | Bear call spread | blocked |  | Options strategy; needs options chain data. |
| 2.9 | Bear put spread | blocked |  | Options strategy; needs options chain data. |
| 2.10 | Long synthetic forward | blocked |  | Options strategy; needs options chain data. |
| 2.11 | Short synthetic forward | blocked |  | Options strategy; needs options chain data. |
| 2.12 | Long combo | blocked |  | Options strategy; needs options chain data. |
| 2.13 | Short combo | blocked |  | Options strategy; needs options chain data. |
| 2.14 | Bull call ladder | blocked |  | Options strategy; needs options chain data. |
| 2.15 | Bull put ladder | blocked |  | Options strategy; needs options chain data. |
| 2.16 | Bear call ladder | blocked |  | Options strategy; needs options chain data. |
| 2.17 | Bear put ladder | blocked |  | Options strategy; needs options chain data. |
| 2.18 | Calendar call spread | blocked |  | Options strategy; needs options chain data. |
| 2.19 | Calendar put spread | blocked |  | Options strategy; needs options chain data. |
| 2.20 | Diagonal call spread | blocked |  | Options strategy; needs options chain data. |
| 2.21 | Diagonal put spread | blocked |  | Options strategy; needs options chain data. |
| 2.22 | Ratio call spread | blocked |  | Options strategy; needs options chain data. |
| 2.23 | Ratio put spread | blocked |  | Options strategy; needs options chain data. |
| 2.24 | Backspread | blocked |  | Options strategy; needs options chain data. |
| 2.25 | Box spread | blocked |  | Options strategy; needs options chain data. |
| 2.26 | Butterfly spread | blocked |  | Options strategy; needs options chain data. |
| 2.27 | Condor spread | blocked |  | Options strategy; needs options chain data. |
| 2.28 | Iron butterfly spread | blocked |  | Options strategy; needs options chain data. |
| 2.29 | Iron condor spread | blocked |  | Options strategy; needs options chain data. |
| 2.30 | Straddle | blocked |  | Options strategy; needs options chain data. |
| 2.31 | Strangle | blocked |  | Options strategy; needs options chain data. |
| 2.32 | Collar | blocked |  | Options strategy; needs options chain data. |
| 2.33 | Ratio collar | blocked |  | Options strategy; needs options chain data. |
| 2.34 | Fence | blocked |  | Options strategy; needs options chain data. |
| 2.35 | Seagull spread | blocked |  | Options strategy; needs options chain data. |
| 2.36 | Switch | blocked |  | Options strategy; needs options chain data. |
| 2.37 | Risk reversal | blocked |  | Options strategy; needs options chain data. |
| 2.38 | Costless collar | blocked |  | Options strategy; needs options chain data. |
| 2.39 | Married put | blocked |  | Options strategy; needs options chain data. |
| 2.40 | Synthetic long stock | blocked |  | Options strategy; needs options chain data. |
| 2.41 | Synthetic short stock | blocked |  | Options strategy; needs options chain data. |
| 2.42 | Synthetic put | blocked |  | Options strategy; needs options chain data. |
| 2.43 | Synthetic call | blocked |  | Options strategy; needs options chain data. |
| 2.44 | Conversion | blocked |  | Options strategy; needs options chain data. |
| 2.45 | Reverse conversion | blocked |  | Options strategy; needs options chain data. |
| 3.1 | Price-momentum | implemented | 3.1-price-momentum | kind=time_series_momentum |
| 3.2 | Earnings-momentum | planned |  | Not yet implemented. |
| 3.3 | Value | planned |  | Not yet implemented. |
| 3.4 | Low-volatility anomaly | planned |  | Not yet implemented. |
| 3.5 | Implied volatility | planned |  | Not yet implemented. |
| 3.6 | Multifactor portfolio | planned |  | Not yet implemented. |
| 3.7 | Residual momentum | planned |  | Not yet implemented. |
| 3.8 | Pairs trading | planned |  | Not yet implemented. |
| 3.9 | Mean-reversion – single cluster | implemented | 3.9-mean-reversion | kind=mean_reversion_drawdown |
| 3.11 | Single moving average | implemented | 3.11-single-ma | kind=single_moving_average |
| 3.12 | Two moving averages | implemented | 3.12-two-ma | kind=two_moving_averages |
| 3.13 | Three moving averages | implemented | 3.13-three-ma | kind=three_moving_averages |
| 3.14 | Support and resistance | implemented | 3.14-support-resistance | kind=support_resistance_breakout |
| 3.15 | Channel | implemented | 3.15-channel | kind=channel_breakout |
| 3.16 | Event-driven – M&A | planned |  | Not yet implemented. |
| 3.17 | Machine learning – single-stock KNN | planned |  | Not yet implemented. |
| 3.18 | Statistical arbitrage – optimization | planned |  | Not yet implemented. |
| 3.19 | Market-making | planned |  | Not yet implemented. |
| 3.20 | Alpha combos | planned |  | Not yet implemented. |
| 4.1 | Sector momentum rotation | implemented | 4.1-sector-mom-rotation | kind=sector_momentum_rotation |
| 4.2 | Alpha rotation | planned |  | Not yet implemented. |
| 4.3 | Index volatility | planned |  | Not yet implemented. |
| 4.4 | Smart beta | planned |  | Not yet implemented. |
| 4.5 | Leveraged ETFs | planned |  | Not yet implemented. |
| 4.6 | Multi-asset trend following | implemented | 4.6-multi-asset-trend | kind=multi_asset_trend_equal |
| 5.2 | Rolling down the yield curve | blocked |  | Rates strategy; needs yield curves / bond data. |
| 5.3 | Floating-to-fixed interest rate swap | blocked |  | Rates strategy; needs yield curves / bond data. |
| 5.4 | Fixed-to-floating interest rate swap | blocked |  | Rates strategy; needs yield curves / bond data. |
| 5.5 | Treasury bond futures duration neutral carry | blocked |  | Rates strategy; needs yield curves / bond data. |
| 5.6 | Swap spread | blocked |  | Rates strategy; needs yield curves / bond data. |
| 5.7 | Butterfly | blocked |  | Rates strategy; needs yield curves / bond data. |
| 5.8 | PCA curve strategy | blocked |  | Rates strategy; needs yield curves / bond data. |
| 6.1 | TIPS breakeven inflation | blocked |  | Rates strategy; needs yield curves / bond data. |
| 6.2 | Basis trade | blocked |  | Rates strategy; needs yield curves / bond data. |
| 7.1 | Risk reversal | blocked |  | Options strategy; needs options chain data. |
| 7.2 | Dispersion | blocked |  | Options strategy; needs options chain data. |
| 7.3 | Risk-free arbitrage | blocked |  | Options strategy; needs options chain data. |
| 7.4 | Butterfly | blocked |  | Options strategy; needs options chain data. |
| 7.5 | Straddle | blocked |  | Options strategy; needs options chain data. |
| 7.6 | Strangle | blocked |  | Options strategy; needs options chain data. |
| 7.7 | Directional straddle | blocked |  | Options strategy; needs options chain data. |
| 8.1 | Carry | blocked |  | Needs futures/FX + carry inputs not wired yet. |
| 8.2 | Value | blocked |  | Needs futures/FX + carry inputs not wired yet. |
| 8.3 | Curve | blocked |  | Needs futures/FX + carry inputs not wired yet. |
| 8.4 | Momentum & carry combo | blocked |  | Needs futures/FX + carry inputs not wired yet. |
| 9.1 | FX carry | blocked |  | Needs futures/FX + carry inputs not wired yet. |
| 9.2 | FX momentum | blocked |  | Needs futures/FX + carry inputs not wired yet. |
| 9.3 | FX value | blocked |  | Needs futures/FX + carry inputs not wired yet. |
| 10.1 | Single stock, index and sector hedged carry | blocked |  | Specialized/institutional data not wired yet. |
| 10.2 | Convertible arbitrage (hedged carry) | blocked |  | Specialized/institutional data not wired yet. |
| 10.3 | Convertible arbitrage (carry + gamma) | blocked |  | Specialized/institutional data not wired yet. |
| 10.4 | Trend following (momentum) | implemented | 10.4-trend-following-mom-invvol | kind=trend_follow_invvol |
| 11.1 | CDS basis | blocked |  | Specialized/institutional data not wired yet. |
| 11.2 | Index tranche arbitrage | blocked |  | Specialized/institutional data not wired yet. |
| 11.3 | Recovery rate arbitrage | blocked |  | Specialized/institutional data not wired yet. |
| 11.4 | Capital structure arbitrage | blocked |  | Specialized/institutional data not wired yet. |
| 12.1 | ETF arbitrage | blocked |  | Specialized/institutional data not wired yet. |
| 12.2 | Triangle arbitrage | blocked |  | Specialized/institutional data not wired yet. |
| 12.3 | Covered interest parity (CIP) | blocked |  | Specialized/institutional data not wired yet. |
| 12.4 | Treasury bond futures arbitrage | blocked |  | Specialized/institutional data not wired yet. |
| 12.5 | Repo | blocked |  | Specialized/institutional data not wired yet. |
| 13.1 | Correlation trading | blocked |  | Specialized/institutional data not wired yet. |
| 13.2 | Curve | blocked |  | Specialized/institutional data not wired yet. |
| 13.3 | Capital structure arbitrage | blocked |  | Specialized/institutional data not wired yet. |
| 13.4 | M&A arbitrage | blocked |  | Specialized/institutional data not wired yet. |
| 14.1 | Distressed debt | blocked |  | Specialized/institutional data not wired yet. |
| 14.2 | CLO equity | blocked |  | Specialized/institutional data not wired yet. |
| 14.3 | Master limited partnership (MLP) | blocked |  | Specialized/institutional data not wired yet. |
| 15.1 | Commercial real estate – private equity approach | blocked |  | Specialized/institutional data not wired yet. |
| 16.1 | Real estate investment trust (REIT) | planned |  | Not yet implemented. |
| 16.2 | Real estate momentum – individual REITs approach | planned |  | Not yet implemented. |
| 16.3 | Real estate momentum – property type approach | planned |  | Not yet implemented. |
| 16.4 | Real estate momentum – regional approach | planned |  | Not yet implemented. |
| 17.1 | Repo | planned |  | Not yet implemented. |
| 17.2 | Treasury | planned |  | Not yet implemented. |
| 17.3 | Dollar | planned |  | Not yet implemented. |
| 18.1 | Machine learning – neural networks | planned |  | Not yet implemented. |
| 18.2 | Machine learning – support vector machine | planned |  | Not yet implemented. |
| 18.3 | Machine learning – Bayes | planned |  | Not yet implemented. |
| 18.4 | Machine learning – k-nearest neighbors | planned |  | Not yet implemented. |
| 18.5 | Sentiment analysis | planned |  | Not yet implemented. |
| 19.1 | Energy | planned |  | Not yet implemented. |
| 19.2 | Fundamental macro momentum | planned |  | Not yet implemented. |
| 19.3 | Inflation | planned |  | Not yet implemented. |
| 20.1 | Global macro | planned |  | Not yet implemented. |
| 21.1 | Publicly traded infrastructure | planned |  | Not yet implemented. |
| 22.1 | Tax arbitrage | blocked |  | Specialized/institutional data not wired yet. |
