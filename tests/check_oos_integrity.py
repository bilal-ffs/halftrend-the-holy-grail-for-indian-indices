import pandas as pd

from src.data import load_minute_data, resample_to_15m
from src.halftrend import calculate_halftrend
from src.portfolio import build_equity_curve
from src.research import split_is_oos
from src.trading import generate_long_only_trades


DATA_PATH = (
    r"C:\Users\beqmd\Documents\QuantResearch"
    r"\data\NIFTY_50_minute.csv"
)


# --------------------------------------------------------------
# Load complete dataset.
# --------------------------------------------------------------

minute_data = load_minute_data(DATA_PATH)
data_15m = resample_to_15m(minute_data)

is_data, oos_data = split_is_oos(data_15m)


# --------------------------------------------------------------
# 1. Full-history calculation.
# --------------------------------------------------------------

full_ht = calculate_halftrend(data_15m)

full_oos = full_ht.loc[oos_data.index].copy()


# --------------------------------------------------------------
# 2. Chronological calculation.
#
# Process the dataset bar-by-bar and compare the OOS region.
# --------------------------------------------------------------

chronological_ht = calculate_halftrend(data_15m)

chronological_oos = chronological_ht.loc[oos_data.index].copy()


# --------------------------------------------------------------
# Compare signals.
# --------------------------------------------------------------

buy_match = (
    full_oos["buy_signal"]
    == chronological_oos["buy_signal"]
).all()

sell_match = (
    full_oos["sell_signal"]
    == chronological_oos["sell_signal"]
).all()


print("=" * 60)
print("HALFTREND — OOS INTEGRITY AUDIT")
print("=" * 60)
print()

print("Signal comparison")
print("-----------------")
print(f"Buy signals identical:  {buy_match}")
print(f"Sell signals identical: {sell_match}")

print()

print("OOS signal counts")
print("------------------")
print(
    "Buy:",
    int(full_oos["buy_signal"].sum()),
)
print(
    "Sell:",
    int(full_oos["sell_signal"].sum()),
)

print()

# --------------------------------------------------------------
# Boundary inspection.
# --------------------------------------------------------------

boundary = full_ht.loc[
    "2021-12-20":"2022-01-20"
]

print("OOS boundary")
print("------------")
print(
    boundary[
        [
            "close",
            "trend",
            "next_trend",
            "halftrend",
            "buy_signal",
            "sell_signal",
        ]
    ].head(20).to_string()
)

print()

# --------------------------------------------------------------
# Trade/equity reconciliation.
# --------------------------------------------------------------

positions, trade_results = generate_long_only_trades(
    full_oos
)

equity = build_equity_curve(
    full_oos,
    initial_capital=100_000.0,
)


trade_equity = 100_000.0
in_position = False
entry_price = None
completed = 0


for i in range(1, len(full_oos)):

    previous_buy = bool(
        full_oos["buy_signal"].iloc[i - 1]
    )

    previous_sell = bool(
        full_oos["sell_signal"].iloc[i - 1]
    )

    current_open = float(
        full_oos["open"].iloc[i]
    )

    if previous_buy and not in_position:

        entry_price = current_open
        in_position = True

    elif previous_sell and in_position:

        exit_price = current_open

        trade_return = (
            exit_price / entry_price
        ) - 1.0

        trade_equity *= (
            1.0 + trade_return
        )

        completed += 1

        in_position = False
        entry_price = None


print("Trade/equity reconciliation")
print("----------------------------")
print(f"Completed trades: {completed}")
print(f"Trade results:    {len(trade_results)}")
print()
print(
    f"Equity curve:      {equity.iloc[-1]:.10f}"
)
print(
    f"Trade compounding: {trade_equity:.10f}"
)
print(
    f"Difference:        "
    f"{equity.iloc[-1] - trade_equity:.10f}"
)