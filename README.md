# paper-strategy-lab

Analyze and reproduce the trading/investing strategies described in `ssrn-3247865.pdf`.

Paper link: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3247865`

See `docs/WORKFLOW.md` for the end-to-end flow from PDF → YAML specs → backtests.
See `docs/BACKTEST_PLAN.md` for the plan to backtest the full paper and keep this repo public-ready.
See `docs/COVERAGE.md` for current implementation coverage.
See `DISCLAIMER.md` for important usage disclaimers.

## Data: Sharadar

We use the local **Sharadar** dataset. On this machine it lives under `~/Downloads/sharadar/`.

Recommended: symlink it into the repo (the data is not committed):

```bash
mkdir -p data
ln -s ~/Downloads/sharadar data/sharadar
```

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

## Next: encode strategies

Once you confirm the strategy list from the paper, translate each strategy into a YAML spec under `strategies/` and run:

```bash
paper-strategy-lab list-strategies strategies/ssrn-3247865.yaml
```

## Notes

- `extract-strategy-candidates` is heuristic: it surfaces likely “strategy blocks” from page text.
- Backtesting is scaffolded; you’ll still need to map each paper strategy to an implementable spec.
