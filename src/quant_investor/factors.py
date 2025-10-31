from typing import Dict, Union

import pandas as pd

from .config import SCORING_WEIGHTS


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


def compute_composite_score(
    momentum_scores: Dict[str, float],
    technical_scores: Dict[str, Dict[str, float]],
    fundamental_scores: Dict[str, Dict[str, float]],
    weights: Union[Dict[str, float], None] = None,
) -> Dict[str, Dict[str, float]]:
    """Compute composite score combining momentum, technical, and fundamental factors.

    Args:
        momentum_scores: Dict mapping ticker to momentum score
        technical_scores: Dict mapping ticker to dict of technical indicator scores
        fundamental_scores: Dict mapping ticker to dict of fundamental scores
        weights: Weights for each factor type (defaults to SCORING_WEIGHTS from config)

    Returns:
        Dict mapping ticker to dict containing:
        - momentum_score: Raw momentum value
        - technical_score: Composite technical score
        - fundamental_score: Composite fundamental score
        - composite_score: Weighted combination of all factors
    """
    weights = weights or SCORING_WEIGHTS
    composite_scores: Dict[str, Dict[str, float]] = {}

    # Get all unique tickers from all score dicts
    all_tickers = set(momentum_scores.keys()) | set(technical_scores.keys()) | set(fundamental_scores.keys())

    for ticker in all_tickers:
        momentum = momentum_scores.get(ticker, 0.0)
        technical = technical_scores.get(ticker, {}).get("composite_technical", 0.0)
        fundamental = fundamental_scores.get(ticker, {}).get("composite_fundamental", 0.0)

        # Normalize momentum to 0-1 range (assuming typical range of -0.5 to 0.5)
        # Clamp extreme values
        normalized_momentum = max(-1.0, min(1.0, momentum))
        normalized_momentum = (normalized_momentum + 1.0) / 2.0  # Convert to 0-1 range

        # Normalize technical score (already roughly in -1 to 1 range)
        normalized_technical = max(0.0, min(1.0, (technical + 1.0) / 2.0))

        # Fundamental score is already in 0-1 range

        # Compute weighted composite score
        composite = (
            normalized_momentum * weights.get("momentum", 0.4) +
            normalized_technical * weights.get("technical", 0.35) +
            fundamental * weights.get("fundamental", 0.25)
        )

        composite_scores[ticker] = {
            "momentum_score": momentum,
            "technical_score": technical,
            "fundamental_score": fundamental,
            "composite_score": composite,
            # Include sub-scores for detailed breakdown
            "normalized_momentum": normalized_momentum,
            "normalized_technical": normalized_technical,
        }

    return composite_scores

