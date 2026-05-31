/**
 * VecTrade Bot Trading — TypeScript Example
 *
 * Shows how to use the Bot API for building custom trading bots.
 *
 * Setup:
 *   export VECTRADE_BOT_KEY="tvt_your_key_here"
 *   npx tsx bot-trading.ts
 */

const BOT_API_BASE =
  process.env.VECTRADE_BOT_API_BASE || "https://vectrade.io/api/trade/v1/bot";
const BOT_KEY = process.env.VECTRADE_BOT_KEY || "";

if (!BOT_KEY) {
  console.error("Error: Set VECTRADE_BOT_KEY environment variable");
  process.exit(1);
}

// ─── API Client ──────────────────────────────────────────────────

async function botApi<T = unknown>(
  method: "GET" | "POST" | "DELETE",
  path: string,
  body?: unknown
): Promise<T> {
  const url = `${BOT_API_BASE}${path}`;
  const headers: Record<string, string> = {
    "X-Bot-Key": BOT_KEY,
    Accept: "application/json",
  };
  if (body) headers["Content-Type"] = "application/json";

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`Bot API ${res.status}: ${err.detail || res.statusText}`);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ─── Trading Functions ───────────────────────────────────────────

interface Order {
  id: string;
  symbol: string;
  side: string;
  order_type: string;
  quantity: number;
  status: string;
  filled_price?: number;
  filled_quantity?: number;
  created_at: string;
}

interface Portfolio {
  balance: number;
  total_equity: number;
  positions: Array<{
    symbol: string;
    quantity: number;
    avg_cost: number;
    current_price?: number;
    unrealized_pnl?: number;
  }>;
}

async function placeOrder(params: {
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  order_type?: "MARKET" | "LIMIT" | "STOP" | "STOP_LIMIT";
  limit_price?: number;
  stop_price?: number;
}): Promise<Order> {
  return botApi<Order>("POST", "/orders", {
    symbol: params.symbol.toUpperCase(),
    side: params.side,
    quantity: params.quantity,
    order_type: params.order_type || "MARKET",
    asset_type: "STOCK",
    time_in_force: "GTC",
    ...(params.limit_price && { limit_price: params.limit_price }),
    ...(params.stop_price && { stop_price: params.stop_price }),
  });
}

async function getPortfolio(): Promise<Portfolio> {
  return botApi<Portfolio>("GET", "/portfolio");
}

async function getKPI(): Promise<Record<string, unknown>> {
  return botApi("GET", "/kpi");
}

// ─── Main ────────────────────────────────────────────────────────

async function main() {
  console.log("=== VecTrade Bot Trading Example ===\n");

  // 1. Check portfolio
  const portfolio = await getPortfolio();
  console.log(`Cash: $${portfolio.balance}`);
  console.log(`Equity: $${portfolio.total_equity}`);
  console.log(`Positions: ${portfolio.positions.length}`);
  for (const p of portfolio.positions) {
    console.log(`  ${p.symbol}: ${p.quantity} @ $${p.avg_cost}`);
  }
  console.log();

  // 2. Place a market buy
  const order = await placeOrder({ symbol: "AAPL", side: "BUY", quantity: 5 });
  console.log(`Order: ${order.id}`);
  console.log(`  ${order.side} ${order.quantity} ${order.symbol} → ${order.status}`);
  if (order.filled_price) console.log(`  Filled @ $${order.filled_price}`);
  console.log();

  // 3. Check KPIs
  const kpi = await getKPI();
  console.log(`Return: ${kpi.total_return_pct}%`);
  console.log(`Sharpe: ${kpi.sharpe_ratio}`);
  console.log(`Win Rate: ${kpi.win_rate}%`);
  console.log(`Rank: #${kpi.rank || "N/A"}`);
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
