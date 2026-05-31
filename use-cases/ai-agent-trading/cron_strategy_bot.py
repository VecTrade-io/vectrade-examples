"""
VecTrade — Cron Strategy Bot (No AI Required)

This example shows how to build a simple automated trading strategy
that runs on a schedule (cron/systemd timer) using ONLY the Bot API.
No LLM, no MCP — just Python + HTTP + your bot key.

Architecture:
    ┌─────────────────────┐    X-Bot-Key     ┌──────────────────┐
    │  Your Script        │ ─────────────────►│  VecTrade Bot    │
    │  (cron/systemd/     │                   │  Trading API     │
    │   cloud scheduler)  │ ◄─────────────────│                  │
    └─────────────────────┘   JSON responses  └──────────────────┘

Use Case: Mean Reversion Bot
    - Runs every 30 minutes via cron
    - Checks if any of your watchlist stocks dropped > 3% intraday
    - If RSI < 30, buys $200 worth
    - If RSI > 70 and you hold it, sells

Crontab entry:
    */30 9-16 * * 1-5 cd /path/to/this && python cron_strategy_bot.py

Requirements:
    pip install httpx

Environment:
    export VECTRADE_BOT_KEY="tvt_your_bot_key"
    export VECTRADE_API_KEY="vq_your_key"  # for market data
"""

import os
import sys
import logging
from datetime import datetime
from decimal import Decimal

import httpx

# ─── Configuration ────────────────────────────────────────────────

BOT_KEY = os.environ.get("VECTRADE_BOT_KEY", "")
API_KEY = os.environ.get("VECTRADE_API_KEY", "")
BOT_API_BASE = os.environ.get("VECTRADE_BOT_API_BASE", "https://vectrade.io/api/trade/v1/bot")
DATA_API_BASE = os.environ.get("VECTRADE_DATA_API_BASE", "https://api.vectrade.io/v1")

if not BOT_KEY or not API_KEY:
    print("Set VECTRADE_BOT_KEY and VECTRADE_API_KEY environment variables")
    sys.exit(1)

# Strategy parameters
WATCHLIST = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"]
BUY_AMOUNT_USD = 200.0  # Invest $200 per signal
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
INTRADAY_DROP_THRESHOLD = -3.0  # percent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("cron_strategy.log"),
    ],
)
log = logging.getLogger("cron-bot")

# ─── API Clients ─────────────────────────────────────────────────

bot_client = httpx.Client(
    base_url=BOT_API_BASE,
    headers={"X-Bot-Key": BOT_KEY},
    timeout=15.0,
)

data_client = httpx.Client(
    base_url=DATA_API_BASE,
    headers={"X-API-Key": API_KEY},
    timeout=15.0,
)


# ─── Market Data Helpers ──────────────────────────────────────────

def get_quote(symbol: str) -> dict | None:
    """Fetch current price and change percent."""
    try:
        resp = data_client.get(f"/vq/quotes/{symbol}")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        log.error(f"Quote fetch failed for {symbol}: {e}")
        return None


def get_technicals(symbol: str) -> dict | None:
    """Fetch RSI and other technical indicators."""
    try:
        resp = data_client.get(f"/vq/technical/{symbol}")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        log.error(f"Technicals fetch failed for {symbol}: {e}")
        return None


# ─── Bot Trading Helpers ──────────────────────────────────────────

def get_portfolio() -> dict | None:
    """Fetch portfolio positions and balance."""
    try:
        resp = bot_client.get("/portfolio")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        log.error(f"Portfolio fetch failed: {e}")
        return None


def place_order(symbol: str, side: str, quantity: float) -> dict | None:
    """Place a market order."""
    try:
        resp = bot_client.post("/orders", json={
            "symbol": symbol,
            "asset_type": "STOCK",
            "side": side,
            "order_type": "MARKET",
            "quantity": quantity,
            "time_in_force": "DAY",
        })
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        log.error(f"Order failed for {symbol} {side}: {e}")
        return None


# ─── Strategy Logic ───────────────────────────────────────────────

def run_strategy():
    """Main strategy: mean reversion on watchlist."""
    log.info(f"Strategy run started — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Get current portfolio to know what we hold
    portfolio = get_portfolio()
    if not portfolio:
        log.error("Cannot fetch portfolio — aborting")
        return

    held_symbols = {
        p["symbol"]: float(p["quantity"])
        for p in portfolio.get("positions", [])
    }
    balance = float(portfolio["balance"])
    log.info(f"Balance: ${balance:,.2f} | Positions: {len(held_symbols)}")

    buy_signals = []
    sell_signals = []

    for symbol in WATCHLIST:
        quote = get_quote(symbol)
        if not quote:
            continue

        price = float(quote.get("price", 0))
        change_pct = float(quote.get("change_percent", 0))

        tech = get_technicals(symbol)
        rsi = float(tech.get("rsi_14", 50)) if tech else 50.0

        log.info(f"  {symbol}: ${price:.2f} ({change_pct:+.1f}%) RSI={rsi:.1f}")

        # BUY signal: dropped > 3% intraday AND RSI oversold
        if change_pct <= INTRADAY_DROP_THRESHOLD and rsi < RSI_OVERSOLD:
            shares = int(BUY_AMOUNT_USD / price)
            if shares > 0 and balance >= shares * price:
                buy_signals.append((symbol, shares, price, rsi))

        # SELL signal: RSI overbought AND we hold it
        elif rsi > RSI_OVERBOUGHT and symbol in held_symbols:
            sell_signals.append((symbol, held_symbols[symbol], price, rsi))

    # Execute buy signals
    for symbol, shares, price, rsi in buy_signals:
        log.info(f"  BUY SIGNAL: {symbol} — {shares} shares @ ~${price:.2f} (RSI={rsi:.1f})")
        order = place_order(symbol, "BUY", shares)
        if order:
            log.info(f"    Order {order['id']}: {order['status']} @ ${order.get('filled_price', 'pending')}")
            balance -= shares * price

    # Execute sell signals
    for symbol, qty, price, rsi in sell_signals:
        log.info(f"  SELL SIGNAL: {symbol} — {qty} shares @ ~${price:.2f} (RSI={rsi:.1f})")
        order = place_order(symbol, "SELL", qty)
        if order:
            log.info(f"    Order {order['id']}: {order['status']} @ ${order.get('filled_price', 'pending')}")

    total_signals = len(buy_signals) + len(sell_signals)
    log.info(f"Strategy complete — {total_signals} signals executed")


# ─── Entry Point ──────────────────────────────────────────────────

if __name__ == "__main__":
    run_strategy()
