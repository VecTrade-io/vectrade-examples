// Vercel AI SDK Chatbot with VecTrade Financial Tools
// Next.js App Router API route

import { streamText } from "ai";
import { openai } from "@ai-sdk/openai";
import { createVecTrade } from "@vectrade/ai-provider";

const vectrade = createVecTrade();

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai("gpt-4o"),
    system: `You are a financial assistant powered by VecTrade.
You have access to real-time market data, technical analysis, and AI-powered stock research.
Always use the available tools to provide data-driven answers.
Format numbers nicely and include relevant context.`,
    messages,
    tools: { ...vectrade.tools() },
  });

  return result.toDataStreamResponse();
}
