"""Earnings Tracker — checks earnings data for portfolio companies.

Demonstrates: earnings endpoint, batch quotes, async concurrent requests.
"""

import asyncio

from vectrade import AsyncVecTrade


async def main() -> None:
    async with AsyncVecTrade() as client:
        # Portfolio tickers to track
        portfolio = ["AAPL", "GOOGL", "MSFT", "NVDA", "AMZN"]

        # Get batch quotes for portfolio
        quotes = await client.quotes.batch(portfolio)
        print(f"{'Symbol':<8} {'Price':<10} {'Change':<10} {'Volume'}")
        print("-" * 45)
        for q in quotes:
            print(f"{q.symbol:<8} ${q.price:<9.2f} {q.change_pct:+.2f}%{'':>3} {q.volume:,.0f}")

        # Check earnings data for each stock
        print("\n\nEarnings Data:")
        print("-" * 60)
        earnings_tasks = [client.earnings.get(symbol) for symbol in portfolio]
        results = await asyncio.gather(*earnings_tasks, return_exceptions=True)

        for symbol, result in zip(portfolio, results):
            if isinstance(result, Exception):
                print(f"  {symbol}: No earnings data available")
                continue
            print(f"\n  {symbol}: {result}")

        # Get analyst ratings for context
        print("\n\nAnalyst Consensus:")
        print("-" * 45)
        analyst_tasks = [client.analyst.get(symbol) for symbol in portfolio]
        analyst_results = await asyncio.gather(*analyst_tasks, return_exceptions=True)

        for symbol, result in zip(portfolio, analyst_results):
            if isinstance(result, Exception):
                print(f"  {symbol}: No analyst data")
                continue
            print(f"  {symbol}: {result}")


if __name__ == "__main__":
    asyncio.run(main())
