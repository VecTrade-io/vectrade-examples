"""Earnings Tracker — alerts you when portfolio companies report earnings.

Demonstrates: earnings calendar, webhooks, portfolio tracking.
"""

import asyncio
from datetime import datetime, timedelta

from vectrade import AsyncVecTrade


async def main() -> None:
    async with AsyncVecTrade() as client:
        # Portfolio tickers to track
        portfolio = ["AAPL", "GOOGL", "MSFT", "NVDA", "AMZN"]

        # Check earnings calendar for next 30 days
        today = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        calendar = await client.earnings.calendar(from_date=today, to_date=end_date)

        # Filter for portfolio companies
        upcoming = [e for e in calendar if e.symbol in portfolio]

        if not upcoming:
            print("No portfolio earnings in the next 30 days.")
            return

        print(f"{'Symbol':<8} {'Date':<12} {'Time':<15} {'EPS Est':<10} {'Rev Est'}")
        print("-" * 60)
        for entry in sorted(upcoming, key=lambda x: x.date):
            eps_str = f"${entry.eps_estimate:.2f}" if entry.eps_estimate else "N/A"
            rev_str = f"${entry.revenue_estimate/1e9:.1f}B" if entry.revenue_estimate else "N/A"
            print(f"{entry.symbol:<8} {entry.date:<12} {entry.time:<15} {eps_str:<10} {rev_str}")

        # Set up webhook for earnings alerts
        print("\nSetting up webhook for earnings alerts...")
        webhook = await client.webhooks.create(
            url="https://your-server.com/webhooks/earnings",
            events=["earnings.released"],
        )
        print(f"Webhook created: {webhook.id}")


if __name__ == "__main__":
    asyncio.run(main())
