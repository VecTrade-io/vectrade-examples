/**
 * VecTrade client instance for server-side usage.
 * This file initializes a singleton client to be used in API routes and server components.
 */

import { VecTrade } from "@vectrade/sdk";

let client: VecTrade | null = null;

export function getVecTradeClient(): VecTrade {
  if (!client) {
    client = new VecTrade({
      apiKey: process.env.VECTRADE_API_KEY,
    });
  }
  return client;
}
