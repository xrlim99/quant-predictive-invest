from typing import Dict

import pandas as pd
import ta


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators (SMA, EMA, RSI) to a DataFrame.

    Args:
        df: DataFrame with Date, Open, High, Low, Close, Volume columns

    Returns:
        DataFrame with added technical indicator columns
    """
    df = df.copy()
    
    # Remove duplicate columns if any (keep first occurrence)
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
    
    # Ensure we have required columns
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return df
    
    # Ensure Close column is a single Series (not duplicated)
    if isinstance(df["Close"], pd.DataFrame):
        # If Close is a DataFrame (multiple columns), take the first one
        df["Close"] = df["Close"].iloc[:, 0]
    elif isinstance(df["Close"], pd.Series):
        # Already a Series, good
        pass
    else:
        return df
    
    # Set Date as index if it's a column (needed for ta library)
    date_as_index = False
    if "Date" in df.columns:
        df = df.set_index("Date")
        date_as_index = True
    
    try:
        # Get Close as a Series to ensure it's 1-dimensional
        close_series = df["Close"]
        if not isinstance(close_series, pd.Series):
            close_series = close_series.iloc[:, 0] if hasattr(close_series, 'iloc') else close_series.squeeze()
        
        # Simple Moving Averages (SMA)
        df["SMA_20"] = ta.trend.SMAIndicator(close=close_series, window=20).sma_indicator()
        df["SMA_50"] = ta.trend.SMAIndicator(close=close_series, window=50).sma_indicator()
        df["SMA_200"] = ta.trend.SMAIndicator(close=close_series, window=200).sma_indicator()
        
        # Exponential Moving Averages (EMA)
        df["EMA_12"] = ta.trend.EMAIndicator(close=close_series, window=12).ema_indicator()
        df["EMA_26"] = ta.trend.EMAIndicator(close=close_series, window=26).ema_indicator()
        
        # Relative Strength Index (RSI)
        df["RSI"] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
        
        # MACD (bonus indicator)
        macd = ta.trend.MACD(close=close_series)
        df["MACD"] = macd.macd()
        df["MACD_signal"] = macd.macd_signal()
        df["MACD_diff"] = macd.macd_diff()
        
    except Exception as e:
        print(f"Warning: Error calculating technical indicators: {e}")
    
    # Reset index if we set Date as index
    if date_as_index:
        df = df.reset_index()
    
    return df


def compute_technical_scores(data_by_ticker: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
    """Compute technical indicator scores for each ticker.

    Returns a dictionary mapping ticker to a dict of technical scores.
    Scores are normalized and combined into a composite technical score.
    """
    scores: Dict[str, Dict[str, float]] = {}
    
    for ticker, df in data_by_ticker.items():
        df_with_indicators = add_technical_indicators(df)
        
        if df_with_indicators.empty or "Close" not in df_with_indicators.columns:
            continue
        
        ticker_scores: Dict[str, float] = {}
        
        try:
            # Get latest values
            latest = df_with_indicators.iloc[-1]
            close_price = float(latest["Close"])
            
            # 1. SMA Signals (price vs moving averages)
            if "SMA_20" in df_with_indicators.columns and pd.notna(latest["SMA_20"]):
                sma20 = float(latest["SMA_20"])
                ticker_scores["sma20_signal"] = (close_price - sma20) / sma20 if sma20 > 0 else 0.0
            
            if "SMA_50" in df_with_indicators.columns and pd.notna(latest["SMA_50"]):
                sma50 = float(latest["SMA_50"])
                ticker_scores["sma50_signal"] = (close_price - sma50) / sma50 if sma50 > 0 else 0.0
            
            # 2. EMA Signal (12 vs 26 crossover)
            if all(col in df_with_indicators.columns for col in ["EMA_12", "EMA_26"]):
                ema12 = float(latest["EMA_12"]) if pd.notna(latest["EMA_12"]) else 0
                ema26 = float(latest["EMA_26"]) if pd.notna(latest["EMA_26"]) else 0
                if ema26 > 0:
                    ticker_scores["ema_signal"] = (ema12 - ema26) / ema26
                else:
                    ticker_scores["ema_signal"] = 0.0
            
            # 3. RSI Score (normalized: 0-100 -> -1 to 1, where >70 is overbought, <30 is oversold)
            if "RSI" in df_with_indicators.columns and pd.notna(latest["RSI"]):
                rsi = float(latest["RSI"])
                # Normalize RSI: ideal is around 50-60, so we score based on distance from extremes
                # RSI 30-70 is neutral, above 70 is bearish, below 30 is bullish (for contrarian)
                # For momentum: RSI 50-70 is bullish, 30-50 is neutral, <30 or >70 are extreme
                if 30 <= rsi <= 70:
                    # In neutral range, score based on distance from 50
                    ticker_scores["rsi_signal"] = (rsi - 50) / 50  # -0.4 to 0.4
                elif rsi < 30:
                    # Oversold - bullish signal
                    ticker_scores["rsi_signal"] = 0.5
                else:  # rsi > 70
                    # Overbought - bearish signal
                    ticker_scores["rsi_signal"] = -0.3
            
            # 4. MACD Signal
            if "MACD" in df_with_indicators.columns and "MACD_signal" in df_with_indicators.columns:
                macd = float(latest["MACD"]) if pd.notna(latest["MACD"]) else 0
                macd_signal = float(latest["MACD_signal"]) if pd.notna(latest["MACD_signal"]) else 0
                if macd_signal != 0:
                    ticker_scores["macd_signal"] = (macd - macd_signal) / abs(macd_signal)
                else:
                    ticker_scores["macd_signal"] = 0.0
            
            # Composite technical score (weighted average)
            technical_score = (
                ticker_scores.get("sma20_signal", 0) * 0.2 +
                ticker_scores.get("sma50_signal", 0) * 0.2 +
                ticker_scores.get("ema_signal", 0) * 0.25 +
                ticker_scores.get("rsi_signal", 0) * 0.2 +
                ticker_scores.get("macd_signal", 0) * 0.15
            )
            ticker_scores["composite_technical"] = technical_score
            
            scores[ticker] = ticker_scores
            
        except Exception as e:
            print(f"Warning: Error computing technical scores for {ticker}: {e}")
            continue
    
    return scores

