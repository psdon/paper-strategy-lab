# paper-strategy-lab

Analyze and reproduce the trading/investing strategies described in `ssrn-3247865.pdf`.

Paper link: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3247865`

See `docs/WORKFLOW.md` for the end-to-end flow from PDF → YAML specs → backtests.
See `docs/BACKTEST_PLAN.md` for the plan to backtest the full paper and keep this repo public-ready.
See `docs/COVERAGE.md` for current implementation coverage.
See `DISCLAIMER.md` for important usage disclaimers.

## Data: Sharadar

We use the local **Sharadar** dataset. On this machine it lives under `~/Downloads/sharadar/`.

You can also set `SHARADAR_DIR` to point at the folder.

Recommended: symlink it into the repo (the data is not committed):

```bash
mkdir -p data
ln -s ~/Downloads/sharadar data/sharadar
```

## Datasets Needed

This repo is **bring-your-own-data**. Do not commit datasets to git.

Minimum to run the SSRN leaderboard (`strategies/ssrn-3247865.yaml`):
- **Sharadar SFP** (ETFs daily OHLCV): `SHARADAR_SFP_*.csv` (uses `closeadj`)
- **Sharadar TICKERS** (metadata): `SHARADAR_TICKERS_*.csv`

Required for the US equities strategies (paper section 3.* anomalies / factors):
- **Sharadar SEP** (equities daily OHLCV): `SHARADAR_SEP_*.csv`
- **Sharadar DAILY** (daily valuations/fundamentals): `SHARADAR_DAILY_*.csv` (e.g. `pe`, `pb`, `marketcap`)

Not yet wired (blocked until we add data/connectors):
- **Options chains** (for options strategies in paper section 2.* / 7.*)
- **Futures curves / roll data** (for commodities/futures carry/curve strategies)
- **Rates/curves** (risk-free + yield curves for fixed income / FX carry)

## Risk-Adjusted Metrics (Sharpe vs Sortino vs Calmar)

We report multiple “risk-adjusted” ratios because they penalize risk differently:

- **Sharpe**: excess return divided by total volatility (standard deviation). Penalizes upside and downside equally.
- **Sortino**: excess return divided by *downside deviation* (only returns below a target, usually 0%). Penalizes harmful volatility more than “good” volatility.
- **Calmar**: CAGR divided by absolute max drawdown. Emphasizes drawdown severity over day-to-day volatility.

In this repo’s default reports, the “excess return” uses a 0% risk-free rate unless a risk-free series is provided.

## Setup

Prereqs: Python 3.11+ and `uv`.

```bash
cd personal/paper-strategy-lab
uv venv --python 3.13
source .venv/bin/activate
uv sync --all-extras
```

## Add the paper PDF

Place the PDF at:

`data/papers/ssrn-3247865.pdf`

This repo does not commit PDFs.

## Extract text + strategy candidates

```bash
paper-strategy-lab extract-text data/papers/ssrn-3247865.pdf --out tmp/ssrn-3247865.pages.jsonl
paper-strategy-lab extract-strategy-candidates tmp/ssrn-3247865.pages.jsonl --out tmp/ssrn-3247865.candidates.jsonl
```

## Sanity-check: example backtests

```bash
paper-strategy-lab list-strategies strategies/examples.yaml
paper-strategy-lab backtest strategies/examples.yaml buy-and-hold-spy --start 2005-01-01
paper-strategy-lab backtest strategies/examples.yaml sma-20-100-spy --start 2005-01-01
```

## Run the SSRN leaderboard (5y, long-only)

Uses Sharadar SFP adjusted prices.

```bash
paper-strategy-lab leaderboard strategies/ssrn-3247865.yaml --years 5
```

To reproduce the full “since 2005” report used in this repo:

```bash
paper-strategy-lab leaderboard strategies/ssrn-3247865.yaml --start 2005-01-01 --out-md docs/RESULTS_since_2005.md
```

## Next: encode strategies

Once you confirm the strategy list from the paper, translate each strategy into a YAML spec under `strategies/` and run:

```bash
paper-strategy-lab list-strategies strategies/ssrn-3247865.yaml
```

## Notes

- `extract-strategy-candidates` is heuristic: it surfaces likely “strategy blocks” from page text.
- Backtesting is scaffolded; you’ll still need to map each paper strategy to an implementable spec.
