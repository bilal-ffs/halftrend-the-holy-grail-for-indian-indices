from src.data import load_minute_data, resample_to_15m
from src.halftrend import calculate_halftrend
from src.trading import generate_long_only_trades
from src.portfolio import build_equity_curve, equity_to_returns
from src.backtest import run_backtest, NSE_15M_PERIODS_PER_YEAR


DATA_PATH = (
    r"C:\Users\beqmd\Documents\QuantResearch"
    r"\data\NIFTY_50_minute.csv"
)


df = load_minute_data(DATA_PATH)
df15 = resample_to_15m(df).iloc[:1000]

ht = calculate_halftrend(df15)

positions, trade_results = generate_long_only_trades(ht)

equity = build_equity_curve(ht)

returns = equity_to_returns(equity)

backtest = run_backtest(
    df=ht,
    equity=equity,
    returns=returns,
    trade_results=trade_results,
    periods_per_year=NSE_15M_PERIODS_PER_YEAR,
)

print("HalfTrend Backtest")
print("==================")
print()
print(
    "Annualization:",
    f"{NSE_15M_PERIODS_PER_YEAR:,} 15-minute periods/year",
)
print()
print(backtest.to_dataframe().to_string(index=False))
print()
print("JSON:")
print(backtest.to_json())