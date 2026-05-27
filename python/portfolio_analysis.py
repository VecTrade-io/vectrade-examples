"""VecTrade Python SDK — Portfolio Analysis Example.

Demonstrates building a portfolio dashboard with:
- Batch quotes for current positions
- Technical scoring for each holding
- Insider activity monitoring
- Analyst consensus overview

Prerequisites:
    pip install vectrade
    export VECTRADE_API_KEY=vq_your_key_here
"""

import asyncio
from vectrade import AsyncVecTrade


async def main():
    portfolio = {
        "AAPL": 50,   # 50 shares
        "MSFT": 30,
        "GOOGL": 20,
        "NVDA": 40,
        "AMZN": 25,
    }
    symbols = list(portfolio.keys())

    async with AsyncVecTrade() as client:
        # 1. Portfolio value from batch quotes
        print("=== Portfolio Overview ===")
        quotes = await client.quotes.batch(symbols)
        total_value = 0
        print(f"{'Symbol':<8} {'Shares':<8} {'Price':<10} {'Value':<12} {'Change'}")
        print("-" * 55)
        for q in quotes:
            if q.symbol in portfolio:
                shares = portfolio[q.symbol]
                value = shares * q.price
                total_value += value
                print(f"{q.symbol:<8} {shares:<8} ${q.price:<9.2f} ${value:<11,.0f} {q.change_pct:+.2f}%")
        print(f"\n  Total Portfolio Value: ${total_value:,.0f}")

        # 2. Technical health check
        print("\n=== Technical Health ===")
        techs = await asyncio.gather(
            *[client.technicals.get(sym) for sym in symbols]
        )
        print(f"{'Symbol':<8} {'Score':<8} {'RSI':<8} {'Signal':<12} {'Trend'}")
        print("-" * 50)
        for tech in techs:
            rsi = tech.indicators["rsi"]["value"]
            signal = tech.indicators["rsi"]["signal"]
            trend = tech.summary["trend"]
            print(f"{tech.symbol:<8} {tech.technical_score:<8} {rsi:<8.1f} {signal:<12} {trend}")

        # 3. Analyst consensus
        print("\n=== Analyst Ratings ===")
        analysts = await asyncio.gather(
            *[client.analyst.consensus(sym) for sym in symbols]
        )
        print(f"{'Symbol':<8} {'Rating':<10} {'Signal':<10} {'Score'}")
        print("-" * 40)
        for a in analysts:
            print(f"{a.symbol:<8} {a.consensus:<10} {a.signal:<10} {a.consensus_score}")

        # 4. Insider activity (check for unusual activity)
        print("\n=== Recent Insider Activity ===")
        insiders = await asyncio.gather(
            *[client.insider.transactions(sym, limit=3) for sym in symbols],
            return_exceptions=True
        )
        for sym, trades in zip(symbols, insiders):
            if isinstance(trades, Exception) or not trades:
                continue
            for t in trades[:2]:
                print(f"  {sym} | {t.insider_name} ({t.position}) | {t.transaction_type} | {t.shares:,} shares")


if __name__ == "__main__":
    asyncio.run(main())
