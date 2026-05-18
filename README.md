# VecTrade Examples

[![CI](https://github.com/VecTrade-io/vectrade-examples/actions/workflows/ci.yml/badge.svg)](https://github.com/VecTrade-io/vectrade-examples/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/VecTrade-io/vectrade-examples)](LICENSE)

Runnable examples, templates, and use cases demonstrating [VecTrade](https://vectrade.io) SDK usage across Python, TypeScript, and cURL.

## Quick Start

```bash
# Set your API key
export VECTRADE_API_KEY=vq_test_...

# Python
cd python/ && pip install vectrade && python quickstart.py

# TypeScript
cd typescript/ && npm install @vectrade/sdk tsx && npx tsx quickstart.ts

# cURL
cd curl/ && bash quickstart.sh
```

## Example Catalog

### Python

| Example | Description | Key Features |
|---------|-------------|--------------|
| [`quickstart.py`](python/quickstart.py) | Basic quote retrieval + AI analysis | Quotes, Batch, AI Streaming |
| [`streaming.py`](python/streaming.py) | Streaming AI responses | AI Stream, Real-time output |
| [`portfolio_analysis.py`](python/portfolio_analysis.py) | Risk metrics with finkit | Sharpe, Sortino, VaR, Screening |
| [`async_example.py`](python/async_example.py) | Async client for concurrency | AsyncVecTrade, gather, Quota |
| [`error_handling.py`](python/error_handling.py) | Production error patterns | All exception types, Retry |
| [`langchain_agent.py`](python/langchain_agent.py) | LangChain multi-agent research | LangChain, Tools, Agent |

### TypeScript

| Example | Description | Key Features |
|---------|-------------|--------------|
| [`quickstart.ts`](typescript/quickstart.ts) | Basic usage with typed responses | Quotes, Batch, AI Stream |
| [`streaming.ts`](typescript/streaming.ts) | Async generator streaming | AsyncGenerator, stdout |
| [`error_handling.ts`](typescript/error_handling.ts) | Typed exception handling | All error classes, Health |
| [`vercel-ai-chatbot/`](typescript/vercel-ai-chatbot/) | AI chatbot with VecTrade tools | Vercel AI SDK, Next.js |

### cURL

| Example | Description |
|---------|-------------|
| [`quickstart.sh`](curl/quickstart.sh) | Raw HTTP API calls |

### Use Cases

| Use Case | Description | Complexity |
|----------|-------------|------------|
| [`earnings-tracker/`](use-cases/earnings-tracker/) | Monitor portfolio earnings calendar | Intermediate |
| [`momentum-scanner/`](use-cases/momentum-scanner/) | Screen high-momentum stocks with technicals | Advanced |

### Templates

| Template | Stack | Description |
|----------|-------|-------------|
| [`nextjs-dashboard/`](templates/nextjs-dashboard/) | Next.js 15 + React 19 | Full-stack dashboard starter |
| [`python-project/`](templates/python-project/) | Python + dotenv | Minimal Python project starter |

## Prerequisites

- **Python** >= 3.9 with `pip`
- **Node.js** >= 20 with `npm` (for TypeScript examples)
- **VecTrade API key** — get one at [app.vectrade.io/keys](https://app.vectrade.io/keys)
- **[finkit](https://github.com/VecTrade-io/finkit)** (optional, for `portfolio_analysis.py`)

## Running Examples

### Python

```bash
cd python/
pip install vectrade finkit  # finkit optional
python quickstart.py
```

### TypeScript

```bash
cd typescript/
npm install @vectrade/sdk tsx
npx tsx quickstart.ts
```

### Use Cases

Each use case has its own README with specific setup instructions:

```bash
cd use-cases/momentum-scanner/
cat README.md
pip install vectrade finkit
python main.py
```

### Templates

Templates are complete project starters — copy and customize:

```bash
cp -r templates/nextjs-dashboard/ ~/my-dashboard
cd ~/my-dashboard
npm install
cp .env.example .env.local  # add your API key
npm run dev
```

## VecTrade Ecosystem

| Package | Description |
|---------|-------------|
| [`vectrade`](https://github.com/VecTrade-io/vectrade-python) | Python SDK |
| [`@vectrade/sdk`](https://github.com/VecTrade-io/vectrade-node) | TypeScript SDK |
| [`@vectrade/ai-provider`](https://github.com/VecTrade-io/vectrade-ai-provider) | Vercel AI SDK provider |
| [`vectrade` CLI](https://github.com/VecTrade-io/vectrade-cli) | Command-line interface |
| [`finkit`](https://github.com/VecTrade-io/finkit) | Financial computations (no API key needed) |
| [`@vectrade/mcp`](https://github.com/VecTrade-io/vectrade-mcp) | Model Context Protocol server |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new examples.

## License

MIT — see [LICENSE](LICENSE).
