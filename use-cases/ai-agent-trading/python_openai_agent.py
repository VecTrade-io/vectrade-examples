"""
VecTrade — AI Agent Trading via MCP Protocol (Python)

This example shows how to build YOUR OWN AI agent that connects to the
VecTrade MCP server to research markets and execute trades autonomously.

Architecture:
    ┌─────────────────────┐      MCP Protocol       ┌────────────────────┐
    │  Your Agent         │  ◄────────────────────►  │  VecTrade MCP      │
    │  (OpenAI/Anthropic/ │   JSON-RPC over HTTP     │  Server            │
    │   custom LLM)       │   X-API-Key header       │  (mcp.vectrade.io) │
    └─────────────────────┘                          └────────────────────┘
                                                              │
                                                              │ X-Bot-Key (from
                                                              │ server's env var)
                                                              ▼
                                                     ┌────────────────────┐
                                                     │  VecTrade Bot API  │
                                                     │  (trading engine)  │
                                                     └────────────────────┘

Key Points:
    - VecTrade does NOT run the LLM — YOU bring your own model
    - VecTrade MCP server exposes tools (get_quote, place_order, etc.)
    - Your agent calls these tools via the standard MCP protocol
    - The MCP server injects X-Bot-Key internally from VECTRADE_BOT_KEY env var
    - Your MCP client only sends X-API-Key for authentication

Requirements:
    pip install openai httpx

Environment:
    export OPENAI_API_KEY="sk-..."
    export VECTRADE_API_KEY="vq_your_market_data_key"

    # For self-hosted MCP server, also set on the SERVER:
    #   export VECTRADE_BOT_KEY="tvt_your_bot_key"
"""

import asyncio
import json
import os
from typing import Any

import httpx

# ─── Configuration ────────────────────────────────────────────────

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
VECTRADE_API_KEY = os.environ.get("VECTRADE_API_KEY", "")
MCP_BASE_URL = os.environ.get("VECTRADE_MCP_URL", "https://mcp.vectrade.io")

# Note: VECTRADE_BOT_KEY is configured on the MCP SERVER side (its env var),
# NOT sent by this client. The MCP server injects it when calling the Bot API.
# When using the hosted MCP server (mcp.vectrade.io), your bot key is linked
# to your API key account. For self-hosted MCP, set VECTRADE_BOT_KEY in the
# server's environment.

for name, val in [("OPENAI_API_KEY", OPENAI_API_KEY), ("VECTRADE_API_KEY", VECTRADE_API_KEY)]:
    if not val:
        raise RuntimeError(f"Set {name} environment variable")


# ═══════════════════════════════════════════════════════════════════
# STEP 1: MCP Client — connects to VecTrade MCP server
# ═══════════════════════════════════════════════════════════════════


