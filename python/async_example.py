"""Async VecTrade SDK usage example.

Demonstrates how to use the async client for concurrent API calls,
which is ideal for web frameworks (FastAPI, Starlette) or batch processing.
"""

import asyncio
import os

from vectrade import AsyncVecTrade
from vectrade._exceptions import RateLimitError


async def main() -> None:
    client = AsyncVecTrade(api_key=os.environ["VECTRADE_API_KEY"])

    try:
        # Fetch multiple quotes concurrently
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]
        tasks = [client.quotes.get(s) for s in symbols]
        quotes = await asyncio.gather(*tasks, return_exceptions=True)

        for symbol, result in zip(symbols, quotes):
            if isinstance(result, RateLimitError):
                print(f"{symbol}: rate limited — retry after {result.retry_after}s")
            elif isinstance(result, Exception):
                print(f"{symbol}: error — {result}")
            else:
                print(f"{symbol}: ${result.price}")

        # Developer self-service — check quota
        quota = await client.developer.get_quota()
        print(f"\nQuota: {quota.used}/{quota.monthly_quota} ({quota.remaining} remaining)")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
