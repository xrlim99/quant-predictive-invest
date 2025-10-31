from typing import Dict, Union

import yfinance as yf


def fetch_fundamentals(tickers: list[str]) -> Dict[str, Dict[str, Union[float, None]]]:
    """Fetch fundamental metrics (P/E ratio, dividend yield) for tickers.

    Args:
        tickers: List of ticker symbols

    Returns:
        Dictionary mapping ticker to dict with fundamental metrics:
        - pe_ratio: Price-to-Earnings ratio
        - dividend_yield: Dividend yield as percentage
        - market_cap: Market capitalization (if available)
    """
    fundamentals: Dict[str, Dict[str, Union[float, None]]] = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            ticker_fundamentals: Dict[str, Union[float, None]] = {}
            
            # P/E Ratio
            pe_ratio = info.get("trailingPE") or info.get("forwardPE")
            ticker_fundamentals["pe_ratio"] = float(pe_ratio) if pe_ratio is not None else None
            
            # Dividend Yield
            dividend_yield = info.get("dividendYield")
            if dividend_yield is not None:
                # Convert to percentage if it's a decimal
                if dividend_yield < 1:
                    ticker_fundamentals["dividend_yield"] = dividend_yield * 100
                else:
                    ticker_fundamentals["dividend_yield"] = float(dividend_yield)
            else:
                ticker_fundamentals["dividend_yield"] = None
            
            # Market Cap (for reference)
            market_cap = info.get("marketCap")
            ticker_fundamentals["market_cap"] = float(market_cap) if market_cap is not None else None
            
            # Additional metrics
            ticker_fundamentals["price_to_book"] = info.get("priceToBook")
            ticker_fundamentals["debt_to_equity"] = info.get("debtToEquity")
            ticker_fundamentals["roe"] = info.get("returnOnEquity")  # Return on Equity
            ticker_fundamentals["profit_margin"] = info.get("profitMargins")
            
            fundamentals[ticker] = ticker_fundamentals
            
        except Exception as e:
            print(f"Warning: Failed to fetch fundamentals for {ticker}: {e}")
            fundamentals[ticker] = {
                "pe_ratio": None,
                "dividend_yield": None,
                "market_cap": None,
                "price_to_book": None,
                "debt_to_equity": None,
                "roe": None,
                "profit_margin": None,
            }
    
    return fundamentals


def compute_fundamental_scores(fundamentals: Dict[str, Dict[str, Union[float, None]]]) -> Dict[str, Dict[str, float]]:
    """Compute normalized scores from fundamental metrics.

    Scores are normalized to 0-1 range where higher is better.
    """
    scores: Dict[str, Dict[str, float]] = {}
    
    # Collect all values for normalization
    pe_values = [f["pe_ratio"] for f in fundamentals.values() if f.get("pe_ratio") is not None]
    div_yield_values = [f["dividend_yield"] for f in fundamentals.values() if f.get("dividend_yield") is not None]
    pb_values = [f["price_to_book"] for f in fundamentals.values() if f.get("price_to_book") is not None]
    roe_values = [f["roe"] for f in fundamentals.values() if f.get("roe") is not None]
    
    pe_min, pe_max = (min(pe_values), max(pe_values)) if pe_values else (10, 30)
    div_min, div_max = (min(div_yield_values), max(div_yield_values)) if div_yield_values else (0, 10)
    pb_min, pb_max = (min(pb_values), max(pb_values)) if pb_values else (0, 5)
    roe_min, roe_max = (min(roe_values), max(roe_values)) if roe_values else (-10, 30)
    
    for ticker, metrics in fundamentals.items():
        ticker_scores: Dict[str, float] = {}
        
        # 1. P/E Ratio Score (lower is better, but not too low)
        pe_ratio = metrics.get("pe_ratio")
        if pe_ratio is not None:
            # Ideal P/E is around 15-20, penalize extremes
            if 10 <= pe_ratio <= 25:
                ticker_scores["pe_score"] = 1.0 - abs(pe_ratio - 17.5) / 17.5
            elif pe_ratio < 10:
                ticker_scores["pe_score"] = 0.5  # Might be too cheap (value trap?)
            else:
                ticker_scores["pe_score"] = max(0, 1.0 - (pe_ratio - 25) / 50)  # Penalize high P/E
        else:
            ticker_scores["pe_score"] = 0.5  # Neutral if missing
        
        # 2. Dividend Yield Score (higher is better, but not extreme)
        div_yield = metrics.get("dividend_yield")
        if div_yield is not None:
            # Normalize: 2-6% is ideal, higher is good but might indicate problems
            if 2 <= div_yield <= 6:
                ticker_scores["dividend_score"] = 1.0
            elif div_yield < 2:
                ticker_scores["dividend_score"] = div_yield / 2
            else:  # > 6%
                ticker_scores["dividend_score"] = max(0.7, 1.0 - (div_yield - 6) / 10)
        else:
            ticker_scores["dividend_score"] = 0.3  # Lower score if no dividend
        
        # 3. Price-to-Book Score (lower is generally better for value)
        pb = metrics.get("price_to_book")
        if pb is not None and pb > 0:
            # P/B < 1 is undervalued, 1-3 is reasonable, >3 is expensive
            if pb < 1:
                ticker_scores["pb_score"] = 1.0
            elif pb <= 3:
                ticker_scores["pb_score"] = 1.0 - (pb - 1) / 2
            else:
                ticker_scores["pb_score"] = max(0, 0.5 - (pb - 3) / 10)
        else:
            ticker_scores["pb_score"] = 0.5
        
        # 4. ROE Score (higher is better)
        roe = metrics.get("roe")
        if roe is not None:
            # ROE > 15% is good, >20% is excellent
            if roe >= 20:
                ticker_scores["roe_score"] = 1.0
            elif roe >= 15:
                ticker_scores["roe_score"] = 0.8
            elif roe >= 10:
                ticker_scores["roe_score"] = 0.6
            elif roe >= 0:
                ticker_scores["roe_score"] = 0.4
            else:
                ticker_scores["roe_score"] = 0.1  # Negative ROE is bad
        else:
            ticker_scores["roe_score"] = 0.5
        
        # Composite fundamental score
        fundamental_score = (
            ticker_scores.get("pe_score", 0.5) * 0.3 +
            ticker_scores.get("dividend_score", 0.3) * 0.3 +
            ticker_scores.get("pb_score", 0.5) * 0.2 +
            ticker_scores.get("roe_score", 0.5) * 0.2
        )
        ticker_scores["composite_fundamental"] = fundamental_score
        
        scores[ticker] = ticker_scores
    
    return scores

