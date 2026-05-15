"""VecTrade Python Project Template — main entry point."""

import os

from vectrade import VecTrade


def main() -> None:
    # Client reads VECTRADE_API_KEY from environment
    client = VecTrade()

    # Example: Get a quote
    quote = client.quotes.get("AAPL")
    print(f"{quote.symbol}: ${quote.price:.2f} ({quote.change_pct:+.2f}%)")

    # Example: Get fundamentals
    fundamentals = client.fundamentals.get("AAPL")
    print(f"P/E: {fundamentals.pe_ratio}, Market Cap: ${fundamentals.market_cap/1e9:.0f}B")

    client.close()


if __name__ == "__main__":
    main()
