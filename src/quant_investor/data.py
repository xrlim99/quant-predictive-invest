from typing import Dict, List

import pandas as pd
import yfinance as yf


def fetch_data(tickers: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
    """Fetch historical OHLCV data for each ticker using yfinance.

    Returns a dict mapping ticker to its DataFrame. Skips empty results.
    Normalizes MultiIndex columns and ensures Date is a column.
    """
    data: Dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        df = yf.download(ticker, period=period, progress=False)
        if isinstance(df, pd.DataFrame) and not df.empty:
            # Handle MultiIndex columns (flatten if needed)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1) if df.columns.nlevels > 1 else df.columns
            
            # Ensure Date is a column (not just index)
            if df.index.name == "Date" or isinstance(df.index, pd.DatetimeIndex):
                df = df.reset_index()
            
            data[ticker] = df
    return data

