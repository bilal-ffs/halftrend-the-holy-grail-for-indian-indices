import json
from pathlib import Path

import pandas as pd

from src.backtest import run_backtest
from src.data import load_minute_data, resample_to_15m
from src.halftrend import calculate_halftrend
from src.portfolio import build_equity_curve, equity_to_returns
from src.research import split_is_oos
from src.trading import generate_long_only_trades


DATA_PATH = (
    r"C:\Users\beqmd\Documents\QuantResearch"
    r"\data\NIFTY_50_minute.csv"
)

RESULTS_DIR = Path("results")


def run_is_research():
    # --------------------------------------------------------------
    # Load and resample raw data.
    # --------------------------------------------------------------
    minute_data = load_minute_data(DATA_PATH)
    data_15m = resample_to_15m(minute_data)

    # --------------------------------------------------------------
    # Fixed IS/OOS split.
    #
    # OOS is deliberately not processed further in this runner.
    # --------------------------------------------------------------
    is_data, _ = split_is_oos(data_15m)

    # --------------------------------------------------------------
    # Calculate HalfTrend only on IS data.
    # --------------------------------------------------------------
    halftrend = calculate_halftrend(is_data)

    # --------------------------------------------------------------
    # Generate long-only trades.
    # --------------------------------------------------------------
    positions, trade_results = generate_long_only_trades(
        halftrend
    )

    # --------------------------------------------------------------
    # Build portfolio equity and periodic returns.
    # --------------------------------------------------------------
    equity = build_equity_curve(
        halftrend,
        initial_capital=100_000.0,
    )

    returns = equity_to_returns(equity)

    # --------------------------------------------------------------
    # QuantTools-backed research report.
    # --------------------------------------------------------------
    backtest = run_backtest(
        df=halftrend,
        equity=equity,
        returns=returns,
        trade_results=trade_results,
    )

    # --------------------------------------------------------------
    # Create results directory.
    # --------------------------------------------------------------
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------------
    # Save performance summary.
    # --------------------------------------------------------------
    summary_path = RESULTS_DIR / "halftrend_is_summary.json"

    summary_path.write_text(
        json.dumps(
            backtest.summary(),
            indent=4,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------------
    # Save equity curve and periodic returns.
    # --------------------------------------------------------------
    equity_output = pd.DataFrame(
        {
            "equity": equity,
            "strategy_return": returns,
        }
    )

    equity_output.to_csv(
        RESULTS_DIR / "halftrend_is_equity.csv"
    )

    # --------------------------------------------------------------
    # Save completed trade P&Ls.
    # --------------------------------------------------------------
    trade_results.to_csv(
        RESULTS_DIR / "halftrend_is_trades.csv",
        index=False,
    )

    # --------------------------------------------------------------
    # Console report.
    # --------------------------------------------------------------
    print()
    print("=" * 60)
    print("HALFTREND — IN-SAMPLE RESEARCH")
    print("=" * 60)
    print()

    print(
        f"Period: "
        f"{is_data.index.min()} → {is_data.index.max()}"
    )

    print(f"Bars: {len(is_data):,}")
    print(
        f"Entries: "
        f"{int(halftrend['buy_signal'].sum()):,}"
    )
    print(
        f"Exits: "
        f"{int(halftrend['sell_signal'].sum()):,}"
    )
    print(
        f"Completed trades: "
        f"{len(trade_results):,}"
    )

    print(
        f"Time in market: "
        f"{positions.mean() * 100:.2f}%"
    )

    print()
    print("Performance")
    print("-" * 60)

    print(
        backtest.to_dataframe().to_string(
            index=False
        )
    )

    print()
    print("Final equity:")
    print(f"₹{equity.iloc[-1]:,.2f}")

    print()
    print("Saved results:")
    print(
        f"  {RESULTS_DIR / 'halftrend_is_summary.json'}"
    )
    print(
        f"  {RESULTS_DIR / 'halftrend_is_equity.csv'}"
    )
    print(
        f"  {RESULTS_DIR / 'halftrend_is_trades.csv'}"
    )

    return backtest


if __name__ == "__main__":
    run_is_research()