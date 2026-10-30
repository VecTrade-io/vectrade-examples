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
  const quotes = await client.quotes.batch(watchlist);

  const sorted = [...quotes].sort((a, b) => b.changePct - a.changePct);
  console.log("Symbol   Price      Change     Volume");
  console.log("-".repeat(50));
  for (const q of sorted) {
    const sym = q.symbol.padEnd(8);
    const price = `$${q.price.toFixed(2)}`.padEnd(10);
    const arrow = q.changePct >= 0 ? "+" : "";
    const change = `${arrow}${q.changePct.toFixed(2)}%`.padEnd(10);
    const vol = q.volume?.toLocaleString() ?? "N/A";
    console.log(`${sym} ${price} ${change} ${vol}`);
  }

  // 2. Identify big movers
  const bigMovers = sorted.filter((q) => Math.abs(q.changePct) > 1.5);
  if (bigMovers.length > 0) {
    console.log(`\n=== Big Movers (>1.5%) — Technical Deep Dive ===`);
    for (const mover of bigMovers.slice(0, 3)) {
      const symbol = mover.symbol;
      const tech = await client.technicals.get(symbol);
      const rsi = Object.entries(tech.indicators).find(([name]) => name.toLowerCase() === "rsi")?.[1]?.at(-1)?.value;
      console.log(`\n  ${symbol} (${mover.changePct >= 0 ? "+" : ""}${mover.changePct.toFixed(2)}%):`);
      console.log(`    RSI: ${rsi?.toFixed(1) ?? "N/A"}`);
      console.log(`    Candles loaded: ${tech.candles.length}`);

      const analyst = await client.analyst.consensus(symbol);
      console.log(`    Analyst: ${analyst.consensus} | Mean target: $${analyst.targetMean.toFixed(2)}`);
    }
  }

  // 3. Options activity for top mover
  if (sorted.length > 0) {
    const top = sorted[0];
    const symbol = top.symbol;
    console.log(`\n=== Options Activity: ${symbol} ===`);
    const chain = await client.options.chain(symbol);
    console.log(`  Expiration: ${chain.expirations[0] ?? "N/A"}`);
    console.log(`  Calls: ${chain.chain.filter((contract) => contract.type === "call").length} contracts`);
    console.log(`  Puts: ${chain.chain.filter((contract) => contract.type === "put").length} contracts`);
  }
}

main().catch(console.error);
