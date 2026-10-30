"""Live integration tests for VecTrade API examples.

Run with: VECTRADE_API_KEY=vq_your_key pytest tests/test_live.py -v

These tests hit the real API at https://api.vectrade.io.
"""

import os
import subprocess
import pytest
import httpx

API_KEY = os.environ.get("VECTRADE_API_KEY", "")
BASE = "https://api.vectrade.io/v1/vq"
HEADERS = {"X-API-Key": API_KEY}

pytestmark = pytest.mark.skipif(not API_KEY, reason="VECTRADE_API_KEY not set")


class TestCurlEndpoints:
    """Verify all endpoints used by curl/quickstart.sh work."""

    @pytest.fixture(autouse=True)
    def client(self):
        self._client = httpx.Client(base_url=BASE, headers=HEADERS, timeout=15)
        yield
        self._client.close()

    def test_quote(self):
        r = self._client.get("/quotes/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "ticker" in data or "symbol" in data
        assert "price" in data

    def test_batch_quotes(self):
        r = self._client.get("/quotes/batch", params={"tickers": "AAPL,MSFT"})
        assert r.status_code == 200

    def test_technical(self):
        r = self._client.get("/technical/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "technical_score" in data
        assert "indicators" in data

    def test_analyst(self):
        r = self._client.get("/analyst/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "ratings" in data
        assert "consensus" in data

    def test_profile(self):
        r = self._client.get("/profile/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "company" in data or "ticker" in data

    def test_news(self):
        r = self._client.get("/news/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "articles" in data

    def test_options_chain(self):
        r = self._client.get("/options/AAPL/chain")
        assert r.status_code == 200
        data = r.json()
        assert "calls" in data or "ticker" in data

    def test_earnings(self):
        r = self._client.get("/earnings/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "ticker" in data

    def test_sentiment(self):
        r = self._client.get("/sentiment/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "sentiment_score" in data or "signal" in data

    def test_insider(self):
        r = self._client.get("/insider/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "trades" in data or "ticker" in data

    def test_fundamentals(self):
        r = self._client.get("/fundamentals/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "price" in data or "ticker" in data

    def test_financial_statements(self):
        r = self._client.get("/fundamentals/AAPL/statements")
        assert r.status_code == 200
        data = r.json()
        assert "income_statement" in data

    def test_upgrades_downgrades(self):
        r = self._client.get("/upgrades-downgrades/AAPL")
        assert r.status_code == 200
        data = r.json()
        assert "ticker" in data

    def test_historical_prices(self):
        r = self._client.get("/quotes/AAPL/history", params={"interval": "1d", "period": "1mo"})
        assert r.status_code == 200


class TestCurlScript:
    """Test that the curl quickstart script runs without errors."""

    def test_curl_quickstart_runs(self):
        result = subprocess.run(
            ["bash", "curl/quickstart.sh"],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "VECTRADE_API_KEY": API_KEY},
        )
        assert result.returncode == 0, f"Script failed:\n{result.stderr}"
        assert "Real-Time Quote" in result.stdout
        assert "Technical Analysis" in result.stdout
