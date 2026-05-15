import { getVecTradeClient } from "@/lib/vectrade";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const symbol = searchParams.get("symbol");

  if (!symbol) {
    return NextResponse.json({ error: "symbol parameter required" }, { status: 400 });
  }

  const client = getVecTradeClient();
  const quote = await client.quotes.get(symbol);

  return NextResponse.json(quote);
}
