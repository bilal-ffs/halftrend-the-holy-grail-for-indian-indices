from src.data import load_minute_data, resample_to_15m
from src.halftrend import calculate_halftrend
from src.trading import generate_long_only_trades


DATA_PATH = (
    r"C:\Users\beqmd\Documents\QuantResearch"
    r"\data\NIFTY_50_minute.csv"
)


df = load_minute_data(DATA_PATH)
df15 = resample_to_15m(df).iloc[:1000]

ht = calculate_halftrend(df15)

positions, trades = generate_long_only_trades(ht)

in_position = False
entry_time = None
entry_price = None
trade_number = 0

print("Signal → execution check:")
print()

for i in range(1, len(ht)):
    if ht["buy_signal"].iloc[i - 1] and not in_position:
        entry_time = ht.index[i]
        entry_price = ht["open"].iloc[i]
        in_position = True

    elif ht["sell_signal"].iloc[i - 1] and in_position:
        trade_number += 1

        exit_time = ht.index[i]
        exit_price = ht["open"].iloc[i]

        pnl = exit_price - entry_price

        print(
            f"Trade {trade_number}: "
            f"ENTRY {entry_time} @ {entry_price:.2f} | "
            f"EXIT {exit_time} @ {exit_price:.2f} | "
            f"P&L {pnl:.2f}"
        )

        in_position = False
        entry_time = None
        entry_price = None