"""VecTrade Python SDK — Quick Start Example."""

import os
from vectrade import VecTrade

def main():
    # Initialize client (reads VECTRADE_API_KEY from environment)
    vt = VecTrade()

    # Get a real-time quote
    quote = vt.quotes.get("AAPL")
    print(f"{quote.symbol}: ${quote.price:.2f} ({quote.change_pct:+.2f}%)")

    # Batch quotes
    quotes = vt.quotes.batch(["AAPL", "GOOGL", "MSFT"])
    for q in quotes:
        print(f"  {q.symbol}: ${q.price:.2f}")

    # Stream AI analysis
    print("\n--- AI Analysis ---")
    for chunk in vt.ai.stream("Analyze AAPL for long-term hold"):
        print(chunk.text, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
