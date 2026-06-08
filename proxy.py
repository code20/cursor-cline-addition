#!/usr/bin/env python3
"""Unified LLM Gateway — Cursor Cline Addition v2.4 (June 2026) by @code20"""
import os, json, httpx, asyncio, re
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════
# Backend Selection
# ═══════════════════════════════════════════

LLM_BACKEND = os.getenv("LLM_BACKEND", "local")
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://localhost:11434/v1")
DIRECT_API_URL = os.getenv("DIRECT_API_URL", "")
DIRECT_API_KEY = os.getenv("DIRECT_API_KEY", "")
DIRECT_API_PROVIDER = os.getenv("DIRECT_API_PROVIDER", "")

if LLM_BACKEND == "openrouter":
    TARGET_URL = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
    if not OPENROUTER_KEY:
        raise RuntimeError("OPENROUTER_API_KEY missing from .env")
elif LLM_BACKEND == "direct":
    TARGET_URL = f"{DIRECT_API_URL}/chat/completions"
    if not DIRECT_API_KEY:
        raise RuntimeError("DIRECT_API_KEY missing from .env")
    if not DIRECT_API_URL:
        raise RuntimeError("DIRECT_API_URL missing from .env")
else:
    TARGET_URL = f"{LOCAL_API_URL}/chat/completions"
    OPENROUTER_KEY = None

# ═══════════════════════════════════════════
# Model Configuration — all from .env
# ═══════════════════════════════════════════

MODELS = {
    "default": os.getenv("DEFAULT_MODEL", ""),
    "planner": os.getenv("PLANNING_MODEL", ""),
    "bulk": os.getenv("BULK_MODEL", ""),
    "ring": os.getenv("RING_MODEL", ""),
    "vision": os.getenv("VISION_MODEL", ""),
    "kimi": os.getenv("KIMI_MODEL", ""),
    "v4": os.getenv("V4_MODEL", ""),
    "dc": os.getenv("DEEPSEEK_CHAT_MODEL", ""),
}

missing = [name.upper() + "_MODEL" for name, val in MODELS.items() if not val]
if missing:
    raise RuntimeError(
        f"Missing required model(s) in .env: {', '.join(missing)}. "
        "Check your .env file — every model must be declared in the DEFAULTS section."
    )

DEFAULT_MODEL = MODELS["default"]
PLANNING_MODEL = MODELS["planner"]
VISION_MODEL = MODELS["vision"]

# Model-specific parameters
REASONING_EFFORT = {MODELS["ring"]: "high"}
VISION_PARAMS = {"annotation_format": "box"}

# Mode prefixes — which model handles each Cline mode
MODE_PREFIXES = {
    "ask": DEFAULT_MODEL,
    "plan": PLANNING_MODEL,
    "agent": DEFAULT_MODEL,
}

# ═══════════════════════════════════════════
# Context Window Limits (for warnings)
# ═══════════════════════════════════════════

CONTEXT_WINDOWS = {
    "deepseek/deepseek-v4-pro": 1_048_576,
    "deepseek/deepseek-chat": 1_048_576,
    "deepseek/deepseek-v4-flash": 1_048_576,
    "google/gemini-2.5-flash": 1_048_576,
    "moonshotai/kimi-k2.5": 262_144,
    "inclusionai/ring-2.6-1t": 262_144,
    "perceptron/perceptron-mk1": 33_000,
}

def get_context_limit(model_id):
    return CONTEXT_WINDOWS.get(model_id, 131_072)

# ═══════════════════════════════════════════
# HTTP Client
# ═══════════════════════════════════════════

MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]
_http_client = None

def get_client():
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=120,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
    return _http_client

app = FastAPI()

# ═══════════════════════════════════════════
# Routing Logic — simple mode-based routing
# ═══════════════════════════════════════════

def detect_routing(payload):
    """Route based on mode prefixes (plan:, ask:, agent:) — no hashtags."""
    msgs = payload.get("messages", [])
    if not msgs:
        return DEFAULT_MODEL, payload

    last = msgs[-1]
    content = last.get("content", "")
    text_to_scan = ""

    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                task_match = re.search(r"<task>\s*(.*?)\s*</task>", text, re.DOTALL)
                if task_match:
                    text_to_scan = task_match.group(1).strip()
                    break
                feedback_match = re.search(r"<feedback>\s*(.*?)\s*</feedback>", text, re.DOTALL)
                if feedback_match:
                    text_to_scan = feedback_match.group(1).strip()
                    break
                text_to_scan = text
                break
    elif isinstance(content, str):
        text_to_scan = content

    # Mode prefix routing (plan:, ask:, agent:)
    if text_to_scan:
        for prefix, model in MODE_PREFIXES.items():
            if text_to_scan.startswith(prefix + ":"):
                return model, payload

    # Image detection
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "image_url":
                return VISION_MODEL, payload

    return DEFAULT_MODEL, payload

