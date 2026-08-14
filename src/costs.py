from __future__ import annotations

import pandas as pd


def apply_transaction_costs(
    trades: pd.DataFrame,
    cost_bps: float,
) -> pd.DataFrame:
    """
    Apply proportional transaction costs to a completed trade ledger.

    Costs are applied independently to entry and exit notional.

    Parameters
    ----------
    trades:
        Trade ledger containing entry_price and exit_price.

    cost_bps:
        Transaction cost in basis points per side.

        Examples
        --------
        5 bps = 0.05% per side
        8 bps = 0.08% per side
        10 bps = 0.10% per side

    Returns
    -------
    pandas.DataFrame
        Copy of the trade ledger with:

        - entry_cost
        - exit_cost
        - total_cost
        - net_pnl
    """

    if cost_bps < 0:
        raise ValueError(
            "cost_bps must be greater than or equal to zero."
        )

    required = {
        "entry_price",
        "exit_price",
        "gross_pnl",
    }

    missing = required - set(trades.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    result = trades.copy()

    rate = cost_bps / 10_000.0

    result["entry_cost"] = (
        result["entry_price"] * rate
    )

    result["exit_cost"] = (
        result["exit_price"] * rate
    )

    result["total_cost"] = (
        result["entry_cost"]
        + result["exit_cost"]
    )

    result["net_pnl"] = (
        result["gross_pnl"]
        - result["total_cost"]
    )

    return result