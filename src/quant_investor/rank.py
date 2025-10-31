from typing import Dict, List, Tuple


def rank_by_score(scores: Dict[str, float], top_n: int = 5) -> List[Tuple[str, float]]:
    """Return top_n tickers by descending score.

    If fewer than top_n available, returns as many as exist.
    """
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_n]

