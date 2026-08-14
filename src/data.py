from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"date", "open", "high", "low", "close", "volume"}


def load_minute_data(path: str | Path) -> pd.DataFrame:
    """
    Load NIFTY 50 minute-level OHLCV data.

    Parameters
    ----------
    path:
        Path to the minute-level CSV.

    Returns
    -------
    pandas.DataFrame
        Data indexed by datetime with OHLCV columns.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date")
    df = df.set_index("date")

    if df.index.has_duplicates:
        raise ValueError("Duplicate timestamps found in minute data.")

    return df[
        ["open", "high", "low", "close", "volume"]
    ]


def resample_to_15m(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample minute-level OHLCV data to 15-minute bars.

    Parameters
    ----------
    df:
        Minute-level OHLCV data indexed by datetime.

    Returns
    -------
    pandas.DataFrame
        15-minute OHLCV data.
    """
    required = {"open", "high", "low", "close", "volume"}

    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    resampled = df.resample("15min").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    )

    resampled = resampled.dropna(
        subset=["open", "high", "low", "close"]
    )

    return resampled