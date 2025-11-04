import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.quant_investor.config import DEFAULT_MARKET
from src.quant_investor.data import fetch_data
from src.quant_investor.ml_predictor import (
    create_features,
    prepare_training_data,
    train_prediction_models,
)
from src.quant_investor.markets import MARKET_CONFIGS


st.set_page_config(page_title="Quant Investor - Validation", layout="wide")

st.title("🔬 Model Validation: 6-Month Backtest")
st.markdown(
    "This dashboard trains a prediction model on historical data up to 6 months ago, "
    "makes predictions as of that split date for the selected tickers, extrapolates the predicted 20-day return to a 6-month estimate, "
    "and compares the estimated 6-month return against the actual observed return over the past 6 months.\n\n"
    "Notes: this is a simple validation harness. We assume the model predicting 20-day returns can be extrapolated to 6 months by compounding. "
    "This introduces approximation error — treat results as indicative rather than definitive."
)


@st.cache_data(show_spinner=False)
def get_data(tickers: list[str], period: str = "1y", provider: str = "yahoo", api_key: str | None = None) -> dict[str, pd.DataFrame]:
    return fetch_data(tickers, period=period, provider=provider, api_key=api_key)


# Sidebar
with st.sidebar:
    st.header("Validation Settings")
    market = st.selectbox("Market", list(MARKET_CONFIGS.keys()), index=list(MARKET_CONFIGS.keys()).index(DEFAULT_MARKET))
    market_tickers = MARKET_CONFIGS[market]["tickers"]
    tickers = st.multiselect("Tickers (choose up to 20)", market_tickers, default=market_tickers[:10])
    provider = st.selectbox("Data Provider", ["yahoo", "alpha_vantage"], index=0)
    api_key = None
    if provider == "alpha_vantage":
        api_key = st.text_input("Alpha Vantage API Key", type="password")

    st.markdown("---")
    st.write("This validation uses 1 year of history and treats the last 6 months as the test window.")


if not tickers:
    st.info("Select tickers in the sidebar to run validation.")
    st.stop()

with st.spinner("Fetching data..."):
    data = get_data(tickers, period="1y", provider=provider, api_key=api_key)

if not data:
    st.error("No data fetched. Check tickers or data provider.")
    st.stop()

# Determine split date (6 months before the latest available date)
all_dates = []
for df in data.values():
    if "Date" in df.columns:
        all_dates.extend(pd.to_datetime(df["Date"]))
    elif isinstance(df.index, pd.DatetimeIndex):
        all_dates.extend(df.index)

if not all_dates:
    st.error("No date information available in fetched data.")
    st.stop()

last_date = max(all_dates)
split_date = last_date - pd.DateOffset(months=6)

st.write(f"Data end date: {last_date.date()} — using split date (6 months ago) = {split_date.date()}")

# Prepare training data: use only rows strictly before split_date
train_data = {}
for ticker, df in data.items():
    df_copy = df.copy()
    if "Date" in df_copy.columns:
        df_copy["Date"] = pd.to_datetime(df_copy["Date"])
        df_train = df_copy[df_copy["Date"] < split_date]
    elif isinstance(df_copy.index, pd.DatetimeIndex):
        df_train = df_copy[df_copy.index < split_date]
    else:
        df_train = pd.DataFrame()

    if len(df_train) > 0:
        train_data[ticker] = df_train

if not train_data:
    st.error("Insufficient historical data before split date to train a model.")
    st.stop()

with st.spinner("Preparing training data and training model..."):
    features_df, targets_df = prepare_training_data(train_data)

    # If preparation failed (too few rows), automatically try with more history (2y)
    if features_df.empty or targets_df.empty:
        st.warning("Failed to prepare training data with 1y history. Attempting with 2y history...")
        try:
            data_extended = get_data(tickers, period="2y", provider=provider, api_key=api_key)
        except Exception as e:
            st.error(f"Failed to fetch extended history: {e}")
            st.stop()

        # rebuild train_data using the same split_date but with extended history
        train_data_ext = {}
        for ticker, df in data_extended.items():
            df_copy = df.copy()
            if "Date" in df_copy.columns:
                df_copy["Date"] = pd.to_datetime(df_copy["Date"])
                df_train = df_copy[df_copy["Date"] < split_date]
            elif isinstance(df_copy.index, pd.DatetimeIndex):
                df_train = df_copy[df_copy.index < split_date]
            else:
                df_train = pd.DataFrame()

            if len(df_train) > 0:
                train_data_ext[ticker] = df_train

        if not train_data_ext:
            st.error("Insufficient historical data before split date even with extended history.")
            st.stop()

        features_df, targets_df = prepare_training_data(train_data_ext)

        if features_df.empty or targets_df.empty:
            st.error("Failed to prepare training data even after extending history to 2y. Try selecting different tickers or enabling a longer period manually.")
            st.stop()

    # Train for 20-day horizon (can be changed)
    try:
        model, scaler, feature_names = train_prediction_models(features_df, targets_df, horizon="next_20d")
    except Exception as e:
        st.error(f"Model training failed: {e}")
        st.stop()

    st.success("Model trained on pre-split data.")

