from typing import Dict

import pandas as pd
import yfinance as yf

from .base import BaseDataProvider


class YahooFinanceProvider(BaseDataProvider):
    """Yahoo Finance data provider using yfinance library."""

    def fetch_data(self, tickers: list[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """Fetch historical OHLCV data using Yahoo Finance.

        Args:
            tickers: List of ticker symbols (e.g., ["BARC.L", "HSBA.L"])
            period: Time period - "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"

        Returns:
            Dictionary mapping ticker to normalized DataFrame
        """
        data: Dict[str, pd.DataFrame] = {}
        for ticker in tickers:
            try:
                df = yf.download(ticker, period=period, progress=False)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    df = self.normalize_dataframe(df)
                    data[ticker] = df
            except Exception as e:
                print(f"Warning: Failed to fetch {ticker} from Yahoo Finance: {e}")
                continue
        return data
