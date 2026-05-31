# AI Agent Trading with VecTrade

> Build your own trading bot — from a Claude-powered AI agent to a simple cron script.

## Understanding the Architecture

**VecTrade does NOT run any AI/LLM for you.** We provide:
1. **Bot Trading API** — place orders, check portfolio, get KPIs (authenticated via `X-Bot-Key`)
2. **MCP Server** — exposes trading tools via standard [Model Context Protocol](https://modelcontextprotocol.io) so any AI agent can discover and use them
3. **Market Data API** — quotes, technicals, fundamentals, news (authenticated via `X-API-Key`)

**You provide** your own intelligence layer — whether that's:
- An AI agent (Claude, GPT, Gemini, local model)
- A rule-based script (Python, Node.js)
- A cron job running a strategy on a timer

```
┌──────────────────────────────┐
│  YOUR AGENT / SCRIPT         │  ← You build this (bring your own LLM or logic)
│  (Claude / GPT / Python /    │
│   Node / cron / anything)    │
└──────────┬───────────────────┘
           │
           │  Two connection options:
           │
     ┌─────┴─────────────────────────────────────────────────┐
     │                                                       │
     ▼                                                       ▼
┌────────────────────┐                            ┌────────────────────┐
│  VecTrade MCP      │  ← For AI agents that      │  VecTrade Bot API  │  ← For scripts that
│  Server            │    support MCP protocol     │  (REST/HTTP)       │    call HTTP directly
│  (mcp.vectrade.io) │                            │  (/api/v1/bot/*)   │
└────────────────────┘                            └────────────────────┘
         │                                                   │
         └──────────────── both talk to ─────────────────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │  VecTrade Trading  │
                        │  Engine            │
                        └────────────────────┘
```

## Three Approaches

| Approach | When to Use | Example |
|----------|-------------|---------|
| **AI Agent + MCP** | You want natural language interaction, Claude/GPT deciding trades | [`python_openai_agent.py`](python_openai_agent.py), [`typescript_claude_agent.ts`](typescript_claude_agent.ts) |
| **Script + Bot API** | Automated strategy, no AI needed, runs on schedule | [`cron_strategy_bot.py`](cron_strategy_bot.py) |
| **Claude Desktop** | Personal use — tell Claude to trade for you in chat | See [Quick Start](#quick-start-claude-desktop) below |

---

## Approach 1: Custom AI Agent + MCP

Your agent connects to VecTrade MCP server, discovers available tools, and uses them through the LLM's function-calling/tool-use capability.

### Python + OpenAI → [python_openai_agent.py](python_openai_agent.py)

```bash
pip install openai httpx
export OPENAI_API_KEY="sk-..."
export VECTRADE_API_KEY="vq_your_key"
export VECTRADE_BOT_KEY="tvt_your_bot_key"

python python_openai_agent.py
```

The agent:
1. Connects to VecTrade MCP server (discovers tools)
2. Converts MCP tools → OpenAI function format
3. Runs the standard tool-use loop: prompt → LLM → tool_calls → execute → LLM → response

### TypeScript + Claude → [typescript_claude_agent.ts](typescript_claude_agent.ts)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export VECTRADE_API_KEY="vq_your_key"
export VECTRADE_BOT_KEY="tvt_your_bot_key"

npx tsx typescript_claude_agent.ts "Buy 5 shares of AAPL"
```

Same pattern but using Anthropic's tool_use API.

---

## Approach 2: Script + Bot API (No AI)

If you don't need an LLM — just use the Bot API directly with `X-Bot-Key`:

### Cron Strategy Bot → [cron_strategy_bot.py](cron_strategy_bot.py)

```bash
# Run every 30 min during market hours
*/30 9-16 * * 1-5 cd /opt/bots && python cron_strategy_bot.py
```

This mean-reversion bot:
1. Checks watchlist for > 3% intraday drops with RSI < 30
2. Buys $200 worth of oversold stocks
3. Sells positions when RSI > 70
4. Logs everything for review

### Minimal API Example

```python
import httpx

bot = httpx.Client(
    base_url="https://vectrade.io/api/trade/v1/bot",
    headers={"X-Bot-Key": "tvt_your_key"},
)

# Check balance
account = bot.get("/account").json()
print(f"Balance: ${account['balance']}")

# Buy crypto (24/7, no market hours restriction)
order = bot.post("/orders", json={
    "symbol": "BTC-USD",
    "asset_type": "CRYPTO",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 0.01,
    "time_in_force": "GTC",
}).json()
print(f"Order {order['id']}: {order['status']}")
```

---

## Approach 3: Claude Desktop (Zero Code) {#quick-start-claude-desktop}

The easiest way — Claude Desktop has built-in MCP support:

### Step 1: Get Your Keys

1. Sign up at [vectrade.io](https://vectrade.io)
2. **Developer Settings** → **API Keys** → create a `vq_` key
3. **Developer Settings** → **Bot API Keys** → create a `tvt_` key

### Step 2: Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vectrade": {
      "command": "npx",
      "args": ["-y", "@vectrade/mcp-server"],
      "env": {
        "VECTRADE_API_KEY": "vq_your_key",
        "VECTRADE_BOT_KEY": "tvt_your_bot_key"
      }
    }
  }
}
```

### Step 3: Talk to Claude

> "Buy 10 shares of AAPL at market price"
> "Show my portfolio and tell me which positions are underwater"
> "Sell all my TSLA shares"

Claude handles tool discovery and execution automatically.

---

## Authentication

| Key Type | Header | Purpose | Format |
|----------|--------|---------|--------|
| API Key | `X-API-Key` | Market data access | `vq_...` |
| Bot Key | `X-Bot-Key` | Trading actions | `tvt_...` |
| JWT | `Authorization: Bearer` | Key management (create/revoke bot keys) | JWT token |

Your bot key authenticates ALL trades to your account. All bot-placed orders appear in your portfolio and count toward your leaderboard score.

## Plan Limits

| Plan | Bot Keys | API Calls/Month | Rate Limit |
|------|----------|-----------------|------------|
| Free | 1 | 10,000 | 20 RPM |
| Standard ($19/mo) | 5 | 100,000 | 120 RPM |
| Professional ($49/mo) | 25 | 500,000 | 300 RPM |

## Available Trading Tools (via MCP)

| Tool | Description |
|------|-------------|
| `place_order` | Buy/sell stocks, crypto, forex, ETFs |
| `cancel_order` | Cancel an open order |
| `get_orders` | List recent orders |
| `get_portfolio` | Cash balance + positions |
| `get_trading_kpi` | Sharpe, win rate, drawdown, rank |
| `get_bot_account` | Account info, key usage, plan |

Plus 16 market data tools: `get_quote`, `get_technicals`, `get_fundamentals`, `get_news`, `get_options_chain`, `get_earnings`, etc.

## Links

- [Bot Trading API Docs](https://docs.vectrade.io/guides/bot-trading)
- [MCP Server on npm](https://www.npmjs.com/package/@vectrade/mcp-server)
- [Python SDK](https://pypi.org/project/vectrade/)
- [Node SDK](https://www.npmjs.com/package/@vectrade/sdk)
- [Platform](https://vectrade.io)
