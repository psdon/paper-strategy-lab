from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from paper_strategy_lab.backtest.metrics import (
    annualized_return,
    annualized_volatility,
    calmar_ratio,
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
)
from paper_strategy_lab.backtest.portfolio import run_portfolio_backtest
from paper_strategy_lab.data_sources.sharadar import (
    load_daily_metrics,
    load_equity_prices,
    load_prices,
)
from paper_strategy_lab.market_data import MarketData
from paper_strategy_lab.pdf_text import extract_pages
from paper_strategy_lab.strategies.runner import run_strategy_weights
from paper_strategy_lab.strategies.yaml_loader import load_strategy_specs
from paper_strategy_lab.strategy_candidates import extract_candidates_from_pages_jsonl
from paper_strategy_lab.universe.sharadar_universe import build_us_equities_liquid

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
    table.add_column("universe")
    table.add_column("description")
    for s in strategies:
        paper = s.paper_section or ""
        universe = ",".join(s.universe) if s.universe else (s.universe_type or "")
        table.add_row(paper, s.id, s.name, s.kind, universe, s.description or "")

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

    if not selected.universe and not selected.universe_type:
        raise typer.BadParameter(f"Strategy {selected.id!r} missing universe")

    try:
        tickers = selected.universe
        if not tickers and selected.universe_type == "sharadar_us_equities_liquid":
            tickers = build_us_equities_liquid(
                start=start,
                end=end,
                max_tickers=int(selected.universe_config.get("max_tickers", 500)),
                min_price=float(selected.universe_config.get("min_price", 5.0)),
                exchanges=list(selected.universe_config.get("exchanges", ["NYSE", "NASDAQ"])),
            )

        prices = (
            load_equity_prices(tickers, start=start, end=end)
            if selected.universe_type == "sharadar_us_equities_liquid"
            else load_prices(tickers, start=start, end=end)
        )
        if prices.empty:
            raise typer.BadParameter(f"No prices found for {tickers}")

        if start is None:
            # Trailing N trading days window; use a simple 252*years convention.
            n = 252 * years
            if len(prices) > n:
                prices = prices.iloc[-n:]

        features = {}
        if selected.kind in {"equity_value", "equity_multifactor"}:
            value_field = str(selected.params.get("value_field", "pe"))
            features[value_field] = load_daily_metrics(
                tickers, fields=[value_field], start=start, end=end
            )[value_field].reindex(prices.index).ffill()
        if selected.kind == "equity_residual_momentum":
            features["benchmark_spy"] = load_prices(["SPY"], start=start, end=end).reindex(
                prices.index
            )

        weights = run_strategy_weights(
            data=MarketData(prices=prices, features=features), spec=selected
        )
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
    sortino = sortino_ratio(result.daily_returns)
    calmar = calmar_ratio(result.daily_returns)
    mdd = max_drawdown(result.equity_curve)

    universe = (
        ",".join(selected.universe)
        if selected.universe
        else f"{selected.universe_type}(n={len(tickers)})"
    )
    table = Table(title=f"Backtest: {selected.id} ({universe})")
    table.add_column("metric", style="cyan", no_wrap=True)
    table.add_column("value", style="bold")
    table.add_row("CAGR", f"{cagr:.2%}")
    table.add_row("Vol", f"{vol:.2%}")
    table.add_row("Sharpe", f"{sharpe:.2f}")
    table.add_row("Sortino", f"{sortino:.2f}")
    table.add_row("Calmar", f"{calmar:.2f}")
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
    out_md: Path | None = typer.Option(None, "--out-md", dir_okay=False),
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

    bench_px_full = load_prices(["SPY"], start=start, end=end).dropna()

    universe_cache: dict[tuple[object, ...], list[str]] = {}
    prices_cache: dict[tuple[object, ...], pd.DataFrame] = {}
    daily_cache: dict[tuple[object, ...], pd.DataFrame] = {}

    rows: list[dict[str, object]] = []
    for s in specs:
        tickers = s.universe
        if not tickers and s.universe_type == "sharadar_us_equities_liquid":
            universe_key = (
                s.universe_type,
                start or "",
                end or "",
                int(s.universe_config.get("max_tickers", 500)),
                float(s.universe_config.get("min_price", 5.0)),
                tuple(s.universe_config.get("exchanges", ["NYSE", "NASDAQ"])),
            )
            cached_universe = universe_cache.get(universe_key)
            if cached_universe is None:
                cached_universe = build_us_equities_liquid(
                    start=start,
                    end=end,
                    max_tickers=int(s.universe_config.get("max_tickers", 500)),
                    min_price=float(s.universe_config.get("min_price", 5.0)),
                    exchanges=list(s.universe_config.get("exchanges", ["NYSE", "NASDAQ"])),
                )
                universe_cache[universe_key] = cached_universe
            tickers = cached_universe

        if not tickers:
            continue

        if s.universe_type == "sharadar_us_equities_liquid":
            px_key = ("equity_px", start or "", end or "", tuple(tickers))
            cached_px = prices_cache.get(px_key)
            if cached_px is None:
                cached_px = load_equity_prices(tickers, start=start, end=end)
                prices_cache[px_key] = cached_px
            px_full = cached_px
        else:
            px_full = load_prices(tickers, start=start, end=end)

        if px_full.empty:
            continue

        if start is None:
            n = 252 * years
            if len(px_full) > n:
                px_full = px_full.iloc[-n:]

        px_full = px_full.sort_index().dropna(how="all")
        px_full = px_full.dropna(axis=1, how="all")
        if px_full.empty:
            continue
        common_index = px_full.index.intersection(bench_px_full.index)
        if len(common_index) < 252:
            continue

        px = px_full.loc[common_index]
        bench_px = bench_px_full.loc[common_index]

        features = {}
        if s.kind in {"equity_value", "equity_multifactor"}:
            value_field = str(s.params.get("value_field", "pe"))
            daily_key = ("daily", value_field, start or "", end or "", tuple(tickers))
            daily = daily_cache.get(daily_key)
            if daily is None:
                daily = load_daily_metrics(tickers, fields=[value_field], start=start, end=end)[
                    value_field
                ]
                daily_cache[daily_key] = daily
            features[value_field] = daily.reindex(px.index).ffill()
        if s.kind == "equity_residual_momentum":
            features["benchmark_spy"] = bench_px.reindex(px.index)

        w = run_strategy_weights(data=MarketData(prices=px, features=features), spec=s)
        avg_exposure = float(w.shift(1).fillna(0.0).sum(axis=1).mean())

        bt = run_portfolio_backtest(
            prices=px,
            weights=w,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
        )
        avg_turnover = float(bt.turnover.mean()) if len(bt.turnover) else 0.0

        bench_w = pd.DataFrame(1.0, index=bench_px.index, columns=bench_px.columns)
        bench_bt = run_portfolio_backtest(
            prices=bench_px,
            weights=bench_w,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
        )
        bench_sharpe = sharpe_ratio(bench_bt.daily_returns)
        bench_sortino = sortino_ratio(bench_bt.daily_returns)
        bench_calmar = calmar_ratio(bench_bt.daily_returns)
        bench_cagr = annualized_return(bench_bt.daily_returns)
        bench_vol = annualized_volatility(bench_bt.daily_returns)
        bench_maxdd = max_drawdown(bench_bt.equity_curve)

        strat_sharpe = sharpe_ratio(bt.daily_returns)
        strat_sortino = sortino_ratio(bt.daily_returns)
        strat_calmar = calmar_ratio(bt.daily_returns)
        strat_cagr = annualized_return(bt.daily_returns)
        strat_vol = annualized_volatility(bt.daily_returns)
        strat_maxdd = max_drawdown(bt.equity_curve)

        rows.append(
            {
                "paper_section": s.paper_section or "",
                "id": s.id,
                "name": s.name,
                "kind": s.kind,
                "universe": (
                    ",".join(s.universe)
                    if s.universe
                    else f"{s.universe_type}(n={len(tickers)})"
                ),
                "start_date": str(px.index.min())[:10],
                "end_date": str(px.index.max())[:10],
                "days": int(len(px)),
                "sharpe": strat_sharpe,
                "sortino": strat_sortino,
                "calmar": strat_calmar,
                "cagr": strat_cagr,
                "vol": strat_vol,
                "maxdd": strat_maxdd,
                "avg_exposure": avg_exposure,
                "avg_turnover": avg_turnover,
                "bench_id": "bh-spy",
                "bench_sharpe": bench_sharpe,
                "bench_sortino": bench_sortino,
                "bench_calmar": bench_calmar,
                "bench_cagr": bench_cagr,
                "bench_vol": bench_vol,
                "bench_maxdd": bench_maxdd,
                "sharpe_vs_bh": strat_sharpe - bench_sharpe,
                "sortino_vs_bh": strat_sortino - bench_sortino,
                "calmar_vs_bh": strat_calmar - bench_calmar,
                "cagr_vs_bh": strat_cagr - bench_cagr,
                "maxdd_vs_bh": strat_maxdd - bench_maxdd,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        console.print("No strategies produced results (check universe/tickers).")
        raise typer.Exit(code=1)

    df = df.sort_values("sharpe", ascending=False)

    table = Table(title=f"Leaderboard: {spec.name}")
    table_cols = [
        "paper_section",
        "id",
        "sharpe",
        "sortino",
        "calmar",
        "cagr",
        "vol",
        "maxdd",
        "sharpe_vs_bh",
        "avg_exposure",
        "avg_turnover",
    ]
    for col in table_cols:
        table.add_column(col)
    for _, r in df.iterrows():
        table.add_row(
            str(r["paper_section"]),
            str(r["id"]),
            f"{float(r['sharpe']):.2f}",
            f"{float(r['sortino']):.2f}",
            f"{float(r['calmar']):.2f}",
            f"{float(r['cagr']):.2%}",
            f"{float(r['vol']):.2%}",
            f"{float(r['maxdd']):.2%}",
            f"{float(r['sharpe_vs_bh']):+.2f}",
            f"{float(r['avg_exposure']):.2f}",
            f"{float(r['avg_turnover']):.2f}",
        )
    console.print(table)

    if out_csv is not None:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
        console.print(f"Wrote {len(df)} rows -> {out_csv}")

    if out_md is not None:
        from datetime import datetime

        cols = [
            "paper_section",
            "id",
            "name",
            "kind",
            "universe",
            "start_date",
            "end_date",
            "days",
            "sharpe",
            "sortino",
            "calmar",
            "cagr",
            "vol",
            "maxdd",
            "avg_exposure",
            "avg_turnover",
            "bench_id",
            "bench_sharpe",
            "bench_sortino",
            "bench_calmar",
            "bench_cagr",
            "bench_vol",
            "bench_maxdd",
            "sharpe_vs_bh",
            "sortino_vs_bh",
            "calmar_vs_bh",
            "cagr_vs_bh",
            "maxdd_vs_bh",
        ]

        fmt = df.copy()
        fmt["sharpe"] = fmt["sharpe"].map(lambda x: f"{float(x):.2f}")
        fmt["sortino"] = fmt["sortino"].map(lambda x: f"{float(x):.2f}")
        fmt["calmar"] = fmt["calmar"].map(lambda x: f"{float(x):.2f}")
        fmt["cagr"] = fmt["cagr"].map(lambda x: f"{float(x):.2%}")
        fmt["vol"] = fmt["vol"].map(lambda x: f"{float(x):.2%}")
        fmt["maxdd"] = fmt["maxdd"].map(lambda x: f"{float(x):.2%}")
        fmt["avg_exposure"] = fmt["avg_exposure"].map(lambda x: f"{float(x):.2f}")
        fmt["avg_turnover"] = fmt["avg_turnover"].map(lambda x: f"{float(x):.2f}")
        fmt["bench_sharpe"] = fmt["bench_sharpe"].map(lambda x: f"{float(x):.2f}")
        fmt["bench_sortino"] = fmt["bench_sortino"].map(lambda x: f"{float(x):.2f}")
        fmt["bench_calmar"] = fmt["bench_calmar"].map(lambda x: f"{float(x):.2f}")
        fmt["bench_cagr"] = fmt["bench_cagr"].map(lambda x: f"{float(x):.2%}")
        fmt["bench_vol"] = fmt["bench_vol"].map(lambda x: f"{float(x):.2%}")
        fmt["bench_maxdd"] = fmt["bench_maxdd"].map(lambda x: f"{float(x):.2%}")
        fmt["sharpe_vs_bh"] = fmt["sharpe_vs_bh"].map(lambda x: f"{float(x):+.2f}")
        fmt["sortino_vs_bh"] = fmt["sortino_vs_bh"].map(lambda x: f"{float(x):+.2f}")
        fmt["calmar_vs_bh"] = fmt["calmar_vs_bh"].map(lambda x: f"{float(x):+.2f}")
        fmt["cagr_vs_bh"] = fmt["cagr_vs_bh"].map(lambda x: f"{float(x):+.2%}")
        fmt["maxdd_vs_bh"] = fmt["maxdd_vs_bh"].map(lambda x: f"{float(x):+.2%}")

        header = "| " + " | ".join(cols) + " |"
        sep = "|" + "|".join(["---"] * len(cols)) + "|"
        lines = [header, sep]
        for _, row in fmt[cols].iterrows():
            lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md_lines: list[str] = []
        md_lines.append("# Results")
        md_lines.append("")
        md_lines.append(f"Generated: `{now}`")
        md_lines.append("")
        md_lines.append("## Inputs & Assumptions")
        md_lines.append("")
        md_lines.append(
            "- Data: Sharadar (SFP/SEP/DAILY as needed) via `SHARADAR_DIR` or `data/sharadar` "
            "symlink."
        )
        if start:
            md_lines.append(f"- Window: start=`{start}`" + (f", end=`{end}`" if end else ""))
        else:
            md_lines.append(f"- Window: trailing `{years}` years (≈ `{252 * years}` trading days)")
        md_lines.append("- Frequency: daily close-to-close; positions applied with a 1-day lag.")
        md_lines.append(
            f"- Costs: fee={fee_bps} bps, slippage={slippage_bps} bps (applied to turnover)."
        )
        md_lines.append("")
        md_lines.append("## Leaderboard (Sharpe-ranked)")
        md_lines.append("")
        md_lines.extend(lines)
        md_lines.append("")

        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text("\n".join(md_lines), encoding="utf-8")
        console.print(f"Wrote {len(df)} rows -> {out_md}")
