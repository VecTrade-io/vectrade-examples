"""VecTrade Python SDK — Async Example.

Demonstrates using AsyncVecTrade for concurrent API calls,
which is significantly faster when fetching data for multiple stocks.

Prerequisites:
    pip install vectrade
    export VECTRADE_API_KEY=vq_your_key_here
"""

import asyncio
from vectrade import AsyncVecTrade


async def main():
    async with AsyncVecTrade() as client:
        # Fetch technicals for 5 stocks concurrently
        symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]

        print("=== Concurrent Technical Analysis ===")
        print(f"Fetching technicals for {len(symbols)} stocks concurrently...\n")

        # All 5 requests execute in parallel
        results = await asyncio.gather(
            *[client.technicals.get(sym) for sym in symbols]
        )

        print(f"{'Symbol':<8} {'Score':<8} {'RSI':<10} {'MACD':<12} {'Trend'}")
        print("-" * 55)
        for tech in results:
            rsi = tech.indicators["rsi"]["value"]
            macd_signal = tech.indicators["macd"]["signal"]
            trend = tech.summary["trend"]
            print(f"{tech.symbol:<8} {tech.technical_score:<8} {rsi:<10.1f} {macd_signal:<12} {trend}")

        # Fetch analyst consensus + news concurrently for a single stock
        print("\n=== Deep Dive: NVDA ===")
        analyst, news, earnings = await asyncio.gather(
            client.analyst.consensus("NVDA"),
            client.news.list("NVDA", limit=3),
            client.earnings.history("NVDA", limit=2),
        )

        print(f"  Analyst: {analyst.consensus} (signal: {analyst.signal})")
        print(f"  News ({len(news)} articles):")
        for article in news:
            print(f"    • {article.title[:70]}")
        print(f"  Last Earnings:")
        for e in earnings:
            eps_str = f"${e.eps_actual:.2f}" if e.eps_actual and e.eps_actual < 1000 else str(e.eps_actual)
            print(f"    {e.date}: EPS {eps_str}")


if __name__ == "__main__":
    asyncio.run(main())
