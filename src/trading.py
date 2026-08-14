from __future__ import annotations

import pandas as pd


def generate_trade_ledger(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert HalfTrend signals into a long-only trade ledger.

    Signals generated at the close of bar N are executed at the
    open of bar N+1, matching the default TradingView strategy
    execution behavior.

    Parameters
    ----------
    df:
        DataFrame containing open, close, buy_signal, and sell_signal.

    Returns
    -------
    pandas.DataFrame
        Completed trade ledger containing:

        - trade
        - entry_time
        - entry_price
        - exit_time
        - exit_price
        - gross_pnl
    """

    required = {
        "open",
        "close",
        "buy_signal",
        "sell_signal",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    trades: list[dict] = []

    in_position = False
    entry_time = None
    entry_price: float | None = None

    for i in range(len(df)):

        if i > 0:

            # ----------------------------------------------------------
            # Previous bar's signal executes at current bar's open.
            # ----------------------------------------------------------
            if (
                df["buy_signal"].iloc[i - 1]
                and not in_position
            ):
                entry_time = df.index[i]
                entry_price = float(df["open"].iloc[i])
                in_position = True

            elif (
                df["sell_signal"].iloc[i - 1]
                and in_position
            ):
                exit_time = df.index[i]
                exit_price = float(df["open"].iloc[i])

                gross_pnl = exit_price - entry_price

                trades.append(
                    {
                        "trade": len(trades) + 1,
                        "entry_time": entry_time,
                        "entry_price": entry_price,
                        "exit_time": exit_time,
                        "exit_price": exit_price,
                        "gross_pnl": gross_pnl,
                    }
                )

                entry_time = None
                entry_price = None
                in_position = False

    return pd.DataFrame(
        trades,
        columns=[
            "trade",
            "entry_time",
            "entry_price",
            "exit_time",
            "exit_price",
            "gross_pnl",
        ],
    )


def generate_long_only_trades(
    df: pd.DataFrame,
) -> tuple[pd.Series, pd.Series]:
    """
    Backward-compatible execution interface.

    Returns
    -------
    positions:
        Position held during each bar.

    trade_results:
        Gross P&L in points for each completed trade.
    """

    required = {
        "open",
        "close",
        "buy_signal",
        "sell_signal",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    positions = pd.Series(
        0.0,
        index=df.index,
        name="position",
    )

    in_position = False

    for i in range(len(df)):

        if i > 0:

            if (
                df["buy_signal"].iloc[i - 1]
                and not in_position
            ):
                in_position = True

            elif (
                df["sell_signal"].iloc[i - 1]
                and in_position
            ):
                in_position = False

        positions.iloc[i] = (
            1.0 if in_position else 0.0
        )

    ledger = generate_trade_ledger(df)

    trade_results = pd.Series(
        ledger["gross_pnl"].to_numpy(),
        name="trade_results",
        dtype=float,
    )

    return positions, trade_results