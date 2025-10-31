import os
from typing import Dict, List, Union

import pandas as pd
from dotenv import load_dotenv

from .config import ALPHA_VANTAGE_API_KEY, DataProvider, DEFAULT_DATA_PROVIDER
from .providers import AlphaVantageProvider, YahooFinanceProvider

# Load environment variables from .env file
load_dotenv()


def get_provider(provider: DataProvider | None = None, api_key: str | None = None) -> Union[YahooFinanceProvider, AlphaVantageProvider]:
    """Get a data provider instance.

    Args:
        provider: Provider name ("yahoo" or "alpha_vantage"). If None, uses DEFAULT_DATA_PROVIDER.
        api_key: Alpha Vantage API key (only needed for alpha_vantage provider)

    Returns:
        Data provider instance
    """
    provider = provider or DEFAULT_DATA_PROVIDER or os.getenv("DATA_PROVIDER", "yahoo")

    if provider == "alpha_vantage":
        # Use provided key, then env var, then config default
        key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY") or ALPHA_VANTAGE_API_KEY
        return AlphaVantageProvider(api_key=key)
    else:
        return YahooFinanceProvider()


def fetch_data(
    tickers: List[str],
    period: str = "1y",
    provider: Union[DataProvider, None] = None,
    api_key: Union[str, None] = None,
) -> Dict[str, pd.DataFrame]:
    """Fetch historical OHLCV data for each ticker using the specified provider.

    Args:
        tickers: List of ticker symbols
        period: Time period (e.g., "1y", "6mo")
        provider: Data provider to use ("yahoo" or "alpha_vantage"). Defaults to config.
        api_key: Alpha Vantage API key (only needed for alpha_vantage provider)

    Returns:
        Dictionary mapping ticker to its DataFrame. Skips empty results.
        All DataFrames are normalized with Date as a column.
    """
    data_provider = get_provider(provider=provider, api_key=api_key)
    return data_provider.fetch_data(tickers, period=period)

