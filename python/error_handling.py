"""VecTrade Python SDK — Error Handling & Resilience Patterns.

Demonstrates proper error handling for all error scenarios:
- Authentication failures (invalid/expired API key)
- Rate limiting (too many requests)
- Quota exhaustion (monthly limit reached)
- Payment required (feature needs paid plan)
- Validation errors (bad request parameters)
- Service outages (5xx / network errors)
"""

import sys
from vectrade import (
    VecTrade,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
    PaymentRequiredError,
    ValidationError,
    NotFoundError,
    ServerError,
    ServiceUnavailableError,
    VecTradeError,
)


def basic_error_handling():
    """Minimal error handling — catch the base class."""
    client = VecTrade()

    try:
        quote = client.quotes.get("AAPL")
        print(f"{quote.symbol}: ${quote.price:.2f}")
    except VecTradeError as e:
        print(f"API error: {e} (request_id={e.request_id})")
        sys.exit(1)


def production_error_handling():
    """Production-grade error handling with specific recovery strategies."""
    client = VecTrade()

    try:
        quote = client.quotes.get("AAPL")
        print(f"{quote.symbol}: ${quote.price:.2f}")

        # Check quota after each call
        meta = client.last_response_metadata
        if meta and meta.quota.remaining is not None:
            print(f"  Quota remaining: {meta.quota.remaining}/{meta.quota.limit}")
            if meta.quota.is_overage:
                print("  ⚠ Running in overage mode (PAYG billing active)")

    except AuthenticationError as e:
        # API key invalid, expired, or revoked
        print(f"❌ Authentication failed: {e}")
        print(f"   Error code: {e.error_code}")
        print("   → Check your VECTRADE_API_KEY or create a new key at https://app.vectrade.io/keys")
        sys.exit(1)

    except RateLimitError as e:
        # Too many requests — respect retry_after
        print(f"⏳ Rate limited: {e}")
        print(f"   Retry after: {e.retry_after}s")
        print(f"   Limit: {e.limit} RPM")
        # In production: time.sleep(e.retry_after) and retry

    except QuotaExceededError as e:
        # Monthly quota exhausted
        print(f"📊 Quota exceeded: {e}")
        print(f"   Policy: {e.overage_policy}")
        if e.overage_policy == "BLOCK":
            print("   → Upgrade your plan or wait for quota reset")
        elif e.overage_policy == "THROTTLE":
            print("   → Requests throttled — reduce frequency")

    except PaymentRequiredError as e:
        # Feature requires paid plan (e.g., AI analysis on free tier)
        print(f"💳 Payment required: {e}")
        print("   → Upgrade at https://app.vectrade.io/billing")

    except NotFoundError as e:
        # Ticker not found
        print(f"🔍 Not found: {e}")

    except ValidationError as e:
        # Invalid request parameters
        print(f"⚠ Validation error: {e}")
        if e.details:
            print(f"   Details: {e.details}")

    except ServiceUnavailableError as e:
        # API is temporarily down (502/503)
        print(f"🔧 Service unavailable: {e}")
        print("   → Retry in a few minutes, check https://status.vectrade.io")

    except ServerError as e:
        # Other 5xx errors
        print(f"💥 Server error: {e} (request_id={e.request_id})")
        print("   → Report this request_id to support@vectrade.io")


def health_check():
    """Verify API connectivity before making requests."""
    client = VecTrade()

    try:
        status = client.health(timeout=5.0)
        print(f"API status: {status.get('status', 'unknown')}")
        if status.get("status") == "degraded":
            print("  ⚠ API is running in degraded mode — some endpoints may be slow")
    except ServiceUnavailableError:
        print("❌ API is down — cannot proceed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        sys.exit(1)


def quota_aware_batch():
    """Process a batch of tickers with quota awareness."""
    client = VecTrade()
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "TSLA", "META", "NFLX"]

    for ticker in tickers:
        try:
            quote = client.quotes.get(ticker)
            print(f"{quote.symbol}: ${quote.price:.2f}")

            # Check remaining quota
            meta = client.last_response_metadata
            if meta and meta.quota.remaining is not None and meta.quota.remaining < 10:
                print(f"  ⚠ Low quota: {meta.quota.remaining} calls remaining")
                print("  → Stopping to preserve quota for critical operations")
                break

        except QuotaExceededError:
            print(f"  Quota exhausted at {ticker} — stopping batch")
            break
        except RateLimitError as e:
            import time
            wait = e.retry_after or 2.0
            print(f"  Rate limited — waiting {wait}s...")
            time.sleep(wait)
            # Retry this ticker (simplified — production code would use a proper retry loop)


if __name__ == "__main__":
    print("=== Health Check ===")
    health_check()
    print("\n=== Production Error Handling ===")
    production_error_handling()
    print("\n=== Quota-Aware Batch ===")
    quota_aware_batch()
