#!/bin/bash
# VecTrade API — cURL Quick Start
# Replace YOUR_API_KEY with your actual key

API_KEY="vq_test_YOUR_KEY_HERE"
BASE="https://api.vectrade.io/v1"

echo "=== Get Quote ==="
curl -s "$BASE/vq/quotes/AAPL" \
  -H "Authorization: Bearer $API_KEY" | python3 -m json.tool

echo ""
echo "=== Batch Quotes ==="
curl -s "$BASE/vq/quotes/batch?symbols=AAPL,GOOGL,MSFT" \
  -H "Authorization: Bearer $API_KEY" | python3 -m json.tool

echo ""
echo "=== AI Analysis (non-streaming) ==="
curl -s "$BASE/vq/ai/analyze" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze AAPL for long-term hold", "stream": false}' | python3 -m json.tool

echo ""
echo "=== AI Analysis (streaming) ==="
curl -N "$BASE/vq/ai/analyze" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Brief outlook for NVDA", "stream": true}'
