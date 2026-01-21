# Backtest Plan (ssrn-3247865)

Goal: implement and backtest (as many as feasible of) the strategies described in `ssrn-3247865.pdf` in a way that is **reproducible**, **auditable**, and safe to publish as a **public** GitHub repo.

Important: the paper is primarily **descriptive/pedagogical** and does not provide a canonical dataset, parameter set, or performance table. So “backtesting the paper” means:
- translating each strategy description into an explicit, testable spec
- choosing reasonable default parameters (and documenting them)
- running backtests with realistic assumptions (costs, slippage, roll rules, etc.)
- ranking and comparing results under consistent evaluation criteria

## Principles

- **Public repo hygiene**: never commit datasets (Sharadar, PDFs, vendor files) or secrets.
- **Provenance**: every strategy backtest output links to:
  - paper section number + title
  - dataset source(s) + version/hash
  - parameter values + rebalancing rules
  - cost model assumptions
- **Coverage transparency**: not every strategy is implementable with free/public data. Maintain a “coverage matrix” with statuses: `implemented`, `partial`, `blocked`, `not-applicable`.
- **Comparable evaluation**: choose a benchmark per asset class and compute the same metrics for all strategies.

## Scope & Coverage Matrix

The paper spans many asset classes (equities, options, futures, FX, credit, real estate, crypto, tax arb, etc.). We will classify each strategy into one of:

1) **Implementable (Public Data)**: can be tested with daily bars and/or common public proxies (e.g., ETFs).
2) **Implementable (Licensed Data)**: requires Sharadar or another paid dataset (fundamentals, point-in-time fields).
3) **Implementable (Specialized Data)**: needs options chains, CDS quotes, OTC data, or intraday market microstructure.
4) **Conceptual/Institutional**: tax arbitrage, certain structured products, and strategies requiring non-public constraints.

For public GitHub, we keep the code and tests public; data connectors support “bring your own data”.

## Repository Architecture (Target)

**Data layer**
- `paper_strategy_lab/data_sources/`:
  - `sharadar` loader (prices + fundamentals; point-in-time alignment)
  - optional loaders (Yahoo/Stooq/FRED) for free benchmarks
  - unified interfaces: `get_prices()`, `get_fundamentals()`, `get_rates()`, etc.
- `data/` is local-only (symlinks), excluded from git.

**Strategy layer**
- `strategies/*.yaml`: human-authored specs (paper section, universe, signal, sizing, rebalance, costs).
- `paper_strategy_lab/strategies/`:
  - pure functions that turn data → signals/weights
  - strategy registry + validation (schema checks, required inputs)

**Backtest engine**
- Vectorized daily backtester for most strategies (fast, reproducible).
- Event-driven components only where required (options payoffs, roll schedules, market-making toys).
- Standard output artifact per run:
  - metrics JSON (`sharpe`, `cagr`, `vol`, `maxdd`, turnover, exposure, etc.)
  - equity curve CSV/Parquet
  - configuration + dataset fingerprints

**Reporting**
- `docs/results/` (generated; git-ignored) with summary tables and plots.
- A single “leaderboard” report that can be regenerated end-to-end.

## Strategy Implementation Workflow (Repeatable)

For each paper strategy:
1) **Extract**: capture the paper reference (`section`, `title`) and the minimal formal definition.
2) **Decide data requirements**:
   - instruments/universe
   - frequency (daily vs intraday)
   - required fields (prices, volume, fundamentals, rates, options Greeks, etc.)
3) **Encode a spec** in `strategies/ssrn-3247865.yaml`:
   - `id`, `name`, `paper.section`
   - `asset_class`, `universe`, `rebalance`
   - parameters with defaults (and allowed ranges)
4) **Implement** the strategy in code:
   - signal generation
   - portfolio construction (weights, constraints, scaling)
5) **Validate**:
   - unit tests for formula correctness (toy examples)
   - sanity checks: turnover, exposure, NaN handling, rebalancing timing
6) **Backtest**:
   - fixed “default” run (documented)
   - optional parameter sweeps (separate, clearly labeled to avoid p-hacking)
7) **Document**:
   - what data is used
   - what assumptions are made
   - what is likely to break in real trading

## Default Backtest Assumptions (Initial)

These defaults keep results comparable; they can be overridden per strategy:
- Frequency: daily close-to-close.
- Execution: signal computed at `t`, applied at `t+1` (1-day lag).
- Costs (phase 1): zero costs, then add realistic costs in phase 2.
- Cash return: 0% (phase 1), then use risk-free series in phase 2.
- Survivorship: avoid survivorship bias where possible (Sharadar can help).