# ═══════════════════════════════════════════
# API Call Handler
# ═══════════════════════════════════════════

async def call_backend(data: dict, request: Request):
    headers = {
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("OR_PROXY_REFERER", "https://github.com/code20/cursor-cline-addition"),
        "X-Title": os.getenv("OR_PROXY_TITLE", "Cursor Cline Addition"),
    }

    if LLM_BACKEND == "openrouter":
        headers["Authorization"] = f"Bearer {OPENROUTER_KEY}"
        headers["OpenRouter-Enable-Prompt-Caching"] = "true"
    elif LLM_BACKEND == "direct":
        if DIRECT_API_PROVIDER == "anthropic":
            headers["x-api-key"] = DIRECT_API_KEY
        else:
            headers["Authorization"] = f"Bearer {DIRECT_API_KEY}"

    model = data.get("model", "")

    if model in REASONING_EFFORT:
        data["reasoning_effort"] = REASONING_EFFORT[model]
    if model == VISION_MODEL and "annotation_format" not in data:
        data.update(VISION_PARAMS)

    if LLM_BACKEND == "openrouter" and "provider" not in data:
        data["provider"] = {"sort": "latency", "ignore": ["openai"]}

    context_limit = get_context_limit(model)
    estimated_tokens = len(json.dumps(data.get("messages", []))) // 4
    if estimated_tokens > context_limit * 0.9:
        print(f"⚠️  Context warning: ~{estimated_tokens}/{context_limit} tokens (90%+) — consider /smol")

    client = get_client()
    last_exception = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            async with client.stream("POST", TARGET_URL, json=data, headers=headers) as resp:
                if resp.status_code in (429, 502) and attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAYS[attempt])
                    continue
                if resp.status_code != 200:
                    error_text = await resp.aread()
                    error_data = {"error": f"Backend error {resp.status_code}: {error_text.decode()}"}
                    yield json.dumps(error_data).encode()
                    return
                sent_any = False
                async for chunk in resp.aiter_bytes():
                    if await request.is_disconnected():
                        break
                    if chunk:
                        sent_any = True
                        yield chunk
                if not sent_any:
                    err = {"error": "Model returned an empty response."}
                    yield json.dumps(err).encode()
                return
        except Exception as e:
            last_exception = e
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAYS[attempt])
                continue
    error_data = {"error": f"Proxy error after {MAX_RETRIES} retries: {str(last_exception)}"}
    yield json.dumps(error_data).encode()

# ═══════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════

@app.post("/v1/chat/completions")
async def chat(request: Request):
    data = await request.json()
    model, data = detect_routing(data)
    data["model"] = model
    print(f"→ Routed to: {model}  ({LLM_BACKEND})")
    stream_gen = call_backend(data, request)
    return StreamingResponse(stream_gen, media_type="text/event-stream")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "backend": LLM_BACKEND,
        "target": TARGET_URL,
        "default_model": DEFAULT_MODEL,
        "models_configured": len(MODELS),
    }

@app.get("/v1/help")
async def help_info():
    return {
        "backend": LLM_BACKEND.upper(),
        "backend_url": TARGET_URL,
        "default_model": DEFAULT_MODEL,
        "planner_model": PLANNING_MODEL,
        "context_window": get_context_limit(DEFAULT_MODEL),
        "models_configured": list(MODELS.keys()),
        "tips": [
            "Set DEFAULT_MODEL in .env to choose your workhorse model",
            "Use plan: prefix for architecture and planning tasks",
            "Change DEFAULT_MODEL and restart proxy to switch models — 10 seconds",
            "/smol every 10-15 messages saves 50-70% tokens",
            "Stay in one task — prompt caching saves 90% on system overhead",
            "Check openrouter.ai/activity for credit usage",
        ],
    }

# ═══════════════════════════════════════════
# Startup
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    print(f"→ Backend: {LLM_BACKEND.upper()}  |  Target: {TARGET_URL}")
    print(f"→ Default model: {DEFAULT_MODEL} ({get_context_limit(DEFAULT_MODEL)//1000}K context)")
    print(f"→ Planner model: {PLANNING_MODEL}")
    print(f"→ Vision model: {VISION_MODEL}")

    if LLM_BACKEND == "direct":
        print("⚠️  DIRECT MODE — No spending cap. You are billed directly by the provider.")

    print(f"→ Health check: http://127.0.0.1:8000/health")
    print(f"→ Help: http://127.0.0.1:8000/v1/help")

    uvicorn.run(app, host="127.0.0.1", port=8000)