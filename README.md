# Quant Investor

Momentum-based daily stock screener for UK tickers with support for Yahoo Finance and Alpha Vantage APIs. Includes a CLI and a Streamlit dashboard.

## Features
- **Dual API Support**: Fetch data from Yahoo Finance (fast, no key required) or Alpha Vantage (official API)
- Computes 30-day price momentum (configurable)
- Ranks tickers and shows top N
- Streamlit dashboard with rankings and interactive charts

## Quickstart

### 1) Create a virtual environment (recommended)
```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 2b) (Optional) Configure Alpha Vantage API Key
If you want to use Alpha Vantage API:
1. Get a free API key at https://www.alphavantage.co/support/#api-key
2. Copy `env_example.txt` to `.env` and add your key:
```powershell
copy env_example.txt .env
# Then edit .env and add your API key
```

Or set the environment variable:
```powershell
$env:ALPHA_VANTAGE_API_KEY="your_key_here"
```

### 3) Run the CLI (prints top 5)
```powershell
python -m src.quant_investor.cli
```

### 4) Run the dashboard
```powershell
streamlit run app/streamlit_app.py
```

## Data Sources

The project supports two data providers:

### Yahoo Finance (Default)
- ✅ Fast, no API key required
- ✅ Supports all LSE tickers with `.L` suffix
- ✅ Unlimited requests
- ⚠️ Unofficial API (via yfinance library)

### Alpha Vantage
- ✅ Official API
- ✅ Reliable and well-documented
- ⚠️ Requires free API key (get at https://www.alphavantage.co/support/#api-key)
- ⚠️ Free tier: 5 calls/minute, 500 calls/day
- ⚠️ UK ticker format may differ (provider handles conversion)

**Switching providers:**
- **Dashboard**: Use the "API Provider" dropdown in the sidebar
- **Environment variable**: Set `DATA_PROVIDER=alpha_vantage` in `.env` or environment
- **Code**: Pass `provider="alpha_vantage"` to `fetch_data()`

## Configuration
Edit defaults in `src/quant_investor/config.py`:
- `DEFAULT_TICKERS` – initial UK tickers (top 50 LSE stocks)
- `DEFAULT_PERIOD` – history period (e.g., `"1y"`)
- `DEFAULT_MOMENTUM_WINDOW` – window days for momentum
- `DEFAULT_DATA_PROVIDER` – default API provider (`"yahoo"` or `"alpha_vantage"`)
- `TOP_N` – number of top stocks to display

## Roadmap
- Add technical indicators (SMA, EMA, RSI) via `ta`
- Integrate fundamentals for multi-factor scoring
- Optionally swap data source to Alpha Vantage or IEX Cloud
- Train a simple ML forecaster (e.g., linear regression, XGBoost) for next-day return

## Notes
- This project currently ranks by momentum; it is not a predictive model.
- Yahoo Finance is the default due to speed and no API key requirement.
- For production use or higher rate limits, consider Alpha Vantage or upgrading to a paid tier.
- When using Alpha Vantage with many tickers, the provider automatically handles rate limiting (12-second delays between calls).

