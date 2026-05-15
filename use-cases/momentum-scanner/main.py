"""Momentum Scanner — screens for stocks with strong momentum signals.

Demonstrates: screener, technical indicators via FinKit, batch quotes.
"""

import asyncio

from vectrade import AsyncVecTrade

# Using finkit for local calculations on returned data
from finkit import rsi, ema, SignalEngine


async def main() -> None:
    async with AsyncVecTrade() as client:
        # Screen for high-volume stocks with recent price momentum
        results = []
        async for page in client.screener.run(
            filters={
                "market_cap_min": 10_000_000_000,  # $10B+
                "avg_volume_min": 5_000_000,
                "change_pct_min": 2.0,  # Up 2%+ today
            },
            sort_by="change_pct",
            sort_order="desc",
            page_size=20,
        ):
            results.extend(page)

        if not results:
            print("No stocks match momentum criteria today.")
            return

        print(f"Found {len(results)} momentum candidates:\n")
        print(f"{'Symbol':<8} {'Price':<10} {'Change':<10} {'Volume':<12} {'Mkt Cap'}")
        print("-" * 55)

        for stock in results[:10]:
            vol_str = f"{stock.volume/1e6:.1f}M"
            cap_str = f"${stock.market_cap/1e9:.0f}B" if stock.market_cap else "N/A"
            print(
                f"{stock.symbol:<8} "
                f"${stock.price:<9.2f} "
                f"+{stock.change_pct:.1f}%{'':>4} "
                f"{vol_str:<12} "
                f"{cap_str}"
            )

        # Get detailed technicals for top 5
        print("\n\nTechnical Analysis (Top 5):")
        print("-" * 55)
        top_symbols = [r.symbol for r in results[:5]]

        for symbol in top_symbols:
            technicals = await client.technicals.get(symbol)
            print(f"\n  {symbol}:")
            print(f"    RSI(14): {technicals.rsi_14:.1f}")
            print(f"    MACD:    {technicals.macd:.4f}")
            print(f"    Signal:  {technicals.macd_signal:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
