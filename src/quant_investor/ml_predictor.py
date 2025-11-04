"""Machine Learning prediction module for stock price forecasting."""

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .technical import add_technical_indicators


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create ML features from price data and technical indicators.
    
    Args:
        df: DataFrame with Date, Open, High, Low, Close, Volume columns
        
    Returns:
        DataFrame with feature columns
    """
    df = df.copy()
    
    # Ensure Date is datetime and set as index if it's a column
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
    
    # Add technical indicators
    df = add_technical_indicators(df)
    
    # Price-based features
    df["returns"] = df["Close"].pct_change()
    df["log_returns"] = np.log(df["Close"] / df["Close"].shift(1))
    df["price_change"] = df["Close"] - df["Close"].shift(1)
    df["price_change_pct"] = df["Close"].pct_change()
    
    # Volatility features
    df["volatility_5"] = df["returns"].rolling(window=5).std()
    df["volatility_20"] = df["returns"].rolling(window=20).std()
    df["volatility_60"] = df["returns"].rolling(window=60).std()
    
    # Price position features
    df["high_low_ratio"] = df["High"] / df["Low"]
    df["close_position"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"])
    
    # Volume features
    df["volume_ma_5"] = df["Volume"].rolling(window=5).mean()
    df["volume_ma_20"] = df["Volume"].rolling(window=20).mean()
    df["volume_ratio"] = df["Volume"] / df["volume_ma_20"]
    
    # Moving average features
    if "SMA_20" in df.columns:
        df["price_vs_sma20"] = (df["Close"] - df["SMA_20"]) / df["SMA_20"]
    if "SMA_50" in df.columns:
        df["price_vs_sma50"] = (df["Close"] - df["SMA_50"]) / df["SMA_50"]
    if "EMA_12" in df.columns and "EMA_26" in df.columns:
        df["ema_cross"] = (df["EMA_12"] - df["EMA_26"]) / df["EMA_26"]
    
    # RSI features
    if "RSI" in df.columns:
        df["rsi_signal"] = df["RSI"] - 50  # Center around 0
        df["rsi_overbought"] = (df["RSI"] > 70).astype(int)
        df["rsi_oversold"] = (df["RSI"] < 30).astype(int)
    
    # MACD features
    if "MACD" in df.columns and "MACD_signal" in df.columns:
        df["macd_diff"] = df["MACD"] - df["MACD_signal"]
        df["macd_cross"] = ((df["MACD"] > df["MACD_signal"]) & 
                           (df["MACD"].shift(1) <= df["MACD_signal"].shift(1))).astype(int)
    
    # Lag features (past returns)
    for lag in [1, 2, 3, 5, 10]:
        df[f"return_lag_{lag}"] = df["returns"].shift(lag)
    
    # Target variable: future return (next day, next 5 days, next 20 days)
    df["target_next_day"] = df["returns"].shift(-1)
    df["target_next_5d"] = df["Close"].shift(-5) / df["Close"] - 1
    df["target_next_20d"] = df["Close"].shift(-20) / df["Close"] - 1
    
    return df


def prepare_training_data(data_by_ticker: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare training data from multiple tickers.
    
    Args:
        data_by_ticker: Dictionary mapping ticker to DataFrame
        
    Returns:
        Tuple of (features_df, targets_df) with target columns
    """
    all_features = []
    all_targets = []
    
    for ticker, df in data_by_ticker.items():
        try:
            df_features = create_features(df)
            
            # Select feature columns (exclude target and date-related columns)
            feature_cols = [
                col for col in df_features.columns
                if col not in ["target_next_day", "target_next_5d", "target_next_20d", 
                              "Date", "Open", "High", "Low", "Close", "Volume"]
                and not col.startswith("SMA_") and not col.startswith("EMA_")
                and col not in ["MACD", "MACD_signal", "MACD_diff", "RSI"]
            ]
            
            # Remove rows with NaN
            df_clean = df_features[feature_cols + ["target_next_day", "target_next_5d", "target_next_20d"]].dropna()
            
            if len(df_clean) > 50:  # Need minimum data points
                all_features.append(df_clean[feature_cols])
                all_targets.append(df_clean[["target_next_day", "target_next_5d", "target_next_20d"]])
        except Exception as e:
            print(f"Warning: Error preparing data for {ticker}: {e}")
            continue
    
    if not all_features:
        return pd.DataFrame(), pd.DataFrame()
    
    features_df = pd.concat(all_features, ignore_index=True)
    targets_df = pd.concat(all_targets, ignore_index=True)
    
    return features_df, targets_df


