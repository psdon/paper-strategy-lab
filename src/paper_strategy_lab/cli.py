from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from paper_strategy_lab.backtest.metrics import (
    annualized_return,
    annualized_volatility,
    max_drawdown,
    sharpe_ratio,
)
from paper_strategy_lab.backtest.portfolio import run_portfolio_backtest
from paper_strategy_lab.data_sources.sharadar import load_prices
from paper_strategy_lab.pdf_text import extract_pages
from paper_strategy_lab.strategies.runner import run_strategy_weights
from paper_strategy_lab.strategies.yaml_loader import load_strategy_specs
from paper_strategy_lab.strategy_candidates import extract_candidates_from_pages_jsonl

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


@app.command("extract-text")
def extract_text(
    pdf: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(..., "--out", dir_okay=False),
) -> None:
    """
    Extract per-page text from a PDF into JSONL: {"page_index": int, "text": str}.
    """
    out.parent.mkdir(parents=True, exist_ok=True)

    pages = extract_pages(pdf)
    with out.open("w", encoding="utf-8") as f:
        for page in pages:
            f.write(
                json.dumps({"page_index": page.page_index, "text": page.text}, ensure_ascii=False)
            )
            f.write("\n")

    console.print(f"Wrote {len(pages)} pages -> {out}")


