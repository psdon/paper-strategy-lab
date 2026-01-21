# Workflow

## 1) Put the paper in place

- Save the PDF as `data/papers/ssrn-3247865.pdf` (not committed).

## 2) Extract searchable text

```bash
uv venv --python 3.13
source .venv/bin/activate
uv sync --all-extras

paper-strategy-lab extract-text data/papers/ssrn-3247865.pdf --out tmp/ssrn-3247865.pages.jsonl
```

The output is JSONL with `{page_index, text}` per line so you can grep/parse it easily.

## 3) Surface likely strategy blocks

```bash
paper-strategy-lab extract-strategy-candidates tmp/ssrn-3247865.pages.jsonl --out tmp/ssrn-3247865.candidates.jsonl
```

Open `tmp/ssrn-3247865.candidates.jsonl` and confirm which snippets correspond to real strategies.

## 4) Encode strategies as YAML

Create `strategies/ssrn-3247865.yaml` entries under `strategies:` with:

- `id`: stable identifier
- `name`: human-readable name
- `description`: optional
- `params`: runner-specific parameters (at minimum, built-ins expect `kind` + `ticker`)

## 5) Backtest (scaffold)

```bash
paper-strategy-lab list-strategies strategies/ssrn-3247865.yaml
paper-strategy-lab backtest strategies/ssrn-3247865.yaml <strategy-id> --start 2005-01-01
```

To run all currently implemented strategies and rank by Sharpe:

```bash
paper-strategy-lab leaderboard strategies/ssrn-3247865.yaml --years 5
```

The built-in runner currently supports (growing list):

- `kind: buy_and_hold`
- `kind: sma_crossover` with `fast` and `slow`
- `kind: single_moving_average` / `two_moving_averages` / `three_moving_averages`
- `kind: channel_breakout` / `support_resistance_breakout`
- `kind: time_series_momentum`
- `kind: mean_reversion_drawdown`
- `kind: sector_momentum_rotation`
- `kind: multi_asset_trend_equal`
- `kind: trend_follow_invvol`

Extend `src/paper_strategy_lab/strategies/builtins.py` and `src/paper_strategy_lab/strategies/runner.py` as you add paper-specific strategy logic.
