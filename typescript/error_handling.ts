/**
 * VecTrade TypeScript SDK — Error Handling Example.
 *
 * Demonstrates typed error handling with proper recovery patterns:
 * - AuthenticationError: invalid or expired API key
 * - RateLimitError: too many requests (with retry-after)
 * - NotFoundError: invalid symbol
 * - Generic API errors
 *
 * Prerequisites:
 *   npm install @vectrade/sdk tsx
 *   export VECTRADE_API_KEY=vq_your_key_here
 *
 * Run:
 *   npx tsx error_handling.ts
 */

import {
  VecTrade,
  AuthenticationError,
  RateLimitError,
  NotFoundError,
  APIError,
} from "@vectrade/sdk";

async function basicErrorHandling() {
  const client = new VecTrade();

  try {
    const quote = await client.quotes.get("AAPL");
    console.log(`AAPL: $${quote.price.toFixed(2)}`);
  } catch (err) {
    if (err instanceof AuthenticationError) {
      console.error("Authentication failed — check your API key");
      process.exit(1);
    } else if (err instanceof RateLimitError) {
      console.error(`Rate limited. Retry after ${err.retryAfter}s`);
    } else if (err instanceof NotFoundError) {
      console.error("Symbol not found");
    } else if (err instanceof APIError) {
      console.error(`API error ${err.status}: ${err.message}`);
    } else {
      throw err;
    }
  }
}

async function batchWithFallback() {
  const client = new VecTrade();
  const symbols = ["AAPL", "MSFT", "INVALID_XYZ", "GOOGL"];

  console.log("\n=== Batch with Fallback ===");
  const results: Record<string, { price?: number; error?: string }> = {};

  for (const symbol of symbols) {
    try {
      const quote = await client.quotes.get(symbol);
      results[symbol] = { price: quote.price };
    } catch (err) {
      if (err instanceof NotFoundError) {
        results[symbol] = { error: "not found" };
      } else if (err instanceof APIError) {
        results[symbol] = { error: `API error: ${err.message}` };
      } else {
        results[symbol] = { error: "unknown error" };
      }
    }
  }

  for (const [symbol, data] of Object.entries(results)) {
    if (data.error) {
      console.log(`  ${symbol}: ${data.error}`);
    } else {
      console.log(`  ${symbol}: $${data.price!.toFixed(2)}`);
    }
  }
}

async function retryWithBackoff() {
  const client = new VecTrade();
  const maxRetries = 3;

  console.log("\n=== Retry with Backoff ===");
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const tech = await client.technicals.get("TSLA");
      const rsi = tech.indicators.rsi_14?.[0]?.value;
      console.log(`  TSLA RSI(14): ${rsi?.toFixed(1) ?? "unavailable"}`);
      return;
    } catch (err) {
      if (err instanceof RateLimitError) {
        const wait = err.retryAfter ?? Math.pow(2, attempt);
        console.log(`  Rate limited (attempt ${attempt + 1}/${maxRetries}), waiting ${wait}s...`);
        await new Promise((r) => setTimeout(r, wait * 1000));
      } else {
        throw err;
      }
    }
  }
  console.log("  Failed after all retries");
}

async function main() {
  console.log("=== Basic Error Handling ===");
  await basicErrorHandling();
  await batchWithFallback();
  await retryWithBackoff();
}

main().catch(console.error);
