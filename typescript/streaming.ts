/**
 * VecTrade TypeScript SDK — Market Monitor Example.
 *
 * Demonstrates batch quote monitoring and technical deep-dives.
 * Useful for building real-time dashboards or alert systems.
 *
 * Prerequisites:
 *   npm install @vectrade/sdk tsx
 *   export VECTRADE_API_KEY=vq_your_key_here
 *
 * Run:
 *   npx tsx streaming.ts
 */

import { VecTrade } from "@vectrade/sdk";

async function main() {
  const client = new VecTrade();
  const watchlist = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMD", "AMZN"];

  // 1. Market snapshot
  console.log("=== Market Snapshot ===");
  const quotes = (await client.quotes.batch(watchlist)) as any[];

  const sorted = [...quotes].sort((a, b) => (b.change_percent ?? 0) - (a.change_percent ?? 0));
  console.log("Symbol   Price      Change     Volume");
  console.log("-".repeat(50));
  for (const q of sorted) {
    const sym = (q.ticker || q.symbol || "?").padEnd(8);
    const price = `$${q.price.toFixed(2)}`.padEnd(10);
    const arrow = q.change_percent >= 0 ? "+" : "";
    const change = `${arrow}${q.change_percent.toFixed(2)}%`.padEnd(10);
    const vol = q.volume?.toLocaleString() ?? "N/A";
    console.log(`${sym} ${price} ${change} ${vol}`);
  }

  // 2. Identify big movers
  const bigMovers = sorted.filter((q) => Math.abs(q.change_percent) > 1.5);
  if (bigMovers.length > 0) {
    console.log(`\n=== Big Movers (>1.5%) — Technical Deep Dive ===`);
    for (const mover of bigMovers.slice(0, 3)) {
      const symbol = mover.ticker || mover.symbol;
      const tech = (await client.technicals.get(symbol)) as any;
      const rsi = tech.indicators?.rsi;
      console.log(`\n  ${symbol} (${mover.change_percent >= 0 ? "+" : ""}${mover.change_percent.toFixed(2)}%):`);
      console.log(`    Technical Score: ${tech.technical_score}`);
      console.log(`    RSI: ${rsi?.value?.toFixed(1)} (${rsi?.signal})`);
      console.log(`    Trend: ${tech.summary?.trend}`);

      const analyst = (await client.analyst.consensus(symbol)) as any;
      console.log(`    Analyst: ${analyst.consensus} | Signal: ${analyst.signal}`);
    }
  }

  // 3. Options activity for top mover
  if (sorted.length > 0) {
    const top = sorted[0];
    const symbol = top.ticker || top.symbol;
    console.log(`\n=== Options Activity: ${symbol} ===`);
    const chain = (await client.options.chain(symbol)) as any;
    console.log(`  Expiration: ${chain.expiration}`);
    console.log(`  Calls: ${chain.calls?.length ?? 0} contracts`);
    console.log(`  Puts: ${chain.puts?.length ?? 0} contracts`);
  }
}

main().catch(console.error);
