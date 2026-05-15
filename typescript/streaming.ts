import { VecTrade } from "@vectrade/sdk";

async function main() {
  const vt = new VecTrade();

  console.log("=== Streaming AI Analysis ===\n");
  console.log("Prompt: Analyze MSFT cloud business outlook\n");
  console.log("-".repeat(50));

  for await (const chunk of vt.ai.stream("Analyze MSFT cloud business outlook for 2025-2026")) {
    process.stdout.write(chunk.text);
  }

  console.log("\n" + "-".repeat(50));
  console.log("\nDone!");
}

main().catch(console.error);
