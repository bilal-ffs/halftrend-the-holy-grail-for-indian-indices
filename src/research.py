from __future__ import annotations

import pandas as pd


IS_START = "2015-01-09"
IS_END = "2022-01-08"

OOS_START = "2022-01-09"
OOS_END = "2025-07-25"


def split_is_oos(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split the dataset into fixed in-sample and out-of-sample periods.

    In-Sample:
        2015-01-09 → 2022-01-08

    Out-of-Sample:
        2022-01-09 → 2025-07-25

    Parameters
    ----------
    df:
        OHLCV DataFrame indexed by datetime.

    Returns
    -------
    tuple[pandas.DataFrame, pandas.DataFrame]
        In-sample and out-of-sample datasets.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame must have a DatetimeIndex.")

    if not df.index.is_monotonic_increasing:
        raise ValueError("DataFrame index must be sorted.")

    is_data = df.loc[
        IS_START:IS_END
    ].copy()

    oos_data = df.loc[
        OOS_START:OOS_END
    ].copy()

    if is_data.empty:
        raise ValueError("In-sample dataset is empty.")

    if oos_data.empty:
        raise ValueError("Out-of-sample dataset is empty.")

    if is_data.index.max() >= oos_data.index.min():
        raise ValueError("In-sample and OOS periods overlap.")

    return is_data, oos_data