def train_prediction_models(
    features_df: pd.DataFrame,
    targets_df: pd.DataFrame,
    horizon: str = "next_5d"
) -> Tuple[RandomForestRegressor, StandardScaler, List[str]]:
    """Train prediction models for different horizons.
    
    Args:
        features_df: Feature DataFrame
        targets_df: Target DataFrame with target columns
        horizon: Which horizon to predict ("next_day", "next_5d", "next_20d")
        
    Returns:
        Tuple of (trained_model, scaler, feature_names)
    """
    target_col = f"target_{horizon}"
    
    if target_col not in targets_df.columns:
        raise ValueError(f"Target column {target_col} not found")
    
    # Prepare data
    X = features_df.values
    y = targets_df[target_col].values
    
    # Remove infinite and extreme values
    mask = np.isfinite(X).all(axis=1) & np.isfinite(y) & (np.abs(y) < 1.0)  # Max 100% return
    X = X[mask]
    y = y[mask]
    
    if len(X) < 100:
        raise ValueError("Insufficient data for training")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Calculate R² score for validation
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    print(f"Model trained - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
    
    return model, scaler, list(features_df.columns)


def predict_stock_returns(
    data_by_ticker: Dict[str, pd.DataFrame],
    model: RandomForestRegressor,
    scaler: StandardScaler,
    feature_names: List[str],
    horizon: str = "next_5d"
) -> Dict[str, Dict[str, float]]:
    """Predict future returns for each ticker.
    
    Args:
        data_by_ticker: Dictionary mapping ticker to DataFrame
        model: Trained prediction model
        scaler: Fitted scaler
        feature_names: List of feature column names
        horizon: Prediction horizon
        
    Returns:
        Dictionary mapping ticker to dict with predictions and confidence
    """
    predictions = {}
    
    for ticker, df in data_by_ticker.items():
        try:
            # Create features
            df_features = create_features(df)
            
            # Get latest feature values
            feature_cols = [col for col in feature_names if col in df_features.columns]
            if not feature_cols:
                continue
            
            # Get the most recent row with all features
            latest_row = df_features[feature_cols].dropna().iloc[-1:]
            
            if len(latest_row) == 0:
                continue
            
            # Scale features
            X = latest_row.values
            X_scaled = scaler.transform(X)
            
            # Predict
            pred_return = model.predict(X_scaled)[0]
            
            # Get prediction intervals using tree-based uncertainty
            # Use individual tree predictions for uncertainty estimation
            tree_preds = np.array([tree.predict(X_scaled)[0] for tree in model.estimators_])
            pred_std = np.std(tree_preds)
            pred_mean = np.mean(tree_preds)
            
            # 95% confidence interval (assuming normal distribution)
            lower_bound = pred_mean - 1.96 * pred_std
            upper_bound = pred_mean + 1.96 * pred_std
            
            predictions[ticker] = {
                "predicted_return": pred_return,
                "confidence_lower": lower_bound,
                "confidence_upper": upper_bound,
                "confidence_std": pred_std,
                "confidence_score": max(0, 1.0 - pred_std)  # Lower std = higher confidence
            }
            
        except Exception as e:
            print(f"Warning: Error predicting for {ticker}: {e}")
            continue
    
    return predictions


def forecast_trend(
    df: pd.DataFrame,
    days_ahead: int = 180
) -> pd.DataFrame:
    """Forecast price trend using simple moving average and trend extrapolation.
    
    Args:
        df: DataFrame with Date and Close columns
        days_ahead: Number of days to forecast
        
    Returns:
        DataFrame with historical and forecasted prices
    """
    df = df.copy()
    
    # Ensure Date is datetime and sorted
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
    
    if "Close" not in df.columns:
        return pd.DataFrame()
    
    # Calculate trend using linear regression on recent data
    recent_data = df.tail(60)  # Use last 60 days for trend
    if len(recent_data) < 30:
        recent_data = df
    
    dates = pd.to_numeric(recent_data.index if df.index.name == "Date" else recent_data["Date"])
    prices = recent_data["Close"].values
    
    # Simple linear trend
    if len(prices) > 1:
        trend = np.polyfit(dates[-len(prices):], prices, 1)
    else:
        trend = [0, prices[0]]
    
    # Generate future dates (business days for stock market)
    if "Date" in df.columns:
        last_date = pd.to_datetime(df["Date"].max())
    elif isinstance(df.index, pd.DatetimeIndex):
        last_date = df.index.max()
    else:
        last_date = pd.Timestamp.now()
    
    # Generate business days for forecast (skip weekends)
    future_dates = pd.bdate_range(
        start=last_date + pd.Timedelta(days=1),
        periods=days_ahead,
        freq="B"  # Business days
    )
    
    # Forecast prices
    future_dates_numeric = pd.to_numeric(future_dates)
    forecast_prices = np.polyval(trend, future_dates_numeric)
    
    # Ensure forecast prices are reasonable (not negative, not too extreme)
    if len(prices) > 0:
        current_price = prices[-1]
        forecast_prices = np.maximum(forecast_prices, current_price * 0.3)  # Don't go below 30% of current
        forecast_prices = np.minimum(forecast_prices, current_price * 3.0)  # Don't go above 300% of current
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Close": forecast_prices,
        "is_forecast": True
    })
    
    # Add historical data marker
    if "Date" in df.columns:
        df["is_forecast"] = False
        df_forecast = pd.concat([df[["Date", "Close", "is_forecast"]], forecast_df])
    else:
        df = df.reset_index()
        if "Date" not in df.columns or df.columns[0] != "Date":
            df["Date"] = df.index if isinstance(df.index, pd.DatetimeIndex) else pd.date_range(start=pd.Timestamp.now() - pd.Timedelta(days=len(df)), periods=len(df), freq="D")
        df["is_forecast"] = False
        df_forecast = pd.concat([df[["Date", "Close", "is_forecast"]], forecast_df])
    
    return df_forecast.sort_values("Date").reset_index(drop=True)


def get_top_predicted_stocks(
    predictions: Dict[str, Dict[str, float]],
    top_n: int = 5
) -> List[Tuple[str, Dict[str, float]]]:
    """Get top N stocks by predicted return.
    
    Args:
        predictions: Dictionary of predictions
        top_n: Number of top stocks to return
        
    Returns:
        List of tuples (ticker, prediction_dict) sorted by predicted return
    """
    return sorted(
        predictions.items(),
        key=lambda x: x[1]["predicted_return"],
        reverse=True
    )[:top_n]