# For each ticker, get features as of the split date (closest available prior row) and predict
results = []
business_days = pd.bdate_range(start=split_date, end=last_date).size

for ticker, df in data.items():
    try:
        df_feats = create_features(df.copy())

        # Ensure Date is index
        if "Date" in df_feats.columns:
            df_feats.index = pd.to_datetime(df_feats["Date"])

        # Select the latest row on or before split_date
        snapshot = df_feats[df_feats.index <= split_date]
        if snapshot.empty:
            continue

        snapshot_row = snapshot[feature_names].dropna()
        # take the last available row with all feature columns
        if snapshot_row.empty:
            continue
        snapshot_row = snapshot_row.iloc[-1:]

        # Scale and predict 20-day return
        X = snapshot_row.values
        X_scaled = scaler.transform(X)
        pred_20d = float(model.predict(X_scaled)[0])
        # Extrapolate predicted 20-day return to 6-months by compounding
        # n_periods = number of 20-day periods within the observed business day window
        n_periods = max(1, int(round(business_days / 20)))
        pred_6m = (1 + pred_20d) ** n_periods - 1

        # Actual 6-month return: price change from snapshot date to last_date
        # Need price at snapshot and final price
        # Use Close column
        if "Date" in df.columns:
            df_prices = df.copy()
            df_prices["Date"] = pd.to_datetime(df_prices["Date"])
            df_prices = df_prices.set_index("Date")
        else:
            df_prices = df.copy()

        # get price at snapshot (closest on/before split_date)
        price_row = df_prices[df_prices.index <= split_date]
        if price_row.empty:
            continue
        price_snapshot = float(price_row["Close"].iloc[-1])
        price_final = float(df_prices["Close"].iloc[-1])

        actual_6m = price_final / price_snapshot - 1.0

        results.append({
            "ticker": ticker,
            "pred_20d": pred_20d,
            "pred_6m": pred_6m,
            "actual_6m": actual_6m,
            "price_snapshot": price_snapshot,
            "price_final": price_final,
        })

    except Exception as e:
        st.warning(f"Skipping {ticker}: {e}")
        continue

if not results:
    st.error("No valid predictions could be made for the selected tickers.")
    st.stop()

df_results = pd.DataFrame(results)
df_results["error_abs"] = (df_results["pred_6m"] - df_results["actual_6m"]).abs()
df_results = df_results.sort_values("pred_6m", ascending=False)

st.subheader("Prediction vs Actual (6-month)")
st.write(f"Business days in test window: {business_days}")
st.dataframe(
    df_results[["ticker", "pred_6m", "actual_6m", "error_abs"]].assign(
        pred_6m=lambda d: (d["pred_6m"] * 100).map("{:.2f}%".format),
        actual_6m=lambda d: (d["actual_6m"] * 100).map("{:.2f}%".format),
        error_abs=lambda d: (d["error_abs"] * 100).map("{:.2f}%".format),
    ), hide_index=True, use_container_width=True
)

# Summary metrics
mae = df_results["error_abs"].mean()
st.metric("Mean Absolute Error (6m)", f"{mae:.2%}")

# Bar chart: predicted vs actual
fig = px.bar(
    df_results.melt(id_vars=["ticker"], value_vars=["pred_6m", "actual_6m"]),
    x="ticker",
    y="value",
    color="variable",
    barmode="group",
    labels={"value": "Return", "ticker": "Ticker"},
    title="Predicted vs Actual 6-Month Returns"
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Validation is approximate: predicted 20-day returns are extrapolated to 6 months by compounding; for rigorous backtesting use rolling retraining and out-of-sample evaluation.")
