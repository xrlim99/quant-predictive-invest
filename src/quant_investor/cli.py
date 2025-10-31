from typing import List

from .config import DEFAULT_MOMENTUM_WINDOW, DEFAULT_PERIOD, DEFAULT_TICKERS, TOP_N
from .data import fetch_data
from .factors import compute_momentum
from .rank import rank_by_score


def run(tickers: List[str] = DEFAULT_TICKERS, period: str = DEFAULT_PERIOD, window: int = DEFAULT_MOMENTUM_WINDOW, top_n: int = TOP_N) -> None:
    data = fetch_data(tickers, period=period)
    scores = compute_momentum(data, window=window)
    top = rank_by_score(scores, top_n=top_n)
    print("Top", top_n, "UK stocks to consider based on momentum:")
    for ticker, score in top:
        print(f"{ticker}: {score:.2%} momentum over last {window} days")


if __name__ == "__main__":
    run()

