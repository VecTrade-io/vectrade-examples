import { VecTrade } from "@vectrade/sdk";

async function main() {
  const vt = new VecTrade();

  // Get a real-time quote
  const quote = await vt.quotes.get("AAPL");
  console.log(`${quote.symbol}: $${quote.price} (${quote.changePct > 0 ? "+" : ""}${quote.changePct}%)`);

  // Batch quotes
  const quotes = await vt.quotes.batch(["AAPL", "GOOGL", "MSFT"]);
  for (const q of quotes) {
    console.log(`  ${q.symbol}: $${q.price}`);
  }

  // Stream AI analysis
  console.log("\n--- AI Analysis ---");
  for await (const chunk of vt.ai.stream("Analyze AAPL for long-term hold")) {
    process.stdout.write(chunk.text);
  }
  console.log();
}

main().catch(console.error);
