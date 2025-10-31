# Quant Investor

Momentum-based daily stock screener for UK tickers using Yahoo Finance. Includes a CLI and a Streamlit dashboard.

## Features
- Fetches historical data via `yfinance`
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

### 3) Run the CLI (prints top 5)
```powershell
python -m src.quant_investor.cli
```

### 4) Run the dashboard
```powershell
streamlit run app/streamlit_app.py
```

## Configuration
Edit defaults in `src/quant_investor/config.py`:
- `DEFAULT_TICKERS` – initial UK tickers
- `DEFAULT_PERIOD` – history period (e.g., `"1y"`)
- `DEFAULT_MOMENTUM_WINDOW` – window days for momentum
- `TOP_N` – number of top stocks to display

## Roadmap
- Add technical indicators (SMA, EMA, RSI) via `ta`
- Integrate fundamentals for multi-factor scoring
- Optionally swap data source to Alpha Vantage or IEX Cloud
- Train a simple ML forecaster (e.g., linear regression, XGBoost) for next-day return

## Notes
- This project currently ranks by momentum; it is not a predictive model.
- Yahoo Finance data via `yfinance` is convenient but not an official API.

