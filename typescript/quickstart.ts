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
  const quote = (await client.quotes.get("AAPL")) as any;
  console.log(`  ${quote.ticker}: $${quote.price.toFixed(2)} (${quote.change_percent >= 0 ? "+" : ""}${quote.change_percent.toFixed(2)}%)`);
  console.log(`  Volume: ${quote.volume?.toLocaleString()}`);

  // ─── 2. Batch Quotes ─────────────────────────────────────────
  console.log("\n=== Batch Quotes ===");
  const quotes = (await client.quotes.batch(["MSFT", "GOOGL", "NVDA", "META", "AMZN"])) as any[];
  for (const q of quotes) {
    console.log(`  ${q.ticker}: $${q.price.toFixed(2)} (${q.change_percent >= 0 ? "+" : ""}${q.change_percent.toFixed(2)}%)`);
  }

  // ─── 3. Company Profile ──────────────────────────────────────
  console.log("\n=== Company Profile ===");
  const profile = await client.profile.get("AAPL");
  console.log(`  ${profile.company?.name}`);
  console.log(`  Sector: ${profile.company?.sector} | Industry: ${profile.company?.industry}`);
  console.log(`  Location: ${profile.location?.city}, ${profile.location?.state}`);

  // ─── 4. Fundamentals ─────────────────────────────────────────
  console.log("\n=== Fundamentals ===");
  const fund = (await client.fundamentals.get("AAPL")) as any;
  console.log(`  Market Cap: $${(fund.market_cap / 1e12).toFixed(2)}T`);
  console.log(`  SMA50: $${fund.sma50?.toFixed(2)} | SMA200: $${fund.sma200?.toFixed(2)}`);

  // ─── 5. Financial Statements ──────────────────────────────────
  console.log("\n=== Financial Statements ===");
  const stmts = (await client.fundamentals.statements("AAPL")) as any;
  console.log(`  Available: ${Object.keys(stmts).filter(k => k !== "ticker").join(", ")}`);

  // ─── 6. Technical Analysis ────────────────────────────────────
  console.log("\n=== Technical Analysis ===");
  const tech = (await client.technicals.get("AAPL")) as any;
  console.log(`  Technical Score: ${tech.technical_score}/100`);
  console.log(`  RSI: ${tech.indicators?.rsi?.value?.toFixed(1)} (${tech.indicators?.rsi?.signal})`);
  console.log(`  Trend: ${tech.summary?.trend}`);

  // ─── 7. News ─────────────────────────────────────────────────
  console.log("\n=== Latest News ===");
  const articles = await client.news.list("AAPL");
  for (const a of (articles as any[]).slice(0, 3)) {
    console.log(`  • ${(a.headline || a.title)?.slice(0, 70)}`);
  }

  // ─── 8. Sentiment Analysis ────────────────────────────────────
  console.log("\n=== Sentiment ===");
  const sentiment = await client.sentiment.get("AAPL");
  console.log(`  Score: ${sentiment.sentiment_score} | Signal: ${sentiment.signal}`);
  console.log(`  Trend: ${sentiment.sentiment_trend}`);
  console.log(`  Social Mentions (24h): ${sentiment.social_sentiment?.mentions_24h}`);

  // ─── 9. Analyst Consensus ────────────────────────────────────
  console.log("\n=== Analyst Consensus ===");
  const analyst = (await client.analyst.consensus("AAPL")) as any;
  console.log(`  Rating: ${analyst.consensus} (Signal: ${analyst.signal})`);

  // ─── 10. Price Targets ────────────────────────────────────────
  console.log("\n=== Price Targets ===");
  const targets = (await client.analyst.priceTargets("AAPL")) as any;
  console.log(`  High: $${targets.high} | Mean: $${targets.mean?.toFixed(0)} | Low: $${targets.low}`);

  // ─── 11. Upgrades/Downgrades ──────────────────────────────────
  console.log("\n=== Recent Upgrades/Downgrades ===");
  const ratings = (await client.analyst.ratings("AAPL")) as any[];
  for (const r of ratings.slice(0, 3)) {
    console.log(`  ${r.date?.slice(0, 10)}: ${r.firm} → ${r.to_grade} (${r.action})`);
  }

  // ─── 12. Earnings ────────────────────────────────────────────
  console.log("\n=== Earnings History ===");
  const earnings = (await client.earnings.history("AAPL")) as any[];
  for (const e of earnings.slice(0, 4)) {
    const surprise = e.eps_surprise_pct != null ? ` (surprise: ${e.eps_surprise_pct > 0 ? "+" : ""}${e.eps_surprise_pct.toFixed(1)}%)` : "";
    console.log(`  ${e.date}: EPS $${e.eps_actual?.toFixed(2)} vs est $${e.eps_estimate?.toFixed(2)}${surprise}`);
  }

  // ─── 13. Insider Transactions ─────────────────────────────────
  console.log("\n=== Insider Activity ===");
  const trades = (await client.insider.transactions("AAPL")) as any[];
  for (const t of trades.slice(0, 3)) {
    console.log(`  ${t.transaction_date?.slice(0, 10)}: ${t.insider} — ${t.transaction_type} ${t.shares?.toLocaleString()} shares ($${t.value?.toLocaleString()})`);
  }

  // ─── 14. Options Chain ────────────────────────────────────────
  console.log("\n=== Options Chain ===");
  const chain = (await client.options.chain("AAPL")) as any;
  console.log(`  Expiration: ${chain.expiration}`);
  console.log(`  Calls: ${chain.calls?.length} | Puts: ${chain.puts?.length}`);

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
