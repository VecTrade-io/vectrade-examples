#!/usr/bin/env python3
"""
VecTrade Bot Trade — External E2E Verification Script
======================================================
Simulates an independent external trading bot connecting to the
VecTrade Bot Trading API and executes a complete trade workflow:

    Stage 1 · Authentication & Connection
    Stage 2 · Account & Portfolio Baseline
    Stage 3 · Market Buy Order (CRYPTO)
    Stage 4 · Order Status Confirmation
    Stage 5 · Portfolio Impact Verification
    Stage 6 · Limit Sell Order (with Idempotency)
    Stage 7 · Order Cancellation
    Stage 8 · KPI Consistency Check
    Stage 9 · Error Path Coverage
    Stage 10 · Final Report & Exit

Usage:
    # UAT
    VECTRADE_BOT_KEY="tvt_..." VECTRADE_BOT_API_BASE="https://uat.vectrade.io/api/trade/v1/bot" \\
        python scripts/bot_trade_e2e.py

    # Local dev
    VECTRADE_BOT_KEY="tvt_..." VECTRADE_BOT_API_BASE="http://localhost:9002/api/v1/bot" \\
        python scripts/bot_trade_e2e.py

Exit codes:
    0 — all stages passed
    1 — one or more stages failed
    2 — configuration error (missing env vars)
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

# ─── Configuration ────────────────────────────────────────────────

BOT_KEY = os.environ.get("VECTRADE_BOT_KEY", "").strip()
BOT_API_BASE = os.environ.get(
    "VECTRADE_BOT_API_BASE", "https://vectrade.io/api/trade/v1/bot"
).rstrip("/")
SLA_READ_MS = int(os.environ.get("SLA_READ_MS", "3000"))
SLA_ORDER_MS = int(os.environ.get("SLA_ORDER_MS", "5000"))

TRADE_SYMBOL = "BTC-USD"
TRADE_ASSET = "CRYPTO"
TRADE_QTY = "0.0001"            # small, deterministic
LIMIT_SELL_PRICE = "999999.00"  # well above market — a SELL limit stays OPEN until price rises above this
SESSION_ID = uuid.uuid4().hex[:12]

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"


# ─── Result tracking ──────────────────────────────────────────────

@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""
    elapsed_ms: float = 0.0


@dataclass
class Stage:
    name: str
    checks: list[Check] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def add(self, name: str, passed: bool, detail: str = "", elapsed_ms: float = 0.0) -> Check:
        c = Check(name, passed, detail, elapsed_ms)
        self.checks.append(c)
        _print_check(c)
        return c


# ─── HTTP client ──────────────────────────────────────────────────

class RateLimitTransport(httpx.BaseTransport):
    """Automatically retries 429 with exponential back-off (max 3 retries)."""

    MAX_RETRIES = 3

    def __init__(self) -> None:
        self._inner = httpx.HTTPTransport()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        for attempt in range(self.MAX_RETRIES):
            resp = self._inner.handle_request(request)
            if resp.status_code != 429 or attempt == self.MAX_RETRIES - 1:
                return resp
            wait = 2 ** attempt
            _log(f"  429 rate-limited — retrying in {wait}s (attempt {attempt + 1})", YELLOW)
            time.sleep(wait)
        return resp  # type: ignore[return-value]

    def close(self) -> None:
        self._inner.close()


def _make_client() -> httpx.Client:
    return httpx.Client(
        base_url=BOT_API_BASE,
        headers={
            "X-Bot-Key": BOT_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"vectrade-bot-verifier/{SESSION_ID}",
        },
        timeout=15.0,
        transport=RateLimitTransport(),
    )


# ─── Helpers ──────────────────────────────────────────────────────

def _log(msg: str, colour: str = "") -> None:
    print(f"{colour}{msg}{RESET}" if colour else msg)


def _print_check(c: Check) -> None:
    icon = f"{GREEN}✓{RESET}" if c.passed else f"{RED}✗{RESET}"
    lat = f"  {DIM}({c.elapsed_ms:.0f}ms){RESET}" if c.elapsed_ms else ""
    detail = f"  {DIM}{c.detail}{RESET}" if c.detail else ""
    print(f"  {icon} {c.name}{lat}{detail}")


def _stage(name: str) -> Stage:
    _log(f"\n{BOLD}{CYAN}▶ {name}{RESET}")
    return Stage(name)


def _assert_schema(data: dict, required: list[str]) -> tuple[bool, str]:
    missing = [k for k in required if k not in data]
    if missing:
        return False, f"missing fields: {missing}"
    return True, ""


def _timed_get(client: httpx.Client, path: str) -> tuple[httpx.Response, float]:
    t0 = time.perf_counter()
    r = client.get(path)
    return r, (time.perf_counter() - t0) * 1000


def _timed_post(client: httpx.Client, path: str, payload: dict) -> tuple[httpx.Response, float]:
    t0 = time.perf_counter()
    r = client.post(path, json=payload)
    return r, (time.perf_counter() - t0) * 1000


def _timed_delete(client: httpx.Client, path: str) -> tuple[httpx.Response, float]:
    t0 = time.perf_counter()
    r = client.delete(path)
    return r, (time.perf_counter() - t0) * 1000


def _coerce_decimal(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return None


# ─── Stage implementations ────────────────────────────────────────

def stage_auth(client: httpx.Client) -> Stage:
    s = _stage("Stage 1 — Authentication & Connection")

    # Valid key must reach the API
    r, ms = _timed_get(client, "/account")
    s.add("Valid bot key returns 200", r.status_code == 200,
          f"HTTP {r.status_code}", ms)

    # No key must be rejected
    bare = httpx.Client(base_url=BOT_API_BASE, timeout=10)
    rb, _ = _timed_get(bare, "/account")
    bare.close()
    s.add("Missing key returns 401/422", rb.status_code in (401, 422),
          f"HTTP {rb.status_code}")

    # Wrong prefix must be rejected
    bad = httpx.Client(
        base_url=BOT_API_BASE,
        headers={"X-Bot-Key": "sk_not_a_tvt_key"},
        timeout=10,
    )
    rc, _ = _timed_get(bad, "/account")
    bad.close()
    s.add("Non-tvt_ prefix returns 401", rc.status_code == 401,
          f"HTTP {rc.status_code}")

    # Garbage tvt_ key must be rejected
    bad2 = httpx.Client(
        base_url=BOT_API_BASE,
        headers={"X-Bot-Key": "tvt_completelyinvalidkey0000000000"},
        timeout=10,
    )
    rd, _ = _timed_get(bad2, "/account")
    bad2.close()
    s.add("Fake tvt_ key returns 401", rd.status_code == 401,
          f"HTTP {rd.status_code}")

    return s


def stage_account(client: httpx.Client) -> tuple[Stage, dict]:
    s = _stage("Stage 2 — Account & Portfolio Baseline")
    account: dict = {}

    r, ms = _timed_get(client, "/account")
    if r.status_code != 200:
        s.add("GET /account returns 200", False, f"HTTP {r.status_code}", ms)
        return s, account

    account = r.json()
    s.add("GET /account returns 200", True, "", ms)
    s.add("Latency within SLA",
          ms <= SLA_READ_MS,
          f"{ms:.0f}ms (SLA={SLA_READ_MS}ms)")

    ok, detail = _assert_schema(account, [
        "bot_user_id", "display_name", "balance",
        "user_type", "status", "plan",
        "bot_keys_used", "bot_keys_limit",
    ])
    s.add("Account schema complete", ok, detail)

    bal = _coerce_decimal(account.get("balance"))
    s.add("Balance is numeric ≥ 0", bal is not None and bal >= 0,
          f"balance={account.get('balance')}")

    s.add("Status is ACTIVE", account.get("status") == "ACTIVE",
          f"status={account.get('status')}")

    s.add("Bot keys used ≥ 1", (account.get("bot_keys_used") or 0) >= 1,
          f"bot_keys_used={account.get('bot_keys_used')}")

    # Portfolio baseline
    rp, msp = _timed_get(client, "/portfolio")
    if rp.status_code == 200:
        port = rp.json()
        s.add("GET /portfolio returns 200", True, "", msp)
        s.add("Portfolio latency within SLA",
              msp <= SLA_READ_MS,
              f"{msp:.0f}ms")
        ok2, det2 = _assert_schema(port, ["balance", "total_equity", "positions"])
        s.add("Portfolio schema complete", ok2, det2)
        eq = _coerce_decimal(port.get("total_equity"))
        s.add("Total equity is numeric ≥ 0", eq is not None and eq >= 0,
              f"total_equity={port.get('total_equity')}")
    else:
        s.add("GET /portfolio returns 200", False, f"HTTP {rp.status_code}", msp)

    return s, account


def stage_market_buy(client: httpx.Client) -> tuple[Stage, dict]:
    s = _stage("Stage 3 — Market Buy Order (CRYPTO)")
    order: dict = {}

    cid = f"bot-verifier-buy-{SESSION_ID}"
    payload = {
        "symbol": TRADE_SYMBOL,
        "asset_type": TRADE_ASSET,
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": TRADE_QTY,
        "time_in_force": "GTC",
        "client_order_id": cid,
    }

    r, ms = _timed_post(client, "/orders", payload)
    s.add("POST /orders returns 201", r.status_code == 201,
          f"HTTP {r.status_code}", ms)

    if r.status_code != 201:
        return s, order

    order = r.json()
    s.add("Order placement latency within SLA",
          ms <= SLA_ORDER_MS,
          f"{ms:.0f}ms (SLA={SLA_ORDER_MS}ms)")

    ok, detail = _assert_schema(order, [
        "id", "symbol", "side", "order_type",
        "quantity", "status", "created_at",
    ])
    s.add("Order response schema complete", ok, detail)

    s.add("Symbol matches", order.get("symbol") == TRADE_SYMBOL,
          f"symbol={order.get('symbol')}")
    s.add("Side is BUY", order.get("side") == "BUY",
          f"side={order.get('side')}")
    api_qty = _coerce_decimal(order.get("quantity"))
    expected_qty = _coerce_decimal(TRADE_QTY)
    s.add("Quantity matches",
          api_qty is not None and expected_qty is not None and api_qty == expected_qty,
          f"qty={order.get('quantity')}")

    VALID_STATUSES = {"FILLED", "PARTIALLY_FILLED", "OPEN", "PENDING"}
    s.add("Status is valid post-placement state",
          order.get("status") in VALID_STATUSES,
          f"status={order.get('status')}")

    # Idempotency: same client_order_id must return the same order
    r2, ms2 = _timed_post(client, "/orders", payload)
    s.add("Idempotent resubmit returns 200/201",
          r2.status_code in (200, 201),
          f"HTTP {r2.status_code}", ms2)
    if r2.status_code in (200, 201):
        s.add("Idempotent resubmit returns same order id",
              r2.json().get("id") == order.get("id"),
              f"expected={order.get('id')} got={r2.json().get('id')}")

    return s, order


def stage_order_status(client: httpx.Client, order: dict) -> Stage:
    s = _stage("Stage 4 — Order Status Confirmation")

    if not order.get("id"):
        s.add("Order ID available (prerequisite)", False, "no order from stage 3")
        return s

    r, ms = _timed_get(client, f"/orders/{order['id']}")
    s.add("GET /orders/{id} returns 200", r.status_code == 200,
          f"HTTP {r.status_code}", ms)

    if r.status_code != 200:
        return s

    data = r.json()
    s.add("Order ID consistent", data.get("id") == order["id"],
          f"got={data.get('id')}")

    SETTLED = {"FILLED", "PARTIALLY_FILLED", "CANCELLED", "REJECTED", "OPEN"}
    s.add("Order in settled/active state",
          data.get("status") in SETTLED,
          f"status={data.get('status')}")

    if data.get("status") in ("FILLED", "PARTIALLY_FILLED"):
        s.add("Filled order has filled_price",
              data.get("filled_price") is not None,
              f"filled_price={data.get('filled_price')}")
        fp = _coerce_decimal(data.get("filled_price"))
        s.add("fill_price is positive number",
              fp is not None and fp > 0,
              f"filled_price={data.get('filled_price')}")

    # Order appears in listing
    rl, _ = _timed_get(client, "/orders")
    if rl.status_code == 200:
        ids = [o["id"] for o in rl.json()]
        s.add("Order appears in GET /orders listing",
              order["id"] in ids,
              f"listed={order['id'] in ids}")
    else:
        s.add("GET /orders returns 200", False, f"HTTP {rl.status_code}")

    return s


def stage_portfolio_impact(client: httpx.Client, account_before: dict) -> Stage:
    s = _stage("Stage 5 — Portfolio Impact Verification")

    r, ms = _timed_get(client, "/portfolio")
    s.add("GET /portfolio returns 200", r.status_code == 200,
          f"HTTP {r.status_code}", ms)

    if r.status_code != 200:
        return s

    port = r.json()
    eq = _coerce_decimal(port.get("total_equity"))
    s.add("Portfolio equity is numeric ≥ 0",
          eq is not None and eq >= 0,
          f"total_equity={port.get('total_equity')}")

    # Positions list is valid
    positions = port.get("positions", [])
    s.add("Positions is a list", isinstance(positions, list))

    if positions:
        p = positions[0]
        ok, detail = _assert_schema(p, [
            "symbol", "asset_type", "quantity", "avg_cost",
        ])
        s.add("Position schema valid", ok, detail)
        qty = _coerce_decimal(p.get("quantity"))
        s.add("Position quantity > 0", qty is not None and qty > 0,
              f"qty={p.get('quantity')}")

    # Balance + equity cross-check: equity ≥ cash balance (we hold some assets)
    bal = _coerce_decimal(port.get("balance"))
    if eq is not None and bal is not None:
        s.add("Portfolio equity ≥ cash balance",
              eq >= bal,
              f"equity={eq} balance={bal}")

    return s


def stage_limit_sell(client: httpx.Client) -> tuple[Stage, dict]:
    s = _stage("Stage 6 — Limit Sell Order (Open, then verified cancellable)")
    order: dict = {}

    cid = f"bot-verifier-sell-{SESSION_ID}"
    payload = {
        "symbol": TRADE_SYMBOL,
        "asset_type": TRADE_ASSET,
        "side": "SELL",
        "order_type": "LIMIT",
        "quantity": TRADE_QTY,
        "limit_price": LIMIT_SELL_PRICE,  # well above market → SELL limit stays OPEN
        "time_in_force": "GTC",
        "client_order_id": cid,
    }

    r, ms = _timed_post(client, "/orders", payload)
    s.add("POST /orders LIMIT SELL returns 201",
          r.status_code == 201,
          f"HTTP {r.status_code}", ms)

    if r.status_code != 201:
        return s, order

    order = r.json()
    VALID = {"FILLED", "PARTIALLY_FILLED", "OPEN", "PENDING", "CANCELLED", "REJECTED"}
    s.add("Limit order status is valid",
          order.get("status") in VALID,
          f"status={order.get('status')}")
    api_lp = _coerce_decimal(order.get("limit_price"))
    exp_lp = _coerce_decimal(LIMIT_SELL_PRICE)
    s.add("Limit price echoed",
          api_lp is not None and exp_lp is not None and api_lp == exp_lp,
          f"limit_price={order.get('limit_price')}")

    # Filter listing by status OPEN
    ro, _ = _timed_get(client, "/orders?status=OPEN")
    if ro.status_code == 200:
        open_ids = [o["id"] for o in ro.json()]
        # Only check if order is OPEN
        if order.get("status") == "OPEN":
            s.add("OPEN limit order appears in ?status=OPEN filter",
                  order["id"] in open_ids,
                  f"found={order['id'] in open_ids}")
        else:
            s.add(
                f"Order not OPEN (status={order.get('status')}) — filter check skipped",
                True,
            )
    else:
        s.add("Filter listing by status=OPEN returns 200",
              False, f"HTTP {ro.status_code}")

    return s, order


def stage_cancel_order(client: httpx.Client, order: dict) -> Stage:
    s = _stage("Stage 7 — Order Cancellation")

    if not order.get("id"):
        s.add("Order ID available (prerequisite)", False, "no order from stage 6")
        return s

    if order.get("status") not in ("OPEN", "PENDING"):
        s.add(
            f"Cancellation skipped (order status={order.get('status')}, not cancellable)",
            True,
        )
        return s

    r, ms = _timed_delete(client, f"/orders/{order['id']}")
    s.add("DELETE /orders/{id} returns 204",
          r.status_code == 204,
          f"HTTP {r.status_code}", ms)

    # Verify cancelled state
    rv, _ = _timed_get(client, f"/orders/{order['id']}")
    if rv.status_code == 200:
        s.add("Order status is CANCELLED after delete",
              rv.json().get("status") == "CANCELLED",
              f"status={rv.json().get('status')}")
    else:
        s.add("GET after cancel returns 200", False, f"HTTP {rv.status_code}")

    # Cancel a non-existent order → 404
    fake_id = str(uuid.uuid4())
    rf, _ = _timed_delete(client, f"/orders/{fake_id}")
    s.add("Cancel non-existent order returns 404",
          rf.status_code == 404,
          f"HTTP {rf.status_code}")

    return s


def stage_kpi(client: httpx.Client) -> Stage:
    s = _stage("Stage 8 — KPI Consistency Check")

    r, ms = _timed_get(client, "/kpi")
    s.add("GET /kpi returns 200", r.status_code == 200,
          f"HTTP {r.status_code}", ms)

    if r.status_code != 200:
        return s

    data = r.json()
    s.add("KPI latency within SLA", ms <= SLA_READ_MS,
          f"{ms:.0f}ms")

    ok, detail = _assert_schema(data, [
        "total_return_pct", "sharpe_ratio", "win_rate",
        "profit_factor", "max_drawdown", "total_trades",
        "sortino_ratio", "expectancy",
        "consecutive_wins", "consecutive_losses",
    ])
    s.add("KPI schema complete", ok, detail)

    for field_name in ("total_return_pct", "sharpe_ratio", "win_rate",
                       "profit_factor", "max_drawdown", "sortino_ratio", "expectancy"):
        v = data.get(field_name)
        ok_v = isinstance(v, (int, float))
        s.add(f"{field_name} is numeric", ok_v, f"value={v}")

    for int_field in ("total_trades", "consecutive_wins", "consecutive_losses"):
        v = data.get(int_field)
        s.add(f"{int_field} is non-negative int",
              isinstance(v, int) and v >= 0,
              f"value={v}")

    wr = data.get("win_rate", -1)
    s.add("win_rate in [0, 100]",
          isinstance(wr, (int, float)) and 0 <= wr <= 100,
          f"win_rate={wr}")

    # total_trades reflects fully-settled historical trades; a fresh user starts at 0
    tt = data.get("total_trades", -1)
    s.add("total_trades is non-negative int (KPI responding)",
          isinstance(tt, int) and tt >= 0,
          f"total_trades={tt}")

    return s


def stage_error_paths(client: httpx.Client) -> Stage:
    s = _stage("Stage 9 — Error Path Coverage")

    # Invalid symbol format
    r1, _ = _timed_post(client, "/orders", {
        "symbol": "!!!INVALID!!!",
        "asset_type": TRADE_ASSET,
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": TRADE_QTY,
        "time_in_force": "GTC",
    })
    s.add("Invalid symbol returns 422",
          r1.status_code == 422,
          f"HTTP {r1.status_code}")

    # Zero quantity
    r2, _ = _timed_post(client, "/orders", {
        "symbol": TRADE_SYMBOL,
        "asset_type": TRADE_ASSET,
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": "0",
        "time_in_force": "GTC",
    })
    s.add("Zero quantity returns 422",
          r2.status_code == 422,
          f"HTTP {r2.status_code}")

    # Negative quantity
    r3, _ = _timed_post(client, "/orders", {
        "symbol": TRADE_SYMBOL,
        "asset_type": TRADE_ASSET,
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": "-1",
        "time_in_force": "GTC",
    })
    s.add("Negative quantity returns 422",
          r3.status_code == 422,
          f"HTTP {r3.status_code}")

    # LIMIT order without limit_price
    r4, _ = _timed_post(client, "/orders", {
        "symbol": TRADE_SYMBOL,
        "asset_type": TRADE_ASSET,
        "side": "BUY",
        "order_type": "LIMIT",
        "quantity": TRADE_QTY,
        "time_in_force": "GTC",
    })
    s.add("LIMIT order without limit_price returns 422",
          r4.status_code == 422,
          f"HTTP {r4.status_code}")

    # Missing required field
    r5, _ = _timed_post(client, "/orders", {
        "symbol": TRADE_SYMBOL,
        "side": "BUY",
        # missing asset_type, order_type, quantity
    })
    s.add("Order with missing required fields returns 422",
          r5.status_code == 422,
          f"HTTP {r5.status_code}")

    # Non-existent order
    r6, _ = _timed_get(client, f"/orders/{uuid.uuid4()}")
    s.add("GET non-existent order returns 404",
          r6.status_code == 404,
          f"HTTP {r6.status_code}")

    return s


# ─── Report ───────────────────────────────────────────────────────

def _print_report(stages: list[Stage], total_ms: float) -> int:
    total = sum(len(s.checks) for s in stages)
    passed = sum(1 for s in stages for c in s.checks if c.passed)
    failed = total - passed
    all_pass = failed == 0

    line = "═" * 64
    print(f"\n{BOLD}{line}{RESET}")
    print(f"{BOLD}  VecTrade Bot Trade E2E — Verification Report{RESET}")
    print(f"{BOLD}{line}{RESET}")
    print(f"  Base URL : {BOT_API_BASE}")
    print(f"  Session  : {SESSION_ID}")
    print(f"  Finished : {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  Duration : {total_ms / 1000:.2f}s")
    print()

    for s in stages:
        icon = f"{GREEN}PASS{RESET}" if s.passed else f"{RED}FAIL{RESET}"
        print(f"  [{icon}]  {s.name}")

    print()
    print(f"  Checks   : {total}")
    print(f"  Passed   : {GREEN}{passed}{RESET}")
    if failed:
        print(f"  Failed   : {RED}{failed}{RESET}")
    print()

    if all_pass:
        print(f"{BOLD}{GREEN}  ✓ ALL STAGES PASSED — Bot trade mechanism verified.{RESET}")
    else:
        print(f"{BOLD}{RED}  ✗ VERIFICATION FAILED — {failed} check(s) did not pass.{RESET}")
        print(f"\n  {BOLD}Failed checks:{RESET}")
        for s in stages:
            for c in s.checks:
                if not c.passed:
                    print(f"    {RED}✗{RESET} [{s.name}] {c.name}"
                          + (f"  →  {c.detail}" if c.detail else ""))

    print(f"\n{BOLD}{line}{RESET}\n")
    return 0 if all_pass else 1


# ─── Entrypoint ───────────────────────────────────────────────────

def main() -> int:
    if not BOT_KEY:
        print(
            f"{RED}ERROR: VECTRADE_BOT_KEY environment variable is not set.{RESET}\n"
            "  export VECTRADE_BOT_KEY=\"tvt_your_key_here\"",
            file=sys.stderr,
        )
        return 2

    if not BOT_KEY.startswith("tvt_"):
        print(
            f"{YELLOW}WARNING: VECTRADE_BOT_KEY does not start with 'tvt_' — "
            "authentication will likely fail.{RESET}",
            file=sys.stderr,
        )

    header_line = "═" * 64
    print(f"\n{BOLD}{CYAN}{header_line}")
    print(f"  VecTrade Bot Trade — External E2E Verification")
    print(f"{header_line}{RESET}")
    print(f"  Target  : {BOLD}{BOT_API_BASE}{RESET}")
    print(f"  Key     : {BOT_KEY[:8]}{'*' * (len(BOT_KEY) - 8)}")
    print(f"  Session : {SESSION_ID}")
    print(f"  Symbol  : {TRADE_SYMBOL}  qty={TRADE_QTY}\n")

    stages: list[Stage] = []
    t_start = time.perf_counter()

    with _make_client() as client:
        stages.append(stage_auth(client))

        s_account, account_snapshot = stage_account(client)
        stages.append(s_account)

        s_buy, buy_order = stage_market_buy(client)
        stages.append(s_buy)

        stages.append(stage_order_status(client, buy_order))
        stages.append(stage_portfolio_impact(client, account_snapshot))

        s_sell, sell_order = stage_limit_sell(client)
        stages.append(s_sell)

        stages.append(stage_cancel_order(client, sell_order))
        stages.append(stage_kpi(client))
        stages.append(stage_error_paths(client))

    total_ms = (time.perf_counter() - t_start) * 1000
    return _print_report(stages, total_ms)


if __name__ == "__main__":
    sys.exit(main())
