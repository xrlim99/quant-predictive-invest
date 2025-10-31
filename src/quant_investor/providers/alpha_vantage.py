import os
import time
from typing import Dict, Union

import pandas as pd
from alpha_vantage.timeseries import TimeSeries

from .base import BaseDataProvider


class AlphaVantageProvider(BaseDataProvider):
    """Alpha Vantage data provider.

    Requires ALPHA_VANTAGE_API_KEY environment variable or API key parameter.
    Free tier: 5 API calls per minute, 500 calls per day.
    """

    def __init__(self, api_key: Union[str, None] = None):
        """Initialize Alpha Vantage provider.

        Args:
            api_key: Alpha Vantage API key. If None, reads from ALPHA_VANTAGE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key required. "
                "Set ALPHA_VANTAGE_API_KEY environment variable or pass api_key parameter. "
                "Get your free key at: https://www.alphavantage.co/support/#api-key"
            )
        self.ts = TimeSeries(key=self.api_key, output_format="pandas")

    def _period_to_outputsize(self, period: str) -> str:
        """Convert period string to Alpha Vantage outputsize parameter.

        Alpha Vantage supports 'compact' (last 100 data points) or 'full' (full history).
        """
        # Map common periods to full history for more data
        full_periods = ["1y", "2y", "5y", "10y", "max"]
        return "full" if period in full_periods else "compact"

    def fetch_data(self, tickers: list[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """Fetch historical OHLCV data using Alpha Vantage.

        Args:
            tickers: List of ticker symbols (Note: Alpha Vantage uses different formats)
                    For UK stocks, remove .L suffix (e.g., "BARC.L" -> "BARC" or "BARC.LSE")
            period: Time period (converted to outputsize parameter)

        Returns:
            Dictionary mapping ticker to normalized DataFrame

        Note:
            Alpha Vantage has rate limits (5 calls/min free tier).
            This method adds delays between calls to avoid hitting limits.
        """
        data: Dict[str, pd.DataFrame] = {}
        outputsize = self._period_to_outputsize(period)

        for i, ticker in enumerate(tickers):
            try:
                # Alpha Vantage format: remove .L suffix or convert to LSE format
                # Some UK stocks might need ".LSE" or just the base symbol
                av_ticker = ticker.replace(".L", ".LSE") if ".L" in ticker else ticker

                # Rate limiting: 5 calls per minute = 12 seconds between calls
                if i > 0:
                    time.sleep(12)  # Wait 12 seconds between API calls

                df, meta_data = self.ts.get_daily_adjusted(
                    symbol=av_ticker, outputsize=outputsize
                )

                if df is not None and not df.empty:
                    # Alpha Vantage returns columns like: open, high, low, close, adjusted close, volume, dividend, split
                    # Rename to match expected format (title case)
                    df = df.copy()
                    df.columns = [col.title() for col in df.columns]

                    # Map Alpha Vantage columns to our standard format
                    column_mapping = {
                        "Open": "Open",
                        "High": "High",
                        "Low": "Low",
                        "Close": "Close",
                        "Adjusted Close": "Close",  # Use adjusted close if available
                        "Volume": "Volume",
                    }

                    # Select and rename columns
                    available_cols = [col for col in column_mapping.keys() if col in df.columns]
                    df = df[available_cols]
                    df.columns = [column_mapping[col] for col in df.columns]

                    # Reset index (Alpha Vantage uses date as index)
                    df = df.reset_index()
                    if "Date" not in df.columns and len(df.columns) > 0:
                        # Check if first column is date-like
                        first_col = df.columns[0]
                        if "date" in first_col.lower():
                            df = df.rename(columns={first_col: "Date"})

                    df = self.normalize_dataframe(df)
                    data[ticker] = df

            except Exception as e:
                print(f"Warning: Failed to fetch {ticker} from Alpha Vantage: {e}")
                # For UK stocks, try alternative format
                if ".L" in ticker:
                    try:
                        base_ticker = ticker.replace(".L", "")
                        if i > 0:
                            time.sleep(12)
                        df, _ = self.ts.get_daily_adjusted(
                            symbol=base_ticker, outputsize=outputsize
                        )
                        if df is not None and not df.empty:
                            df.columns = [col.title() for col in df.columns]
                            column_mapping = {
                                "Open": "Open",
                                "High": "High",
                                "Low": "Low",
                                "Close": "Close",
                                "Adjusted Close": "Close",
                                "Volume": "Volume",
                            }
                            available_cols = [
                                col for col in column_mapping.keys() if col in df.columns
                            ]
                            df = df[available_cols]
                            df.columns = [column_mapping[col] for col in df.columns]
                            df = df.reset_index()
                            if "Date" not in df.columns and len(df.columns) > 0:
                                first_col = df.columns[0]
                                if "date" in first_col.lower():
                                    df = df.rename(columns={first_col: "Date"})
                            df = self.normalize_dataframe(df)
                            data[ticker] = df
                    except Exception:
                        continue
                continue

        return data
