/**
 * VecTrade TypeScript SDK — Complete Quickstart.
 *
 * Demonstrates ALL 12 resource groups available in the SDK.
 * Shows real-time quotes, fundamentals, technical analysis, news,
 * analyst ratings, earnings, insider activity, options, sentiment,
 * company profile, historical data, and ETF information.
 *
 * Prerequisites:
 *   npm install @vectrade/sdk tsx
 *   export VECTRADE_API_KEY=vq_your_key_here
 *
 * Run:
 *   npx tsx quickstart.ts
 */

import { VecTrade } from "@vectrade/sdk";

async function main() {
  const client = new VecTrade();

  // ─── 1. Real-Time Quote ───────────────────────────────────────
  console.log("=== Real-Time Quote ===");
  const quote = await client.quotes.get("AAPL");
  console.log(`  ${quote.symbol}: $${quote.price.toFixed(2)} (${quote.changePct >= 0 ? "+" : ""}${quote.changePct.toFixed(2)}%)`);
  console.log(`  Volume: ${quote.volume?.toLocaleString()}`);

  // ─── 2. Batch Quotes ─────────────────────────────────────────
  console.log("\n=== Batch Quotes ===");
  const quotes = await client.quotes.batch(["MSFT", "GOOGL", "NVDA", "META", "AMZN"]);
  for (const q of quotes) {
    console.log(`  ${q.symbol}: $${q.price.toFixed(2)} (${q.changePct >= 0 ? "+" : ""}${q.changePct.toFixed(2)}%)`);
  }

  // ─── 3. Company Profile ──────────────────────────────────────
  console.log("\n=== Company Profile ===");
  const profile = await client.profile.get("AAPL");
  console.log(`  ${profile.company?.name}`);
  console.log(`  Sector: ${profile.company?.sector} | Industry: ${profile.company?.industry}`);
  console.log(`  Location: ${profile.location?.city}, ${profile.location?.state}`);

  // ─── 4. Fundamentals ─────────────────────────────────────────
  console.log("\n=== Fundamentals ===");
  const fund = await client.fundamentals.get("AAPL");
  console.log(`  Market Cap: $${((fund.marketCap ?? 0) / 1e12).toFixed(2)}T`);
  console.log(`  P/E: ${fund.peRatio?.toFixed(2) ?? "N/A"} | Beta: ${fund.beta?.toFixed(2) ?? "N/A"}`);

  // ─── 5. Financial Statements ──────────────────────────────────
  console.log("\n=== Financial Statements ===");
  const stmts = await client.fundamentals.statements("AAPL");
  console.log(`  Available: ${Object.keys(stmts).filter((key) => key !== "ticker").join(", ")}`);

  // ─── 6. Technical Analysis ────────────────────────────────────
  console.log("\n=== Technical Analysis ===");
  const tech = await client.technicals.get("AAPL");
  const rsi = Object.entries(tech.indicators).find(([name]) => name.toLowerCase() === "rsi")?.[1]?.at(-1)?.value;
  console.log(`  Indicators: ${Object.keys(tech.indicators).join(", ")}`);
  console.log(`  RSI: ${rsi?.toFixed(1) ?? "N/A"}`);
  console.log(`  Candles loaded: ${tech.candles.length}`);

  // ─── 7. News ─────────────────────────────────────────────────
  console.log("\n=== Latest News ===");
  const articles = await client.news.list("AAPL");
  for (const article of articles.slice(0, 3)) {
    console.log(`  • ${article.title.slice(0, 70)}`);
  }

  // ─── 8. Sentiment Analysis ────────────────────────────────────
  console.log("\n=== Sentiment ===");
  const sentiment = await client.sentiment.get("AAPL");
  console.log(`  Score: ${sentiment.sentiment_score} | Signal: ${sentiment.signal}`);
  console.log(`  Trend: ${sentiment.sentiment_trend}`);
  console.log(`  Social Mentions (24h): ${sentiment.social_sentiment?.mentions_24h}`);

  // ─── 9. Analyst Consensus ────────────────────────────────────
  console.log("\n=== Analyst Consensus ===");
  const analyst = await client.analyst.consensus("AAPL");
  console.log(`  Rating: ${analyst.consensus} | Analysts: ${analyst.totalAnalysts}`);
  console.log(`  Mean target: $${analyst.targetMean.toFixed(2)}`);

  // ─── 10. Price Targets ────────────────────────────────────────
  console.log("\n=== Price Targets ===");
  const targets = await client.analyst.priceTargets("AAPL");
  for (const target of targets.slice(0, 3)) {
    console.log(`  ${target.firm}: ${target.rating} at $${target.target.toFixed(2)}`);
  }

  // ─── 11. Upgrades/Downgrades ──────────────────────────────────
  console.log("\n=== Recent Upgrades/Downgrades ===");
  const ratings = await client.analyst.ratings("AAPL");
  for (const r of ratings.slice(0, 3)) {
    console.log(`  ${r.publishedAt.slice(0, 10)}: ${r.firm} → ${r.toRating} (${r.action})`);
  }

  // ─── 12. Earnings ────────────────────────────────────────────
  console.log("\n=== Earnings History ===");
  const earnings = await client.earnings.history("AAPL");
  for (const e of earnings.slice(0, 4)) {
    const surprise = e.epsSurprisePct != null ? ` (surprise: ${e.epsSurprisePct > 0 ? "+" : ""}${e.epsSurprisePct.toFixed(1)}%)` : "";
    console.log(`  ${e.date}: EPS $${e.epsActual?.toFixed(2)} vs est $${e.epsEstimate?.toFixed(2)}${surprise}`);
  }

  // ─── 13. Insider Transactions ─────────────────────────────────
  console.log("\n=== Insider Activity ===");
  const trades = await client.insider.transactions("AAPL");
  for (const t of trades.slice(0, 3)) {
    console.log(`  ${t.filedAt.slice(0, 10)}: ${t.insiderName} — ${t.transactionType} ${t.shares.toLocaleString()} shares ($${t.totalValue.toLocaleString()})`);
  }

  // ─── 14. Options Chain ────────────────────────────────────────
  console.log("\n=== Options Chain ===");
  const chain = await client.options.chain("AAPL");
  console.log(`  Expiration: ${chain.expirations[0] ?? "N/A"}`);
  console.log(`  Calls: ${chain.chain.filter((contract) => contract.type === "call").length} | Puts: ${chain.chain.filter((contract) => contract.type === "put").length}`);

  // ─── 15. Historical Prices ────────────────────────────────────
  console.log("\n=== Historical Prices (5 day) ===");
  const hist = await client.historical.get("AAPL", { period: "5d" });
  console.log(`  ${hist.history.length} bars loaded`);
  if (hist.history.length > 0) {
    const last = hist.history[hist.history.length - 1];
    console.log(`  Latest: ${last.timestamp.slice(0, 16)} Close=$${last.close.toFixed(2)}`);
  }

  // ─── 16. ETF Data ────────────────────────────────────────────
  console.log("\n=== ETF Data ===");
  const etf = await client.etf.get("SPY");
  console.log(`  ${etf.name}`);
  console.log(`  NAV: $${etf.nav_price?.toFixed(2)} | YTD: ${etf.ytd_return?.toFixed(2)}%`);
  console.log(`  Total Assets: $${((etf.total_assets ?? 0) / 1e9).toFixed(1)}B`);
}

main().catch(console.error);