@app.command("extract-strategy-candidates")
def extract_strategy_candidates(
    pages_jsonl: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(..., "--out", dir_okay=False),
) -> None:
    """
    Heuristically extract likely strategy blocks from extracted page text.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    candidates = extract_candidates_from_pages_jsonl(pages_jsonl)

    with out.open("w", encoding="utf-8") as f:
        for c in candidates:
            f.write(
                json.dumps(
                    {
                        "page_index": c.page_index,
                        "start_line": c.start_line,
                        "end_line": c.end_line,
                        "title_hint": c.title_hint,
                        "snippet": c.snippet,
                    },
                    ensure_ascii=False,
                )
            )
            f.write("\n")

    console.print(f"Wrote {len(candidates)} candidates -> {out}")


@app.command("list-strategies")
def list_strategies(
    spec: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    limit: int | None = typer.Option(None, "--limit", min=1),
) -> None:
    """
    List YAML-defined strategies (once you encode them from the paper).
    """
    strategies = load_strategy_specs(spec)
    if limit is not None:
        strategies = strategies[:limit]

    table = Table(title=f"Strategies: {spec.name}")
    table.add_column("paper", style="magenta", no_wrap=True)
    table.add_column("id", style="cyan", no_wrap=True)
    table.add_column("name", style="bold")
    table.add_column("kind")
    table.add_column("description")
    for s in strategies:
        paper = s.paper_section or ""
        table.add_row(paper, s.id, s.name, s.kind, s.description or "")

    console.print(table)


@app.command("backtest")
def backtest(
    spec: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    strategy_id: str = typer.Argument(...),
    years: int = typer.Option(5, "--years", min=1),
    start: str | None = typer.Option(None, "--start", help="YYYY-MM-DD (overrides --years)"),
    end: str | None = typer.Option(None, "--end", help="YYYY-MM-DD"),
    fee_bps: float = typer.Option(0.0, "--fee-bps", min=0.0),
    slippage_bps: float = typer.Option(0.0, "--slippage-bps", min=0.0),
) -> None:
    """
    Run a long-only portfolio backtest for a YAML-defined strategy using Sharadar prices.
    """
    try:
        strategies = load_strategy_specs(spec)
        selected = next(s for s in strategies if s.id == strategy_id)
    except StopIteration:
        raise typer.BadParameter(f"Unknown strategy_id={strategy_id!r}") from None

    if not selected.universe:
        raise typer.BadParameter(f"Strategy {selected.id!r} missing universe.tickers")

    try:
        prices = load_prices(selected.universe, start=start, end=end)
        if prices.empty:
            raise typer.BadParameter(f"No prices found for {selected.universe}")

        if start is None:
            # Trailing N trading days window; use a simple 252*years convention.
            n = 252 * years
            if len(prices) > n:
                prices = prices.iloc[-n:]

        weights = run_strategy_weights(prices=prices, spec=selected)
        result = run_portfolio_backtest(
            prices=prices, weights=weights, fee_bps=fee_bps, slippage_bps=slippage_bps
        )
    except ImportError:
        console.print(
            "Missing deps. Install with: `uv sync --all-extras` "
            "(or `uv pip install -e '.[analysis,dev]'`)."
        )
        raise typer.Exit(code=1) from None

    cagr = annualized_return(result.daily_returns)
    vol = annualized_volatility(result.daily_returns)
    sharpe = sharpe_ratio(result.daily_returns)
    mdd = max_drawdown(result.equity_curve)

    universe = ",".join(selected.universe)
    table = Table(title=f"Backtest: {selected.id} ({universe})")
    table.add_column("metric", style="cyan", no_wrap=True)
    table.add_column("value", style="bold")
    table.add_row("CAGR", f"{cagr:.2%}")
    table.add_row("Vol", f"{vol:.2%}")
    table.add_row("Sharpe", f"{sharpe:.2f}")
    table.add_row("Max drawdown", f"{mdd:.2%}")
    console.print(table)


@app.command("leaderboard")
def leaderboard(
    spec: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    years: int = typer.Option(5, "--years", min=1),
    start: str | None = typer.Option(None, "--start", help="YYYY-MM-DD (overrides --years)"),
    end: str | None = typer.Option(None, "--end", help="YYYY-MM-DD"),
    fee_bps: float = typer.Option(0.0, "--fee-bps", min=0.0),
    slippage_bps: float = typer.Option(0.0, "--slippage-bps", min=0.0),
    out_csv: Path | None = typer.Option(None, "--out-csv", dir_okay=False),
) -> None:
    """
    Backtest all strategies in a spec file and print a Sharpe-ranked leaderboard.
    """
    try:
        import pandas as pd
    except ImportError:
        console.print("Missing deps. Install with: `uv sync --all-extras`.")
        raise typer.Exit(code=1) from None

    specs = load_strategy_specs(spec)
    all_tickers = sorted({t for s in specs for t in s.universe})
    if not all_tickers:
        raise typer.BadParameter("No universe.tickers found in the spec file.")

    prices = load_prices(all_tickers, start=start, end=end)
    if prices.empty:
        raise typer.BadParameter(f"No prices found for tickers: {all_tickers}")

    if start is None:
        n = 252 * years
        if len(prices) > n:
            prices = prices.iloc[-n:]

    rows: list[dict[str, object]] = []
    for s in specs:
        px = prices.reindex(columns=s.universe).dropna(how="all")
        if px.empty:
            continue
        w = run_strategy_weights(prices=px, spec=s)
        bt = run_portfolio_backtest(
            prices=px, weights=w, fee_bps=fee_bps, slippage_bps=slippage_bps
        )
        rows.append(
            {
                "paper_section": s.paper_section or "",
                "id": s.id,
                "name": s.name,
                "kind": s.kind,
                "universe": ",".join(s.universe),
                "sharpe": sharpe_ratio(bt.daily_returns),
                "cagr": annualized_return(bt.daily_returns),
                "vol": annualized_volatility(bt.daily_returns),
                "maxdd": max_drawdown(bt.equity_curve),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        console.print("No strategies produced results (check universe/tickers).")
        raise typer.Exit(code=1)

    df = df.sort_values("sharpe", ascending=False)

    table = Table(title=f"Leaderboard: {spec.name}")
    for col in ["paper_section", "id", "sharpe", "cagr", "vol", "maxdd", "universe"]:
        table.add_column(col)
    for _, r in df.iterrows():
        table.add_row(
            str(r["paper_section"]),
            str(r["id"]),
            f"{float(r['sharpe']):.2f}",
            f"{float(r['cagr']):.2%}",
            f"{float(r['vol']):.2%}",
            f"{float(r['maxdd']):.2%}",
            str(r["universe"]),
        )
    console.print(table)

    if out_csv is not None:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
        console.print(f"Wrote {len(df)} rows -> {out_csv}")
