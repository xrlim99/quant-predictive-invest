import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.quant_investor.config import (
    DEFAULT_DATA_PROVIDER,
    DEFAULT_MARKET,
    DEFAULT_MOMENTUM_WINDOW,
    DEFAULT_PERIOD,
    DEFAULT_TICKERS,
    SCORING_WEIGHTS,
    TOP_N,
)
from src.quant_investor.data import fetch_data
from src.quant_investor.factors import compute_composite_score, compute_momentum
from src.quant_investor.fundamentals import compute_fundamental_scores, fetch_fundamentals
from src.quant_investor.markets import MARKET_CONFIGS
from src.quant_investor.rank import rank_by_score
from src.quant_investor.technical import compute_technical_scores


st.set_page_config(page_title="Quant Investor - Stock Screener", layout="wide")


@st.cache_data(show_spinner=False)
def get_data(
    tickers: list[str],
    period: str,
    provider: str = "yahoo",
    api_key: str = None,
) -> dict[str, pd.DataFrame]:
    return fetch_data(tickers, period=period, provider=provider, api_key=api_key)  # type: ignore[arg-type]


# Initialize session state for market if not exists
if "selected_market" not in st.session_state:
    st.session_state.selected_market = DEFAULT_MARKET

with st.sidebar:
    st.header("Settings")
    
    # Market Selection
    st.subheader("Stock Market")
    market = st.selectbox(
        "Market",
        ["UK", "MY"],
        index=0 if DEFAULT_MARKET == "UK" else 1,
        help="Select stock market: UK (London Stock Exchange) or MY (Bursa Malaysia)",
        key="market_selector",
    )
    
    # Update session state when market changes
    st.session_state.selected_market = market
    
    market_config = MARKET_CONFIGS[market]
    market_tickers = market_config["tickers"]
    currency_symbol = market_config["currency_symbol"]
    currency_code = market_config["currency"]
    
    st.info(f"📍 {market_config['name']} - {market_config['index_name']}")
    st.caption(f"Currency: {currency_code} ({currency_symbol})")
    
    st.divider()
    
    # Data Provider Selection
    st.subheader("Data Source")
    provider = st.selectbox(
        "API Provider",
        ["yahoo", "alpha_vantage"],
        index=0 if DEFAULT_DATA_PROVIDER == "yahoo" else 1,
        help="Yahoo Finance: Fast, no API key required. Alpha Vantage: Official API, requires key (free tier: 5 calls/min)",
    )
    
    api_key = None
    if provider == "alpha_vantage":
        api_key = st.text_input(
            "Alpha Vantage API Key",
            type="password",
            help="Get your free API key at https://www.alphavantage.co/support/#api-key",
            placeholder="Enter your API key or set ALPHA_VANTAGE_API_KEY env var",
        )
        if not api_key:
            st.warning("⚠️ Alpha Vantage requires an API key. Enter it above or set ALPHA_VANTAGE_API_KEY environment variable.")
    
    st.divider()
    
    # Analysis Settings
    st.subheader("Analysis Settings")
    tickers = st.multiselect(
        "Tickers",
        market_tickers,
        default=market_tickers[:10],  # Default to first 10 for performance
        help=f"Select stocks from {market_config['index_name']}",
    )
    period = st.selectbox("History period", ["6mo", "1y", "2y", "5y"], index=["6mo", "1y", "2y", "5y"].index(DEFAULT_PERIOD))
    window = st.slider("Momentum window (days)", min_value=10, max_value=120, value=DEFAULT_MOMENTUM_WINDOW, step=5)
    top_n = st.slider("Top N", min_value=3, max_value=10, value=TOP_N)
    
    st.divider()
    
    # Scoring weights
    st.subheader("Scoring Weights")
    col1, col2, col3 = st.columns(3)
    with col1:
        momentum_weight = st.slider("Momentum", 0.0, 1.0, SCORING_WEIGHTS["momentum"], 0.05)
    with col2:
        technical_weight = st.slider("Technical", 0.0, 1.0, SCORING_WEIGHTS["technical"], 0.05)
    with col3:
        fundamental_weight = st.slider("Fundamental", 0.0, 1.0, SCORING_WEIGHTS["fundamental"], 0.05)
    
    total_weight = momentum_weight + technical_weight + fundamental_weight
    if abs(total_weight - 1.0) > 0.01:
        st.warning(f"⚠️ Weights sum to {total_weight:.2f}. Normalizing to 1.0...")
        momentum_weight /= total_weight
        technical_weight /= total_weight
        fundamental_weight /= total_weight
    
    custom_weights = {
        "momentum": momentum_weight,
        "technical": technical_weight,
        "fundamental": fundamental_weight,
    }

# Main title (update based on selected market)
current_market = st.session_state.get("selected_market", DEFAULT_MARKET)
current_market_config = MARKET_CONFIGS[current_market]
st.title(f"📊 Quant Investor: Multi-Factor Stock Screener - {current_market_config['index_name']}")
st.caption(f"📍 {current_market_config['name']} | 💰 Currency: {current_market_config['currency']} ({current_market_config['currency_symbol']})")

if not tickers:
    st.info("Select at least one ticker in the sidebar.")
    st.stop()

