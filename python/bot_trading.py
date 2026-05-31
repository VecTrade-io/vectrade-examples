"""
VecTrade Bot Trading — Python Example

This example shows how to use the Bot API directly (without MCP).
Useful for building custom trading bots or integrating with other frameworks.

Requirements:
    pip install httpx

Setup:
    export VECTRADE_BOT_KEY="tvt_your_key_here"
"""

import os
import httpx
from typing import Optional

BOT_API_BASE = os.getenv("VECTRADE_BOT_API_BASE", "https://vectrade.io/api/trade/v1/bot")
BOT_KEY = os.getenv("VECTRADE_BOT_KEY", "")

if not BOT_KEY:
    raise RuntimeError("Set VECTRADE_BOT_KEY environment variable")


class VecTradeBot:
    """Simple VecTrade Bot API client."""

    def __init__(self, bot_key: str = BOT_KEY, base_url: str = BOT_API_BASE):
        self.client = httpx.Client(
            base_url=base_url,
            headers={
                "X-Bot-Key": bot_key,
                "User-Agent": "vectrade-bot-example/1.0",
            },
            timeout=15.0,
        )

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        asset_type: str = "STOCK",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> dict:
        """Place a trade order."""
        payload = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "quantity": quantity,
            "order_type": order_type.upper(),
            "asset_type": asset_type.upper(),
            "time_in_force": "GTC",
        }
        if limit_price:
            payload["limit_price"] = limit_price
        if stop_price:
            payload["stop_price"] = stop_price

        resp = self.client.post("/orders", json=payload)
        resp.raise_for_status()
        return resp.json()

    def cancel_order(self, order_id: str) -> None:
        """Cancel an open order."""
        resp = self.client.delete(f"/orders/{order_id}")
        resp.raise_for_status()

    def get_orders(self, status: Optional[str] = None, limit: int = 20) -> list:
        """List recent orders."""
        params = {"limit": str(limit)}
        if status:
            params["status"] = status.upper()
        resp = self.client.get("/orders", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_portfolio(self) -> dict:
        """Get portfolio — cash + positions."""
        resp = self.client.get("/portfolio")
        resp.raise_for_status()
        return resp.json()

    def get_kpi(self) -> dict:
        """Get trading KPIs."""
        resp = self.client.get("/kpi")
        resp.raise_for_status()
        return resp.json()

    def get_account(self) -> dict:
        """Get account info."""
        resp = self.client.get("/account")
        resp.raise_for_status()
        return resp.json()


# ─── Example usage ────────────────────────────────────────────────

if __name__ == "__main__":
    bot = VecTradeBot()

    # Check account
    account = bot.get_account()
    print(f"Bot: {account['display_name']} | Balance: ${account['balance']}")
    print(f"Plan: {account.get('plan', 'N/A')} | Keys: {account.get('bot_keys_used', '?')}/{account.get('bot_keys_limit', '?')}")
    print()

    # View portfolio
    portfolio = bot.get_portfolio()
    print(f"Equity: ${portfolio['total_equity']}")
    for pos in portfolio.get("positions", []):
        print(f"  {pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_cost']}")
    print()

    # Place a market buy (use CRYPTO — works 24/7, no market hours restriction)
    order = bot.place_order("BTC-USD", "BUY", 0.001, asset_type="CRYPTO")
    print(f"Order placed: {order['id']} — {order['status']}")
    if order["status"] == "FILLED":
        print(f"  Filled @ ${order['filled_price']}")
    print()

    # Check KPIs
    kpi = bot.get_kpi()
    print(f"Return: {kpi['total_return_pct']}% | Sharpe: {kpi['sharpe_ratio']}")
    print(f"Win Rate: {kpi['win_rate']}% | Rank: #{kpi.get('rank', 'N/A')}")