## Benchmarks

Define standard benchmarks per group:
- Equity/ETF strategies: buy & hold SPY (or region-appropriate ETF), and cash.
- Sector rotation: SPY and equal-weight sector basket.
- Multi-asset: a fixed 60/40 proxy and equal-weight risk parity proxy (documented).

## Metrics (Risk-Adjusted)

Compute at least:
- CAGR, annualized volatility
- Sharpe (and optionally Sortino)
- Max drawdown, drawdown duration
- Turnover, average exposure, hit rate
- Optional: regression vs benchmark (alpha/beta), information ratio

## Parameter Governance

To keep the repo publishable and credible:
- Maintain a “default parameters” table (one row per strategy).
- Any parameter sweep must be labeled as such and separated from the default leaderboard.
- Prefer **walk-forward** or **train/validation/test** splits for strategies that require optimization.

## Milestones

**M0: Backtest framework**
- Stable data interfaces
- Strategy spec schema + validation
- Reproducible run artifacts

**M1: Strategies feasible with ETFs**
- Implement ETF-proxy versions of stock/sector/multi-asset strategies (fast coverage)

**M2: Sharadar equity universes**
- Price momentum / value / low-volatility / earnings-momentum using point-in-time fundamentals
- Universe filters: liquidity, price, minimum history

**M3: Specialized asset classes**
- Options strategies (needs options data)
- Futures carry/roll (needs futures curves)
- FX carry (needs spot + rates)

**M4: Remaining “conceptual” strategies**
- Mark as `blocked`/`not-applicable` with a clear explanation and what data would be needed

## Current Status (2026-01-21)

Implemented (Sharadar-only; long-only backtests):
- Data connectors: Sharadar `SFP` (ETFs), `SEP` (equities), `DAILY` (valuation metrics), and `TICKERS` (metadata).
- Universe: `sharadar_us_equities_liquid` (static liquidity screen; cached) for US equity cross-sectional strategies.
- Strategy coverage added beyond ETF proxies:
  - `3.1` cross-sectional momentum (US equities)
  - `3.3` value (US equities; low `pe` by default)
  - `3.4` low-volatility (US equities)
  - `3.6` multifactor (momentum + value + low-vol)
  - `3.7` residual momentum (US equities vs SPY)
- Regenerable report: `docs/RESULTS_since_2005.md` via:
  - `paper-strategy-lab leaderboard strategies/ssrn-3247865.yaml --start 2005-01-01 --out-md docs/RESULTS_since_2005.md`
- Coverage matrix: `docs/COVERAGE.md` (generated from extracted section headings + current YAML/specs).

## Next Tranche (Maximize Paper Coverage With Sharadar)

Goal: cover as many remaining **equity** strategies in sections `3.*` (and equity-adjacent parts of `4.*`) as possible using only Sharadar (`SEP` + `DAILY` + `TICKERS` + `SFP`).

High-impact next steps:
- Make the equity universe **point-in-time** (monthly reconstitution, rolling ADV screen, minimum history) to reduce lookahead bias.
- Add **earnings momentum** (`3.2`) if feasible:
  - likely requires Sharadar `SF1` (fundamentals) or an equivalent point-in-time earnings dataset.
- Implement **pairs trading** (`3.8`) variants feasible with daily prices:
  - candidate approaches: correlation/cointegration pre-screen, z-score spread mean reversion, dollar-neutral constraints (if/when we support net exposure constraints).
- Expand factor inputs for **value** and **quality** (where described in the paper) if available in `DAILY`:
  - e.g. `pb`, `ps`, `ev/ebitda`, `marketcap` screens, etc.
- Add equity **sector/industry** universes (if reliably encoded in Sharadar metadata) to support additional rotation/cluster strategies.

Documented gaps:
- Options sections (`2.*`, `7.*`) need options chains/IV surfaces.
- Futures/FX carry/curve sections need futures curves + rates.
- Credit/OTC/institutional strategies are expected to remain `blocked` without specialized data.

## Public GitHub Checklist

- Keep `data/` and PDFs out of git (already ignored).
- Add a clear license for code (choose later).
- Add a citation section for the paper + disclaimer (“research/education only”).
- Keep `docs/COVERAGE.md` current (regenerate via `python scripts/generate_coverage.py`).
- Add a `CONTRIBUTING.md` with:
  - data sources are user-provided
  - no PRs that add datasets or vendor files
