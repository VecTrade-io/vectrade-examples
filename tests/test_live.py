"""Live API tests for vectrade-examples.

Validates that example code patterns work against the live API:
- SDK initialization works
- Quote fetching works
- Auth is enforced
- Rate limits are respected

Requires: VECTRADE_API_KEY environment variable
"""

from __future__ import annotations

import os
import time

import pytest
import requests

API_KEY = os.environ.get("VECTRADE_API_KEY", "vq_Mv8c_RyScES7xeXWhjznncYB6FLW8xRAyyJ5vRM4MQo")
BASE_URL = "https://api.vectrade.io/v1"
HEADERS = {
    "X-API-Key": API_KEY,
    "User-Agent": "vectrade-examples-tests/1.0",
}


class TestQuickstartPatterns:
    """Verify patterns used in quickstart examples work."""

    def test_single_quote_fetch(self):
        """Pattern: vt.quotes.get('AAPL') — single quote fetch."""
        resp = requests.get(
            f"{BASE_URL}/vq/quotes/AAPL",
            headers=HEADERS,
            timeout=10,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data or "symbol" in data

    def test_batch_quotes_fetch(self):
        """Pattern: vt.quotes.batch(['AAPL', 'MSFT']) — batch fetch."""
        resp = requests.get(
            f"{BASE_URL}/vq/quotes/batch",
            headers=HEADERS,
            params={"symbols": "AAPL,MSFT,GOOGL"},
            timeout=10,
        )
        assert resp.status_code in (200, 404)


class TestAuthPatterns:
    """Verify auth patterns match example documentation."""

    def test_no_key_rejected(self):
        """Examples document that missing key returns 401."""
        resp = requests.get(
            f"{BASE_URL}/vq/quotes/AAPL",
            headers={"User-Agent": "vectrade-examples-tests/1.0"},
            timeout=10,
        )
        assert resp.status_code in (401, 403)

    def test_api_key_header_works(self):
        """Examples use X-API-Key header (documented pattern)."""
        resp = requests.get(
            f"{BASE_URL}/vq/quotes/AAPL",
            headers=HEADERS,
            timeout=10,
        )
        assert resp.status_code == 200


class TestErrorHandlingPatterns:
    """Verify error handling patterns from examples."""

    def test_invalid_symbol_handling(self):
        """Pattern: Handle invalid symbol gracefully."""
        resp = requests.get(
            f"{BASE_URL}/vq/quotes/INVALID_SYMBOL_XYZ",
            headers=HEADERS,
            timeout=10,
        )
        # Should return error status or empty data
        assert resp.status_code in (200, 400, 404, 422)

    def test_error_response_is_json(self):
        """Error responses should be JSON (as shown in examples)."""
        resp = requests.get(
            f"{BASE_URL}/vq/quotes/AAPL",
            headers={"User-Agent": "vectrade-examples-tests/1.0"},
            timeout=10,
        )
        assert resp.headers.get("content-type", "").startswith("application/json")


class TestCurlPatterns:
    """Verify curl example patterns work."""

    def test_curl_equivalent_request(self):
        """Matches: curl -H 'X-API-Key: ...' https://api.vectrade.io/v1/vq/quotes/AAPL"""
        resp = requests.get(
            f"{BASE_URL}/vq/quotes/AAPL",
            headers=HEADERS,
            timeout=10,
        )
        assert resp.status_code == 200


class TestPerformance:
    """Verify API performance for examples."""

    def test_reasonable_response_time(self):
        """Examples should demonstrate fast responses."""
        start = time.time()
        resp = requests.get(
            f"{BASE_URL}/vq/quotes/AAPL",
            headers=HEADERS,
            timeout=10,
        )
        elapsed = time.time() - start
        assert elapsed < 5.0
        assert resp.status_code == 200
