from __future__ import annotations

import pandas as pd

from quanttools import Backtest
from quanttools.statistics import (
    cagr,
    sharpe_ratio,
    sortino_ratio,
)


NSE_15M_PERIODS_PER_YEAR = 252 * 26


class HalfTrendBacktest:
    """
    HalfTrend research backtest with explicit 15-minute
    annualization conventions.
    """

    def __init__(
        self,
        returns: pd.Series,
        trade_results: pd.Series,
        periods_per_year: int = NSE_15M_PERIODS_PER_YEAR,
    ) -> None:
        self.returns = returns
        self.trade_results = trade_results
        self.periods_per_year = periods_per_year

        self.backtest = Backtest(
            returns=returns,
            trade_results=trade_results,
        )

    def cagr(self) -> float:
        """Calculate CAGR using the configured frequency."""
        return cagr(
            self.returns,
            periods_per_year=self.periods_per_year,
        )

    def sharpe_ratio(self) -> float:
        """Calculate annualized Sharpe using the configured frequency."""
        return sharpe_ratio(
            self.returns,
            periods_per_year=self.periods_per_year,
        )

    def sortino_ratio(self) -> float:
        """Calculate annualized Sortino using the configured frequency."""
        return sortino_ratio(
            self.returns,
            periods_per_year=self.periods_per_year,
        )

    def summary(self) -> dict[str, float | int]:
        """
        Return the HalfTrend research performance summary.
        """
        base = self.backtest.summary()

        return {
            "cagr": self.cagr(),
            "sharpe_ratio": self.sharpe_ratio(),
            "sortino_ratio": self.sortino_ratio(),
            "calmar_ratio": base["calmar_ratio"],
            "max_drawdown": base["max_drawdown"],
            "drawdown_duration": base["drawdown_duration"],
            "profit_factor": base["profit_factor"],
            "expectancy": base["expectancy"],
            "win_rate": base["win_rate"],
            "average_win": base["average_win"],
            "average_loss": base["average_loss"],
            "payoff_ratio": base["payoff_ratio"],
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Return the research summary as a DataFrame."""
        return pd.DataFrame(
            self.summary().items(),
            columns=["Metric", "Value"],
        )

    def to_json(self) -> str:
        """Return the research summary as JSON."""
        import json

        return json.dumps(
            self.summary(),
            indent=4,
        )


def run_backtest(
    df: pd.DataFrame,
    equity: pd.Series,
    returns: pd.Series,
    trade_results: pd.Series,
    periods_per_year: int = NSE_15M_PERIODS_PER_YEAR,
) -> HalfTrendBacktest:
    """
    Create a HalfTrend research backtest.

    Parameters
    ----------
    df:
        HalfTrend DataFrame.

    equity:
        Portfolio equity curve.

    returns:
        Periodic portfolio returns.

    trade_results:
        Completed trade P&Ls.

    periods_per_year:
        Annualization convention.

        Default:
            252 trading sessions × 26 fifteen-minute bars
            per NSE session = 6,552 periods/year.
    """
    if len(df) != len(returns):
        raise ValueError("Data and returns must have the same length.")

    if not df.index.equals(returns.index):
        raise ValueError("Data and returns must share the same index.")

    if not equity.index.equals(returns.index):
        raise ValueError("Equity and returns must share the same index.")

    if periods_per_year <= 0:
        raise ValueError(
            "periods_per_year must be greater than zero."
        )

    return HalfTrendBacktest(
        returns=returns,
        trade_results=trade_results,
        periods_per_year=periods_per_year,
    )