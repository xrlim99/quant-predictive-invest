from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd


class BaseDataProvider(ABC):
    """Abstract base class for data providers."""

    @abstractmethod
    def fetch_data(self, tickers: list[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """Fetch historical OHLCV data for given tickers.

        Args:
            tickers: List of ticker symbols
            period: Time period (e.g., "1y", "6mo")

        Returns:
            Dictionary mapping ticker to DataFrame with Date, Open, High, Low, Close, Volume columns
        """
        pass

    @staticmethod
    def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize DataFrame to standard format.

        Ensures Date is a column and MultiIndex columns are flattened.
        Removes duplicate columns.
        """
        df = df.copy()

        # Handle MultiIndex columns (flatten if needed)
        if isinstance(df.columns, pd.MultiIndex):
            # If MultiIndex, drop the second level (usually the ticker name)
            if df.columns.nlevels > 1:
                df.columns = df.columns.droplevel(1)
            else:
                df.columns = df.columns.get_level_values(0)

        # Remove duplicate columns (keep first occurrence)
        if df.columns.duplicated().any():
            df = df.loc[:, ~df.columns.duplicated(keep='first')]

        # Ensure Date is a column (not just index)
        if df.index.name == "Date" or isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()

        # Ensure Date column exists and is datetime
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])

        return df
