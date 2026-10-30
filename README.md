# VecTrade Examples

[![CI](https://github.com/VecTrade-io/vectrade-examples/actions/workflows/ci.yml/badge.svg)](https://github.com/VecTrade-io/vectrade-examples/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/VecTrade-io/vectrade-examples)](LICENSE)

Runnable examples, templates, and use cases demonstrating [VecTrade](https://vectrade.io) SDK usage across Python, TypeScript, and cURL.

## Quick Start

```bash
# 1. Get your API key at https://vectrade.io/vtrade/developer
export VECTRADE_API_KEY=vq_your_key_here

# 2. Try the cURL quickstart (no SDK needed)
bash curl/quickstart.sh

# 3. Or use the Python SDK
cd python/ && pip install vectrade && python quickstart.py

# 4. Or use the TypeScript SDK
cd typescript/ && npm install @vectrade/sdk tsx && npx tsx quickstart.ts
```

## API Base URL & Authentication

All VecTrade API requests use:

```
Base URL: https://api.vectrade.io/v1/vq
Auth Header: X-API-Key: vq_your_key_here
```

## Available Endpoints (16)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/quotes/{symbol}` | GET | Real-time stock quote |
| `/quotes/batch?tickers=A,B,C` | GET | Multiple quotes (up to 20) |
| `/quotes/{symbol}/history?period=5d` | GET | Historical OHLCV data |
| `/technical/{symbol}` | GET | Technical indicators (RSI, MACD, Bollinger, S/R) |
| `/fundamentals/{symbol}` | GET | Company fundamentals (market cap, SMAs) |
| `/fundamentals/{symbol}/statements` | GET | Income, balance sheet, cash flow |
| `/profile/{symbol}` | GET | Company profile, sector, description |
| `/news/{symbol}` | GET | Latest news articles |
| `/sentiment/{symbol}` | GET | Sentiment score & social mentions |
| `/analyst-consensus/{symbol}` | GET | Analyst consensus rating |
| `/analyst-targets/{symbol}` | GET | Price target estimates |
| `/upgrades-downgrades/{symbol}` | GET | Analyst upgrades/downgrades |
| `/earnings/{symbol}` | GET | Earnings history & estimates |
| `/insider/{symbol}` | GET | Insider trading activity |
| `/options/{symbol}/chain` | GET | Options chain (calls & puts) |
| `/etf/{symbol}` | GET | ETF info, holdings, sector weights |

## Example Catalog

### Python

| Example | Description | Key Features |
|---------|-------------|--------------|
| [`quickstart.py`](python/quickstart.py) | Complete SDK walkthrough — all 12 resources | Quotes, Profile, Fundamentals, Technicals, News, Sentiment, Analyst, Earnings, Insider, Options, Historical, ETF |
| [`async_example.py`](python/async_example.py) | Async client for concurrent API calls | AsyncVecTrade, gather, parallel requests |
| [`portfolio_analysis.py`](python/portfolio_analysis.py) | Multi-stock portfolio analysis | Technicals, Analyst, Insider, scoring |
| [`bot_trading.py`](python/bot_trading.py) | Bot API client — place orders, check portfolio | X-Bot-Key auth, order lifecycle |
| [`mcp_client.py`](python/mcp_client.py) | MCP server client — call tools programmatically | MCP protocol, tool discovery |
| [`error_handling.py`](python/error_handling.py) | Production error handling patterns | All exception types, retry, fallback |

### TypeScript

| Example | Description | Key Features |
|---------|-------------|--------------|
| [`quickstart.ts`](typescript/quickstart.ts) | Complete SDK walkthrough — all 12 resources | Quotes, Profile, Fundamentals, Technicals, News, Sentiment, Analyst, Earnings, Insider, Options, Historical, ETF |
| [`streaming.ts`](typescript/streaming.ts) | Real-time market monitor | Batch quotes, big mover detection, deep dive |
| [`error_handling.ts`](typescript/error_handling.ts) | Typed exception handling | All error classes, retry, recovery |
| [`ai_provider.ts`](typescript/ai_provider.ts) | AI chatbot with VecTrade tools | Vercel AI SDK integration |

### cURL

| Example | Description |
|---------|-------------|
| [`quickstart.sh`](curl/quickstart.sh) | All API endpoints demonstrated with raw HTTP calls |

### Use Cases

| Use Case | Description | Complexity |
|----------|-------------|------------|
| [`ai-agent-trading/`](use-cases/ai-agent-trading/) | AI agent + MCP trading, cron strategy, direct API | Intermediate–Advanced |
| [`earnings-tracker/`](use-cases/earnings-tracker/) | Monitor portfolio earnings calendar | Intermediate |
| [`momentum-scanner/`](use-cases/momentum-scanner/) | Screen high-momentum stocks with technicals | Advanced |

### Templates

| Template | Stack | Description |
|----------|-------|-------------|
| [`nextjs-dashboard/`](templates/nextjs-dashboard/) | Next.js 15 + React 19 | Full-stack dashboard starter |
| [`python-project/`](templates/python-project/) | Python + dotenv | Minimal Python project starter |

## Prerequisites

- **VecTrade API key** — get one at [vectrade.io/vtrade/developer](https://vectrade.io/vtrade/developer)
- **Python** >= 3.9 with `pip` (for Python examples)
- **Node.js** >= 20 with `npm` (for TypeScript examples)

## Running Examples

### cURL (simplest — no dependencies)

```bash
export VECTRADE_API_KEY=vq_your_key_here
bash curl/quickstart.sh
```

### Python

```bash
pip install vectrade
export VECTRADE_API_KEY=vq_your_key_here
python python/quickstart.py
```

### TypeScript

```bash
cd typescript/
npm install @vectrade/sdk tsx
export VECTRADE_API_KEY=vq_your_key_here
npx tsx quickstart.ts
```

### Use Cases

Each use case has its own README:

```bash
cd use-cases/momentum-scanner/
pip install vectrade
python main.py
```

## MCP Server (for AI Assistants)

VecTrade also provides an MCP (Model Context Protocol) server that gives AI assistants like Claude, Cursor, and VS Code Copilot access to all financial data tools.

### Hosted (recommended)

```json
{
  "mcpServers": {
    "vectrade": {
      "url": "https://mcp.vectrade.io/sse",
      "headers": {
        "X-API-Key": "vq_your_key_here"
      }
    }
  }
}
```

### Local (stdio)

```json
{
  "mcpServers": {
    "vectrade": {
      "command": "npx",
      "args": ["-y", "@vectrade/mcp-server"],
      "env": {
        "VECTRADE_API_KEY": "vq_your_key_here"
      }
    }
  }
}
```

**Available MCP Tools:** `get_quote`, `get_batch_quotes`, `get_historical_prices`, `get_fundamentals`, `get_financial_statements`, `get_company_profile`, `get_earnings`, `get_technicals`, `get_news`, `get_sentiment`, `get_analyst_ratings`, `get_insider_trading`, `get_upgrades_downgrades`, `get_options_chain`, `get_etf`, `place_order`, `cancel_order`, `get_orders`, `get_portfolio`, `get_trading_kpi`, `get_bot_account`

<details>
<summary>Bot Trading via MCP (requires Bot API key)</summary>

Add `VECTRADE_BOT_KEY` to enable trading tools:

```json
{
  "mcpServers": {
    "vectrade": {
      "command": "npx",
      "args": ["-y", "@vectrade/mcp-server"],
      "env": {
        "VECTRADE_API_KEY": "vq_your_key_here",
        "VECTRADE_BOT_KEY": "tvt_your_bot_key"
      }
    }
  }
}
```

Trading tools: `place_order`, `cancel_order`, `get_orders`, `get_portfolio`, `get_trading_kpi`, `get_bot_account`

See [`use-cases/ai-agent-trading/`](use-cases/ai-agent-trading/) for full examples.
</details>

## VecTrade Ecosystem

| Package | Description |
|---------|-------------|
| [`vectrade`](https://github.com/VecTrade-io/vectrade-python) | Python SDK |
| [`@vectrade/sdk`](https://github.com/VecTrade-io/vectrade-node) | TypeScript/Node.js SDK |
| [`@vectrade/mcp-server`](https://github.com/VecTrade-io/vectrade-mcp) | MCP Server for AI assistants |
| [`@vectrade/ai-provider`](https://github.com/VecTrade-io/vectrade-ai-provider) | Vercel AI SDK provider |
| [Docs](https://docs.vectrade.io) | Full API documentation |

## Running Tests

```bash
# Live integration tests (requires API key)
export VECTRADE_API_KEY=vq_your_key_here
pip install httpx pytest
pytest tests/test_live.py -v
```

## License

[MIT](LICENSE) — see [LICENSE](LICENSE) for details.
