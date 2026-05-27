"""VecTrade Python SDK — Error Handling Patterns.

Demonstrates proper error handling for production applications:
- Authentication failures (invalid/expired API key)
- Rate limiting with retry-after
- Not found (invalid ticker symbol)
- Generic API errors
- Batch processing with graceful fallback

Prerequisites:
    pip install vectrade
    export VECTRADE_API_KEY=vq_your_key_here
"""

import sys
import time

from vectrade import (
    VecTrade,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from vectrade._exceptions import APIError


def basic_error_handling():
    """Basic example showing common error types."""
    client = VecTrade()

    try:
        quote = client.quotes.get("AAPL")
        print(f"AAPL: ${quote.price:.2f} ({quote.change_pct:+.2f}%)")
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("  → Check your VECTRADE_API_KEY or get a key at https://vectrade.io/vtrade/developer")
        sys.exit(1)
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after}s")
    except NotFoundError as e:
        print(f"Symbol not found: {e}")
    except ServerError as e:
        print(f"Server error (try again later): {e}")
    except APIError as e:
        print(f"API error ({e.status_code}): {e}")


def retry_with_backoff():
    """Retry pattern with exponential backoff for rate limits."""
    client = VecTrade()
    max_retries = 3

    for attempt in range(max_retries):
        try:
            tech = client.technicals.get("TSLA")
            print(f"TSLA Technical Score: {tech.technical_score}")
            break
        except RateLimitError as e:
            wait = e.retry_after or (2 ** attempt)
            print(f"  Rate limited (attempt {attempt + 1}/{max_retries}), waiting {wait}s...")
            time.sleep(wait)
    else:
        print("  Failed after all retries")


def batch_with_fallback():
    """Fetch data for multiple symbols, handling individual failures gracefully."""
    client = VecTrade()
    symbols = ["AAPL", "MSFT", "INVALID_TICKER_XYZ", "GOOGL", "NVDA"]

    print("\n=== Batch with Fallback ===")
    results = {}
    for symbol in symbols:
        try:
            quote = client.quotes.get(symbol)
            results[symbol] = {"price": quote.price, "change_pct": quote.change_pct}
        except NotFoundError:
            results[symbol] = {"error": "Symbol not found"}
        except APIError as e:
            results[symbol] = {"error": f"API error: {e}"}

    for symbol, data in results.items():
        if "error" in data:
            print(f"  {symbol}: {data['error']}")
        else:
            print(f"  {symbol}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")


if __name__ == "__main__":
    print("=== Basic Error Handling ===")
    basic_error_handling()

    print("\n=== Retry with Backoff ===")
    retry_with_backoff()

    batch_with_fallback()
