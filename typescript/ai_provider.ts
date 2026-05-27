/**
 * VecTrade AI Provider — Vercel AI SDK Example.
 *
 * Shows how to give AI models access to real-time financial data
 * using the @vectrade/ai-provider package with the Vercel AI SDK.
 *
 * Prerequisites:
 *   npm install @vectrade/ai-provider ai @ai-sdk/openai
 *   export VECTRADE_API_KEY=vq_your_key_here
 *   export OPENAI_API_KEY=sk_your_openai_key
 *
 * Run:
 *   npx tsx ai_provider.ts
 */

import { createVecTrade } from "@vectrade/ai-provider";
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

async function main() {
  // Create VecTrade tool provider
  const vt = createVecTrade();

  console.log("=== Available Tools ===");
  const toolNames = Object.keys(vt.tools());
  console.log(`${toolNames.length} tools:`, toolNames.join(", "));

  // Use tools with any Vercel AI SDK model
  console.log("\n=== AI Analysis with Real-Time Data ===");
  const { text, toolResults } = await generateText({
    model: openai("gpt-4o-mini"),
    tools: vt.tools(),
    maxSteps: 5,
    prompt: "Get AAPL's current price, technical score, and analyst consensus. Summarize the outlook.",
  });

  console.log("\nAI Response:", text);
  console.log(`\n(Used ${toolResults?.length ?? 0} tool calls)`);
}

main().catch(console.error);
