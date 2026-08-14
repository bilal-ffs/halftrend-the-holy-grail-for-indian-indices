from __future__ import annotations

import pandas as pd


def build_equity_curve(
    df: pd.DataFrame,
    initial_capital: float = 100_000.0,
) -> pd.Series:
    """
    Build the long-only equity curve from HalfTrend signals.

    Signals generated at the close of bar N are executed at the
    open of bar N+1.

    Parameters
    ----------
    df:
        DataFrame containing:
        open, close, buy_signal, sell_signal.

    initial_capital:
        Starting portfolio value.

    Returns
    -------
    pandas.Series
        Portfolio equity indexed by bar timestamp.
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

    equity = pd.Series(
        initial_capital,
        index=df.index,
        name="equity",
        dtype=float,
    )

    capital = initial_capital
    in_position = False
    entry_price: float | None = None

    for i in range(1, len(df)):
        previous_close = float(df["close"].iloc[i - 1])
        current_open = float(df["open"].iloc[i])
        current_close = float(df["close"].iloc[i])

        previous_buy = bool(df["buy_signal"].iloc[i - 1])
        previous_sell = bool(df["sell_signal"].iloc[i - 1])

        # --------------------------------------------------------------
        # Execute previous-bar signal at current-bar open.
        # --------------------------------------------------------------
        if previous_buy and not in_position:
            entry_price = current_open
            in_position = True

            # Enter at the current bar's open, then mark the position
            # to the current bar's close.
            capital *= current_close / current_open
            equity.iloc[i] = capital

        elif previous_sell and in_position:
            if entry_price is None:
                raise RuntimeError(
                    "Exit occurred without an entry price."
                )

            capital *= current_open / previous_close
            equity.iloc[i] = capital

            in_position = False
            entry_price = None

        # --------------------------------------------------------------
        # While long, mark the portfolio to the current close.
        # --------------------------------------------------------------
        elif in_position:
            capital *= current_close / previous_close
            equity.iloc[i] = capital

        else:
            equity.iloc[i] = capital

    return equity


def equity_to_returns(
    equity: pd.Series,
) -> pd.Series:
    """
    Convert an equity curve into periodic returns.
    """
    if equity.empty:
        return equity.rename("strategy_return")

    returns = equity.pct_change()

    returns = returns.fillna(0.0)

    returns.name = "strategy_return"

    return returns