if provider == "alpha_vantage" and not api_key:
    # Try to get from environment
    import os
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        st.error("❌ Alpha Vantage API key required. Please enter it in the sidebar or set ALPHA_VANTAGE_API_KEY environment variable.")
        st.stop()


with st.spinner(f"Fetching data and computing scores..."):
    try:
        # Fetch price data
        data = get_data(tickers, period, provider=provider, api_key=api_key)
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        if provider == "alpha_vantage":
            st.info("💡 Tip: Make sure your API key is valid and you haven't exceeded rate limits (5 calls/min for free tier).")
        st.stop()
    
    if not data:
        st.error("No data retrieved. Please check ticker symbols and try again.")
        st.stop()
    
    # Compute momentum scores
    momentum_scores = compute_momentum(data, window=window)
    
    # Compute technical indicator scores
    with st.spinner("Computing technical indicators..."):
        technical_scores = compute_technical_scores(data)
    
    # Fetch and compute fundamental scores
    with st.spinner("Fetching fundamentals..."):
        fundamentals_raw = fetch_fundamentals(list(data.keys()))
        fundamental_scores = compute_fundamental_scores(fundamentals_raw)
    
    # Compute composite scores
    composite_scores = compute_composite_score(
        momentum_scores, technical_scores, fundamental_scores, weights=custom_weights
    )
    
    # Rank by composite score
    ranked_by_composite = sorted(
        composite_scores.items(),
        key=lambda x: x[1]["composite_score"],
        reverse=True
    )[:top_n]
    
    if not ranked_by_composite:
        st.warning("No composite scores available. Try adjusting settings.")
        st.stop()

# Display results
st.subheader("🏆 Top Stocks by Composite Score")

# Create comprehensive dataframe
results_data = []
for ticker, scores_dict in ranked_by_composite:
    results_data.append({
        "Ticker": ticker,
        "Composite Score": f"{scores_dict['composite_score']:.3f}",
        "Momentum": f"{scores_dict['momentum_score']:.2%}",
        "Technical": f"{scores_dict['technical_score']:.3f}",
        "Fundamental": f"{scores_dict['fundamental_score']:.3f}",
    })

df_results = pd.DataFrame(results_data)
st.dataframe(df_results, hide_index=True, use_container_width=True)

# Detailed metrics for each stock
st.subheader("📈 Detailed Metrics")

selected_ticker = st.selectbox("Select ticker for detailed view", [t for t, _ in ranked_by_composite])

if selected_ticker in composite_scores:
    ticker_scores = composite_scores[selected_ticker]
    ticker_fundamentals = fundamentals_raw.get(selected_ticker, {})
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Composite Score", f"{ticker_scores['composite_score']:.3f}")
        st.metric("Momentum", f"{ticker_scores['momentum_score']:.2%}")
    
    with col2:
        st.metric("Technical Score", f"{ticker_scores['technical_score']:.3f}")
        tech_details = technical_scores.get(selected_ticker, {})
        if tech_details:
            st.caption(f"RSI: {tech_details.get('rsi_signal', 0):.2f}")
    
    with col3:
        st.metric("Fundamental Score", f"{ticker_scores['fundamental_score']:.3f}")
        pe = ticker_fundamentals.get("pe_ratio")
        if pe is not None:
            st.caption(f"P/E: {pe:.1f}")
    
    with col4:
        div_yield = ticker_fundamentals.get("dividend_yield")
        if div_yield is not None:
            st.metric("Dividend Yield", f"{div_yield:.2f}%")
        else:
            st.metric("Dividend Yield", "N/A")
    
    # Price chart with technical indicators
    if selected_ticker in data:
        from src.quant_investor.technical import add_technical_indicators
        
        df_price = data[selected_ticker].copy()
        if df_price.index.name == "Date" or isinstance(df_price.index, pd.DatetimeIndex):
            df_price = df_price.reset_index()
        
        # Add technical indicators
        df_price = add_technical_indicators(df_price)
        
        # Create chart with price and SMAs
        current_market_config = MARKET_CONFIGS[st.session_state.get("selected_market", DEFAULT_MARKET)]
        currency_symbol = current_market_config["currency_symbol"]
        fig = px.line(df_price, x="Date", y="Close", title=f"{selected_ticker} - Price & Technical Indicators ({currency_symbol})")
        
        # Add SMA lines if available
        if "SMA_20" in df_price.columns:
            fig.add_scatter(x=df_price["Date"], y=df_price["SMA_20"], name="SMA 20", line=dict(dash="dash"))
        if "SMA_50" in df_price.columns:
            fig.add_scatter(x=df_price["Date"], y=df_price["SMA_50"], name="SMA 50", line=dict(dash="dash"))
        if "EMA_12" in df_price.columns:
            fig.add_scatter(x=df_price["Date"], y=df_price["EMA_12"], name="EMA 12", line=dict(dash="dot"))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # RSI subplot
        if "RSI" in df_price.columns:
            fig_rsi = px.line(df_price, x="Date", y="RSI", title=f"{selected_ticker} - RSI")
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
            fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray")
            st.plotly_chart(fig_rsi, use_container_width=True)

