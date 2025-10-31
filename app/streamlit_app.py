import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.quant_investor.config import (
    DEFAULT_MOMENTUM_WINDOW,
    DEFAULT_PERIOD,
    DEFAULT_TICKERS,
    TOP_N,
)
from src.quant_investor.data import fetch_data
from src.quant_investor.factors import compute_momentum
from src.quant_investor.rank import rank_by_score


st.set_page_config(page_title="Quant Investor - Momentum Screener", layout="wide")
st.title("Quant Investor: Top Momentum Stocks")


@st.cache_data(show_spinner=False)
def get_data(tickers: list[str], period: str) -> dict[str, pd.DataFrame]:
    return fetch_data(tickers, period=period)


with st.sidebar:
    st.header("Settings")
    tickers = st.multiselect("Tickers", DEFAULT_TICKERS, default=DEFAULT_TICKERS)
    period = st.selectbox("History period", ["6mo", "1y", "2y", "5y"], index=["6mo", "1y", "2y", "5y"].index(DEFAULT_PERIOD))
    window = st.slider("Momentum window (days)", min_value=10, max_value=120, value=DEFAULT_MOMENTUM_WINDOW, step=5)
    top_n = st.slider("Top N", min_value=3, max_value=10, value=TOP_N)


if not tickers:
    st.info("Select at least one ticker in the sidebar.")
    st.stop()

with st.spinner("Fetching data..."):
    data = get_data(tickers, period)

scores = compute_momentum(data, window=window)
top = rank_by_score(scores, top_n=top_n)

if not top:
    st.warning("No momentum scores available. Try a shorter window or different tickers.")
else:
    df_top = pd.DataFrame(top, columns=["Ticker", "Momentum"])  # type: ignore[arg-type]
    df_top["Momentum %"] = (df_top["Momentum"] * 100).round(2)
    st.subheader("Top Stocks by Momentum")
    st.dataframe(df_top[["Ticker", "Momentum %"]], hide_index=True, use_container_width=True)

    selected = st.selectbox("View price chart for", [t for t, _ in top])
    if selected in data:
        df_price = data[selected].copy()
        # Ensure Date is a column (it should be after fetch_data normalization)
        if df_price.index.name == "Date" or isinstance(df_price.index, pd.DatetimeIndex):
            df_price = df_price.reset_index()
        fig = px.line(df_price, x="Date", y="Close", title=f"{selected} Close Price")
        st.plotly_chart(fig, use_container_width=True)

