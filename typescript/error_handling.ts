/**
 * VecTrade TypeScript SDK — Error Handling & Resilience Patterns
 *
 * Demonstrates proper error handling for all error scenarios:
 * - Authentication failures (invalid/expired API key)
 * - Rate limiting (too many requests)
 * - Quota exhaustion (monthly limit reached)
 * - Payment required (feature needs paid plan)
 * - Validation errors (bad request parameters)
 * - Service outages (5xx / network errors)
 */

import {
  VecTrade,
  AuthenticationError,
  RateLimitError,
  QuotaExceededError,
  PaymentRequiredError,
  ValidationError,
  NotFoundError,
  ServerError,
  ServiceUnavailableError,
  VecTradeError,
} from "@vectrade/sdk";

// ── Production Error Handling ─────────────────────────────────────
async function productionErrorHandling() {
  const client = new VecTrade();

  try {
    const quote = await client.quotes.get("AAPL");
    console.log(`${quote.symbol}: $${quote.price}`);

    // Check quota via response metadata
    const meta = client.lastResponseMeta;
    if (meta) {
      console.log(`  Retries used: ${meta.retries}`);
    }
  } catch (error) {
    if (error instanceof AuthenticationError) {
      console.error(`❌ Auth failed: ${error.message} [${error.errorCode}]`);
      console.error("   → Check VECTRADE_API_KEY or visit https://app.vectrade.io/keys");
      process.exit(1);
    }

    if (error instanceof RateLimitError) {
      console.warn(`⏳ Rate limited: retry after ${error.retryAfter}s`);
      // In production: await sleep(error.retryAfter * 1000) and retry
      return;
    }

    if (error instanceof QuotaExceededError) {
      console.warn(`📊 Quota exceeded (policy: ${error.overagePolicy})`);
      if (error.overagePolicy === "BLOCK") {
        console.warn("   → Upgrade plan or wait for quota reset");
      }
      return;
    }

    if (error instanceof PaymentRequiredError) {
      console.warn(`💳 Payment required: ${error.message}`);
      return;
    }

    if (error instanceof NotFoundError) {
      console.warn(`🔍 Not found: ${error.message}`);
      return;
    }

    if (error instanceof ValidationError) {
      console.warn(`⚠ Validation: ${error.message}`, error.details);
      return;
    }

    if (error instanceof ServiceUnavailableError) {
      console.error(`🔧 Service down: ${error.message}`);
      console.error("   → Check https://status.vectrade.io");
      return;
    }

    if (error instanceof ServerError) {
      console.error(`💥 Server error: ${error.message} (request_id: ${error.requestId})`);
      return;
    }

    // Unknown error
    throw error;
  }
}

// ── Health Check ──────────────────────────────────────────────────
async function healthCheck() {
  const client = new VecTrade();

  try {
    const status = await client.health({ timeout: 5000 });
    console.log(`API status: ${status["status"]}`);
    if (status["status"] === "degraded") {
      console.warn("  ⚠ API running in degraded mode");
    }
  } catch {
    console.error("❌ Cannot reach API");
    process.exit(1);
  }
}

// ── Quota-Aware Batch Processing ─────────────────────────────────
async function quotaAwareBatch() {
  const client = new VecTrade();
  const tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA"];

  for (const ticker of tickers) {
    try {
      const quote = await client.quotes.get(ticker);
      console.log(`${quote.symbol}: $${quote.price}`);
    } catch (error) {
      if (error instanceof QuotaExceededError) {
        console.warn(`Quota exhausted at ${ticker} — stopping batch`);
        break;
      }
      if (error instanceof RateLimitError) {
        const wait = (error.retryAfter ?? 2) * 1000;
        console.warn(`Rate limited — waiting ${wait}ms...`);
        await new Promise((r) => setTimeout(r, wait));
      }
    }
  }
}

// ── Run ──────────────────────────────────────────────────────────
async function main() {
  console.log("=== Health Check ===");
  await healthCheck();
  console.log("\n=== Production Error Handling ===");
  await productionErrorHandling();
  console.log("\n=== Quota-Aware Batch ===");
  await quotaAwareBatch();
}

main().catch(console.error);
