#!/bin/bash
# VecTrade API — cURL Quick Start
# Get your API key at https://vectrade.io/vtrade/developer
#
# Usage: VECTRADE_API_KEY=vq_your_key ./quickstart.sh

set -euo pipefail

API_KEY="${VECTRADE_API_KEY:-vq_test_YOUR_KEY_HERE}"
BASE="https://api.vectrade.io/v1/vq"

echo "=== Real-Time Quote (AAPL) ==="
curl -s "$BASE/quotes/AAPL" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

echo ""
echo "=== Batch Quotes (AAPL, GOOGL, MSFT) ==="
curl -s "$BASE/quotes/batch?symbols=AAPL,GOOGL,MSFT" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

echo ""
echo "=== Technical Analysis (AAPL) ==="
curl -s "$BASE/technical/AAPL" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

echo ""
echo "=== Analyst Ratings (AAPL) ==="
curl -s "$BASE/analyst/AAPL" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

echo ""
echo "=== Company Profile (AAPL) ==="
curl -s "$BASE/profile/AAPL" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

echo ""
echo "=== News (AAPL) ==="
curl -s "$BASE/news/AAPL" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

echo ""
echo "=== Options Chain (AAPL) ==="
curl -s "$BASE/options/AAPL/chain" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

echo ""
echo "=== Earnings (AAPL) ==="
curl -s "$BASE/earnings/AAPL" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

echo ""
echo "=== Sentiment (AAPL) ==="
curl -s "$BASE/sentiment/AAPL" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

echo ""
echo "=== Insider Trading (AAPL) ==="
curl -s "$BASE/insider/AAPL" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool
