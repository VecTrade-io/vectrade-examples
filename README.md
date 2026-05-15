# Examples

[![License](https://img.shields.io/github/license/VecTrade-io/vectrade-examples)](LICENSE)

Runnable examples demonstrating VecTrade SDK usage.

## Quick Start

```bash
# Set your API key
export VECTRADE_API_KEY=vq_test_...

# Python
cd python/ && pip install vectrade && python quickstart.py

# TypeScript
cd typescript/ && npm install && npx tsx quickstart.ts
```

## Structure

```
examples/
├── python/
│   ├── quickstart.py          # Basic quote + AI analysis
│   ├── streaming.py           # Streaming AI responses
│   ├── portfolio_analysis.py  # Portfolio risk metrics with finkit
│   ├── error_handling.py      # Error handling & retry patterns
│   └── async_example.py       # Async client usage
├── typescript/
│   ├── quickstart.ts          # Basic usage
│   ├── streaming.ts           # Streaming with AsyncGenerator
│   ├── error_handling.ts      # Error handling & typed exceptions
│   └── nextjs-dashboard/      # Full Next.js integration example
└── curl/
    └── quickstart.sh          # Raw API calls with curl
```

## Documentation

Full SDK docs at [docs.vectrade.io](https://docs.vectrade.io).

## License

MIT — see [LICENSE](LICENSE).
