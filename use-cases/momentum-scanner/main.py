"""Momentum Scanner — screens for stocks with strong momentum signals.

Demonstrates: batch quotes, technical indicators, insider trading data.
"""

import asyncio

from vectrade import AsyncVecTrade


async def main() -> None:
    async with AsyncVecTrade() as client:
        # Scan a watchlist of popular stocks
        watchlist = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
            "META", "TSLA", "AMD", "NFLX", "CRM",
        ]

        # Get batch quotes
        quotes = await client.quotes.batch(watchlist)

        # Filter for momentum (positive change)
        movers = sorted(quotes, key=lambda q: q.change_pct, reverse=True)

        print("Momentum Candidates (sorted by daily change):\n")
        print(f"{'Symbol':<8} {'Price':<10} {'Change':<10} {'Volume'}")
        print("-" * 45)
        for q in movers:
            print(f"{q.symbol:<8} ${q.price:<9.2f} {q.change_pct:+.2f}%{'':>3} {q.volume:,.0f}")

        # Get detailed technicals for top 5 movers
        top_symbols = [q.symbol for q in movers[:5]]
        print(f"\n\nTechnical Analysis (Top 5 Movers):")
        print("-" * 55)

        tech_tasks = [client.technicals.get(symbol) for symbol in top_symbols]
        tech_results = await asyncio.gather(*tech_tasks, return_exceptions=True)

        for symbol, tech in zip(top_symbols, tech_results):
            if isinstance(tech, Exception):
                print(f"\n  {symbol}: Technical data unavailable")
                continue
            print(f"\n  {symbol}:")
            print(f"    RSI(14): {tech.rsi_14:.1f}" if hasattr(tech, "rsi_14") else f"    RSI: {tech}")
            if hasattr(tech, "macd"):
                print(f"    MACD: {tech.macd:.4f}")
            if hasattr(tech, "signal"):
                signal = "BULLISH" if tech.rsi_14 < 70 and tech.macd > 0 else "BEARISH"
                print(f"    Signal: {signal}")

        # Check insider activity for top movers
        print(f"\n\nInsider Activity (Top 5):")
        print("-" * 55)
        insider_tasks = [client.insider.get(symbol) for symbol in top_symbols]
        insider_results = await asyncio.gather(*insider_tasks, return_exceptions=True)

        for symbol, insider in zip(top_symbols, insider_results):
            if isinstance(insider, Exception):
                print(f"  {symbol}: No insider data")
                continue
            print(f"  {symbol}: {insider}")


if __name__ == "__main__":
    asyncio.run(main())
