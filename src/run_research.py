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
    print(f"Entries: {int(halftrend['buy_signal'].sum()):,}")
    print(f"Exits: {int(halftrend['sell_signal'].sum()):,}")
    print(f"Completed trades: {len(trade_results):,}")

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

    return backtest


if __name__ == "__main__":
    run_is_research()