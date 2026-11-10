import { NextResponse } from "next/server";

type ChatMessage = { role: "system" | "user" | "assistant"; content: string };
type ToolDefinition = Record<string, unknown>;

const allowedOrigins = new Set([
  "https://trustmebro-prompt.vercel.app/",
  "https://k5-l3-a-day-03-trustmebro-prompt-en.vercel.app/",
  "http://localhost:3000",
]);

function withCors(response: NextResponse, origin: string | null) {
  if (origin && allowedOrigins.has(origin)) {
    response.headers.set("Access-Control-Allow-Origin", origin);
    response.headers.set("Access-Control-Allow-Methods", "POST, OPTIONS");
    response.headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
    response.headers.set("Vary", "Origin");
  }
  return response;
}

export function OPTIONS(request: Request) {
  return withCors(new NextResponse(null, { status: 204 }), request.headers.get("origin"));
}

export async function POST(request: Request) {
  const origin = request.headers.get("origin");

  console.log("========== API DEBUG ==========");
  console.log("Incoming Origin:", origin);
  console.log("Origin Allowed:", allowedOrigins.has(origin ?? ""));
  console.log("OpenRouter Key Exists:", !!process.env.OPENROUTER_API_KEY);
  console.log("================================");

  if (origin && !allowedOrigins.has(origin)) {
    return NextResponse.json({ error: "Origin is not allowed." }, { status: 403 });
  }

  const json = (body: unknown, init?: ResponseInit) =>
    withCors(NextResponse.json(body, init), origin);

  let body: {
    provider?: string;
    version?: string;
    model?: string;
    messages?: ChatMessage[];
    tools?: ToolDefinition[];
    temperature?: number;
    tool_choice?: unknown;
  };

  try {
    body = await request.json();
  } catch {
    return json({ error: "Request body must be valid JSON." }, { status: 400 });
  }

  if (body.provider !== "openrouter") {
    return json({ error: "This endpoint supports provider 'openrouter' only." }, { status: 400 });
  }
  if (typeof body.version !== "string" || !body.version.trim()) {
    return json({ error: "A non-empty version is required." }, { status: 400 });
  }
  if (!Array.isArray(body.messages) || body.messages.length === 0) {
    return json({ error: "At least one message is required." }, { status: 400 });
  }
  if (!body.messages.every((message) =>
    message && ["system", "user", "assistant"].includes(message.role) && typeof message.content === "string"
  )) {
    return json({ error: "Messages must have a supported role and string content." }, { status: 400 });
  }

  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    return json({ error: "The server is missing OPENROUTER_API_KEY." }, { status: 500 });
  }

  try {
    const upstream = await fetch(`${process.env.OPENROUTER_BASE_URL ?? "https://openrouter.ai/api/v1"}/chat/completions`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: body.model || process.env.OPENROUTER_MODEL || "openai/gpt-4o-mini",
        messages: body.messages,
        ...(body.tools?.length ? { tools: body.tools } : {}),
        ...(body.tool_choice !== undefined ? { tool_choice: body.tool_choice } : {}),
        temperature: typeof body.temperature === "number" ? body.temperature : 0,
      }),
      signal: AbortSignal.timeout(60_000),
    });

    const payload = await upstream.json().catch(() => ({}));
    if (!upstream.ok) {
      const message = payload?.error?.message ?? `OpenRouter returned HTTP ${upstream.status}.`;
      return json({ error: message }, { status: upstream.status >= 500 ? 502 : upstream.status });
    }

    const choice = payload?.choices?.[0];
    if (!choice?.message) {
      return json({ error: "OpenRouter returned an empty response." }, { status: 502 });
    }

    return json({
      version: body.version,
      model: payload.model ?? body.model ?? process.env.OPENROUTER_MODEL ?? "openai/gpt-4o-mini",
      text: typeof choice.message.content === "string" ? choice.message.content : null,
      tool_calls: (choice.message.tool_calls ?? []).map((call: { function?: { name?: string; arguments?: string } }) => {
        let args: Record<string, unknown> = {};
        try {
          const parsed: unknown = JSON.parse(call.function?.arguments || "{}");
          if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) args = parsed as Record<string, unknown>;
          else args = { _invalid_json_arguments: call.function?.arguments || "{}" };
        } catch {
          args = { _invalid_json_arguments: call.function?.arguments || "{}" };
        }
        return { name: call.function?.name ?? "", args };
      }),
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown upstream error.";
    return json({ error: `OpenRouter request failed: ${message}` }, { status: 502 });
  }
}
