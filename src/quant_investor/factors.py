from typing import Dict

import pandas as pd


def compute_momentum(data_by_ticker: Dict[str, pd.DataFrame], window: int = 30) -> Dict[str, float]:
    """Compute simple price momentum over the window for each ticker.

    Momentum = (Close[-1] - Close[-window]) / Close[-window]
    Only computes if there are at least `window` rows.
    """
    scores: Dict[str, float] = {}
    for ticker, df in data_by_ticker.items():
        closes = df.get("Close")
        if closes is None or len(closes) < window:
            continue
        start = float(closes.iloc[-window])
        end = float(closes.iloc[-1])
        if start != 0:
            scores[ticker] = (end - start) / start
    return scores

