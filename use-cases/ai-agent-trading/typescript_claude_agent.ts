/**
 * VecTrade — AI Agent Trading via MCP Protocol (TypeScript)
 *
 * This example shows how to build a Claude-powered trading agent
 * that connects to VecTrade MCP server using the Anthropic SDK.
 *
 * Architecture:
 *   Your Code (this file)
 *     └── Anthropic Claude API (tool_use)
 *           └── VecTrade MCP Server (tool execution)
 *                 └── VecTrade Bot Trading API (X-Bot-Key)
 *
 * VecTrade does NOT host your LLM. You bring your own Claude/GPT key.
 * VecTrade MCP just exposes trading tools via standard MCP protocol.
 *
 * Setup:
 *   export ANTHROPIC_API_KEY="sk-ant-..."
 *   export VECTRADE_API_KEY="vq_your_key"
 *   # Bot key is configured on the MCP SERVER side (VECTRADE_BOT_KEY env var)
 *   npx tsx typescript_claude_agent.ts
 */

// ─── Configuration ───────────────────────────────────────────────

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || "";
const VECTRADE_API_KEY = process.env.VECTRADE_API_KEY || "";
const MCP_BASE_URL = process.env.VECTRADE_MCP_URL || "https://mcp.vectrade.io";

// Note: VECTRADE_BOT_KEY is set on the MCP SERVER (not this client).
// The hosted MCP server at mcp.vectrade.io uses the bot key linked to your
// API key account. For self-hosted, set VECTRADE_BOT_KEY in the server env.

for (const [name, val] of [
  ["ANTHROPIC_API_KEY", ANTHROPIC_API_KEY],
  ["VECTRADE_API_KEY", VECTRADE_API_KEY],
]) {
  if (!val) {
    console.error(`Error: Set ${name} environment variable`);
    process.exit(1);
  }
}

// ═════════════════════════════════════════════════════════════════
// STEP 1: MCP Client — connects to VecTrade MCP server
// ═════════════════════════════════════════════════════════════════

interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

class VecTradeMCPClient {
  private sessionId = "";
  private requestId = 0;
  tools: MCPTool[] = [];

  async connect(): Promise<void> {
    // Initialize MCP session
    const initResp = await this.callMCP("initialize", {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "ts-claude-agent", version: "1.0.0" },
    });
    this.sessionId = initResp.headers.get("mcp-session-id") || "";
    console.log(`[MCP] Connected — session: ${this.sessionId.slice(0, 20)}...`);

    // Discover tools
    const toolsResp = await this.callMCP("tools/list");
    const toolsData = await toolsResp.json();
    this.tools = toolsData.result.tools;
    console.log(`[MCP] ${this.tools.length} tools available`);
  }

  async callTool(name: string, args: Record<string, unknown>): Promise<string> {
    const resp = await this.callMCP("tools/call", { name, arguments: args });
    const data = await resp.json();
    if (data.error) throw new Error(`MCP error: ${JSON.stringify(data.error)}`);
    const content = data.result.content;
    return content[0]?.text || "";
  }

  /** Convert MCP tools to Anthropic tool format */
  getToolsForClaude(): Array<{
    name: string;
    description: string;
    input_schema: Record<string, unknown>;
  }> {
    return this.tools.map((t) => ({
      name: t.name,
      description: t.description,
      input_schema: t.inputSchema || { type: "object", properties: {} },
    }));
  }

  private async callMCP(
    method: string,
    params?: Record<string, unknown>
  ): Promise<Response> {
    this.requestId++;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "X-API-Key": VECTRADE_API_KEY,
    };
    if (this.sessionId) headers["mcp-session-id"] = this.sessionId;

    const body: Record<string, unknown> = {
      jsonrpc: "2.0",
      id: this.requestId,
      method,
    };
    if (params) body.params = params;

    return fetch(`${MCP_BASE_URL}/mcp`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
  }
}

// ═════════════════════════════════════════════════════════════════
// STEP 2: Claude Agent — LLM with tool execution loop
// ═════════════════════════════════════════════════════════════════

interface Message {
  role: "user" | "assistant";
  content: string | ContentBlock[];
}

interface ContentBlock {
  type: "text" | "tool_use" | "tool_result";
  text?: string;
  id?: string;
  name?: string;
  input?: Record<string, unknown>;
  tool_use_id?: string;
  content?: string;
}

class ClaudeTradingAgent {
  private messages: Message[] = [];
  private mcp: VecTradeMCPClient;

  private readonly systemPrompt = `You are a trading assistant with access to VecTrade tools.
You can research markets (quotes, technicals, fundamentals, news) and execute trades.

Rules:
- Always check current price before placing orders
- For STOCK/ETF, orders only execute during US market hours (9:30-16:00 ET)
- CRYPTO trades execute 24/7
- Use LIMIT orders when the user wants price control
- Never risk more than 5% of portfolio on a single trade
- Report clearly what you did`;

  constructor(mcp: VecTradeMCPClient) {
    this.mcp = mcp;
  }

  async chat(userMessage: string): Promise<string> {
    this.messages.push({ role: "user", content: userMessage });

    // Agent loop: Claude responds → maybe tool_use → execute → back to Claude
    while (true) {
      const response = await this.callClaude();
      const content: ContentBlock[] = response.content;
      this.messages.push({ role: "assistant", content });

      // Check if Claude wants to use tools
      const toolUses = content.filter((b: ContentBlock) => b.type === "tool_use");
      if (toolUses.length === 0) {
        // Final text response
        const textBlock = content.find((b: ContentBlock) => b.type === "text");
        return textBlock?.text || "(no response)";
      }

      // Execute tools and feed results back
      const toolResults: ContentBlock[] = [];
      for (const toolUse of toolUses) {
        console.log(`  [Tool] ${toolUse.name}(${JSON.stringify(toolUse.input)})`);
        let result: string;
        try {
          result = await this.mcp.callTool(toolUse.name!, toolUse.input!);
        } catch (e: unknown) {
          result = `Error: ${e instanceof Error ? e.message : String(e)}`;
        }
        toolResults.push({
          type: "tool_result",
          tool_use_id: toolUse.id,
          content: result,
        });
      }
      this.messages.push({ role: "user", content: toolResults });
    }
  }

  private async callClaude(): Promise<{ content: ContentBlock[] }> {
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 4096,
        system: this.systemPrompt,
        messages: this.messages,
        tools: this.mcp.getToolsForClaude(),
      }),
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`Anthropic API ${resp.status}: ${err}`);
    }
    return resp.json();
  }
}

// ═════════════════════════════════════════════════════════════════
// STEP 3: Run the agent
// ═════════════════════════════════════════════════════════════════

async function main() {
  const mcp = new VecTradeMCPClient();
  await mcp.connect();

  const agent = new ClaudeTradingAgent(mcp);

  console.log("\n" + "=".repeat(60));
  console.log("VecTrade Claude Trading Agent");
  console.log("=".repeat(60));
  console.log("\nExamples:");
  console.log('  "What\'s NVDA trading at? Buy 3 shares if RSI < 70"');
  console.log('  "Show my portfolio performance"');
  console.log('  "Buy $500 of BTC-USD at market price"');

  // ── Demo: run a single prompt ──
  const demoPrompt =
    process.argv[2] || "Check my portfolio balance and list my positions";

  console.log(`\nYou: ${demoPrompt}\n`);
  console.log("Agent thinking...\n");

  const response = await agent.chat(demoPrompt);
  console.log(`\nAgent: ${response}\n`);
}

main().catch(console.error);
