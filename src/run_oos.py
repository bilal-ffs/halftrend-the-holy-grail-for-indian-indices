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


def run_oos_research():
    # --------------------------------------------------------------
    # Load and resample the complete dataset.
    # --------------------------------------------------------------
    minute_data = load_minute_data(DATA_PATH)
    data_15m = resample_to_15m(minute_data)

    # --------------------------------------------------------------
    # Obtain the fixed OOS window.
    # --------------------------------------------------------------
    _, oos_data = split_is_oos(data_15m)

    # --------------------------------------------------------------
    # Calculate HalfTrend on the complete historical dataset.
    #
    # This preserves the state of the indicator at the OOS boundary.
    # No parameters are fitted or changed during OOS.
    # --------------------------------------------------------------
    halftrend_full = calculate_halftrend(data_15m)

    # --------------------------------------------------------------
    # Restrict evaluation to OOS bars only.
    # --------------------------------------------------------------
    halftrend = halftrend_full.loc[oos_data.index].copy()

    # --------------------------------------------------------------
    # Generate OOS trades.
    # --------------------------------------------------------------
    positions, trade_results = generate_long_only_trades(
        halftrend
    )

    # --------------------------------------------------------------
    # Build OOS equity and returns.
    # --------------------------------------------------------------
    equity = build_equity_curve(
        halftrend,
        initial_capital=100_000.0,
    )

    returns = equity_to_returns(equity)

    # --------------------------------------------------------------
    # Backtest analytics.
    # --------------------------------------------------------------
    backtest = run_backtest(
        df=halftrend,
        equity=equity,
        returns=returns,
        trade_results=trade_results,
    )

    # --------------------------------------------------------------
    # Save OOS artifacts.
    # --------------------------------------------------------------
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = (
        RESULTS_DIR / "halftrend_oos_summary.json"
    )

    summary_path.write_text(
        json.dumps(
            backtest.summary(),
            indent=4,
        ),
        encoding="utf-8",
    )

    equity_output = pd.DataFrame(
        {
            "equity": equity,
            "strategy_return": returns,
        }
    )

    equity_output.to_csv(
        RESULTS_DIR / "halftrend_oos_equity.csv"
    )

    trade_results.to_csv(
        RESULTS_DIR / "halftrend_oos_trades.csv",
        index=False,
    )

    # --------------------------------------------------------------
    # Console report.
    # --------------------------------------------------------------
    print()
    print("=" * 60)
    print("HALFTREND — OUT-OF-SAMPLE RESEARCH")
    print("=" * 60)
    print()

    print(
        f"Period: "
        f"{oos_data.index.min()} → {oos_data.index.max()}"
    )

    print(f"Bars: {len(oos_data):,}")

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
        f"  {RESULTS_DIR / 'halftrend_oos_summary.json'}"
    )
    print(
        f"  {RESULTS_DIR / 'halftrend_oos_equity.csv'}"
    )
    print(
        f"  {RESULTS_DIR / 'halftrend_oos_trades.csv'}"
    )

    return backtest


if __name__ == "__main__":
    run_oos_research()