class VecTradeMCPClient:
    """Minimal MCP client that talks to VecTrade MCP server via HTTP."""

    def __init__(self):
        self.session_id: str = ""
        self.tools: list[dict] = []
        self._request_id = 0
        self._client = httpx.AsyncClient(
            base_url=MCP_BASE_URL,
            headers={
                "X-API-Key": VECTRADE_API_KEY,
            },
            timeout=30.0,
        )

    async def connect(self) -> None:
        """Initialize MCP session and discover available tools."""
        # Initialize
        resp = await self._call_mcp("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "python-agent-example", "version": "1.0.0"},
        })
        self.session_id = resp.headers.get("mcp-session-id", "")
        print(f"[MCP] Connected — session: {self.session_id[:20]}...")

        # Discover tools
        tools_resp = await self._call_mcp("tools/list")
        self.tools = tools_resp.json()["result"]["tools"]
        print(f"[MCP] {len(self.tools)} tools available")

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Call an MCP tool and return the text result."""
        resp = await self._call_mcp("tools/call", {
            "name": name,
            "arguments": arguments,
        })
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"MCP tool error: {data['error']}")
        content = data["result"]["content"]
        return content[0]["text"] if content else ""

    async def _call_mcp(self, method: str, params: dict | None = None) -> httpx.Response:
        self._request_id += 1
        headers = {}
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        body: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
        }
        if params:
            body["params"] = params
        return await self._client.post("/mcp", headers=headers, json=body)

    def get_tools_for_llm(self) -> list[dict]:
        """Convert MCP tools to OpenAI function-calling format."""
        functions = []
        for tool in self.tools:
            functions.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}}),
                },
            })
        return functions

    async def close(self):
        await self._client.aclose()


# ═══════════════════════════════════════════════════════════════════
# STEP 2: AI Agent — your LLM with tool-calling capabilities
# ═══════════════════════════════════════════════════════════════════


class TradingAgent:
    """An AI trading agent powered by OpenAI + VecTrade MCP tools.

    You can replace OpenAI with any LLM that supports function calling:
    - Anthropic Claude (via messages API)
    - Local models (Ollama, vLLM)
    - Any provider that returns tool_calls
    """

    SYSTEM_PROMPT = """You are a trading assistant with access to VecTrade tools.
You can research markets (quotes, technicals, fundamentals, news) and execute trades.

Rules:
- Always check current price before placing orders
- For STOCK/ETF, orders only execute during US market hours (9:30-16:00 ET)
- CRYPTO trades execute 24/7
- Use LIMIT orders for better price control
- Never risk more than 5% of portfolio on a single trade
- Report what you did clearly to the user
"""

    def __init__(self, mcp: VecTradeMCPClient):
        self.mcp = mcp
        self.messages: list[dict] = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        self._openai_client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            timeout=60.0,
        )

    async def chat(self, user_message: str) -> str:
        """Send a message to the agent and get a response (with tool execution)."""
        self.messages.append({"role": "user", "content": user_message})

        # Run the agent loop (LLM → tool calls → LLM → ... → final response)
        while True:
            response = await self._call_llm()
            message = response["choices"][0]["message"]
            self.messages.append(message)

            # If no tool calls, we're done
            if not message.get("tool_calls"):
                return message["content"]

            # Execute each tool call via MCP
            for tool_call in message["tool_calls"]:
                fn = tool_call["function"]
                tool_name = fn["name"]
                tool_args = json.loads(fn["arguments"])

                print(f"  [Tool] {tool_name}({tool_args})")
                try:
                    result = await self.mcp.call_tool(tool_name, tool_args)
                except Exception as e:
                    result = f"Error: {e}"

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result,
                })

    async def _call_llm(self) -> dict:
        """Call OpenAI chat completions with tools."""
        resp = await self._openai_client.post("/chat/completions", json={
            "model": "gpt-4o",
            "messages": self.messages,
            "tools": self.mcp.get_tools_for_llm(),
            "tool_choice": "auto",
        })
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._openai_client.aclose()


# ═══════════════════════════════════════════════════════════════════
# STEP 3: Run the agent
# ═══════════════════════════════════════════════════════════════════


async def main():
    mcp = VecTradeMCPClient()
    await mcp.connect()

    agent = TradingAgent(mcp)

    print("\n" + "=" * 60)
    print("VecTrade AI Trading Agent (type 'quit' to exit)")
    print("=" * 60)
    print("\nExamples:")
    print('  "Check AAPL price and buy 5 shares if under $200"')
    print('  "Show my portfolio and KPIs"')
    print('  "Buy $1000 of BTC-USD"')
    print()

    try:
        while True:
            user_input = input("You: ").strip()
            if not user_input or user_input.lower() in ("quit", "exit"):
                break

            print("\nAgent thinking...\n")
            response = await agent.chat(user_input)
            print(f"\nAgent: {response}\n")
    finally:
        await agent.close()
        await mcp.close()


if __name__ == "__main__":
    asyncio.run(main())
