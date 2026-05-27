"""VecTrade MCP Server — Python Client Example.

Demonstrates connecting to the VecTrade MCP server programmatically
using the MCP Python SDK. Useful for building AI agents that
need financial data tools.

Prerequisites:
    pip install mcp httpx
    export VECTRADE_API_KEY=vq_your_key_here
"""

import asyncio
import os
import json
import httpx


async def main():
    """Call VecTrade MCP server tools via HTTP (SSE transport)."""
    api_key = os.environ.get("VECTRADE_API_KEY")
    if not api_key:
        print("Set VECTRADE_API_KEY environment variable")
        return

    base_url = "https://mcp.vectrade.io"
    headers = {"X-API-Key": api_key}

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Initialize the MCP session
        print("=== Connecting to VecTrade MCP Server ===")
        init_resp = await client.post(
            f"{base_url}/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "example-client", "version": "1.0.0"},
                },
            },
        )
        init_data = init_resp.json()
        session_id = init_resp.headers.get("mcp-session-id", "")
        print(f"  Server: {init_data['result']['serverInfo']['name']}")
        print(f"  Session: {session_id[:20]}...")

        # 2. List available tools
        tools_resp = await client.post(
            f"{base_url}/mcp",
            headers={**headers, "mcp-session-id": session_id},
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        )
        tools = tools_resp.json()["result"]["tools"]
        print(f"\n  Available tools ({len(tools)}):")
        for tool in tools:
            print(f"    • {tool['name']}: {tool['description'][:60]}")

        # 3. Call a tool
        print("\n=== Calling get_quote for AAPL ===")
        call_resp = await client.post(
            f"{base_url}/mcp",
            headers={**headers, "mcp-session-id": session_id},
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_quote",
                    "arguments": {"symbol": "AAPL"},
                },
            },
        )
        result = call_resp.json()["result"]["content"][0]["text"]
        data = json.loads(result)
        print(f"  AAPL: ${data['price']:.2f} ({data.get('change_percent', data.get('change_pct', 0)):+.2f}%)")

        # 4. Call technicals tool
        print("\n=== Calling get_technicals for NVDA ===")
        tech_resp = await client.post(
            f"{base_url}/mcp",
            headers={**headers, "mcp-session-id": session_id},
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "get_technicals",
                    "arguments": {"symbol": "NVDA"},
                },
            },
        )
        tech_result = json.loads(tech_resp.json()["result"]["content"][0]["text"])
        print(f"  Technical Score: {tech_result.get('technical_score')}")
        print(f"  Summary: {tech_result.get('summary')}")


if __name__ == "__main__":
    asyncio.run(main())
