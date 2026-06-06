#!/usr/bin/env python3
"""Unified OpenRouter Proxy — speed-optimized, privacy-first."""
import os, json, httpx, asyncio, re
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

# --- Backend Selection ---
# "local" (default) = use your own models. "openrouter" = use OpenRouter.
LLM_BACKEND = os.getenv("LLM_BACKEND", "local")
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://localhost:11434/v1")

if LLM_BACKEND == "openrouter":
    TARGET_URL = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_KEY:
        raise RuntimeError("CRITICAL: OPENROUTER_API_KEY missing from .env. Set it or switch to LLM_BACKEND=local")
else:
    TARGET_URL = f"{LOCAL_API_URL}/chat/completions"
    OPENROUTER_KEY = None

# --- Model IDs — configure in .env, or keep the defaults ---
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek/deepseek-v4-pro")
PLANNING_MODEL = os.getenv("PLANNING_MODEL", "deepseek/deepseek-v4-pro")
BULK_MODEL = os.getenv("BULK_MODEL", "google/gemini-2.5-flash")
RING_MODEL = os.getenv("RING_MODEL", "inclusionai/ring-2.6-1t")
VISION_MODEL = os.getenv("VISION_MODEL", "perceptron/perceptron-mk1")
V4_MODEL = os.getenv("V4_MODEL", "deepseek/deepseek-v4-flash")

KEYWORD_MAP = {
    "#pro": PLANNING_MODEL,
    "#v4": V4_MODEL,
    "#flash": BULK_MODEL,
    "#ring": RING_MODEL,
    "#vision": VISION_MODEL,
    "#kimi": os.getenv("KIMI_MODEL", "moonshotai/kimi-k2.5"),
    "#dc": os.getenv("DEEPSEEK_CHAT_MODEL", "deepseek/deepseek-chat"),
}

REASONING_EFFORT = {"inclusionai/ring-2.6-1t": "high"}
VISION_PARAMS = {"annotation_format": "box"}
MODE_PREFIXES = {"ask": DEFAULT_MODEL, "plan": PLANNING_MODEL, "agent": DEFAULT_MODEL}

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

def detect_routing(payload):
    msgs = payload.get("messages", [])
    if not msgs:
        return DEFAULT_MODEL, payload

    last = msgs[-1]
    content = last.get("content", "")
    text_to_scan = ""

    # Extract text safely without mutating the message dictionary
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                task_match = re.search(r"<task>\s*(.*?)\s*</task>", text, re.DOTALL)
                text_to_scan = task_match.group(1).strip() if task_match else text
                break
    elif isinstance(content, str):
        text_to_scan = content

    # Check for prefix modifications
    if text_to_scan:
        for prefix, model in MODE_PREFIXES.items():
            if text_to_scan.startswith(prefix + ":"):
                return model, payload
        for tag, model in KEYWORD_MAP.items():
            if text_to_scan.startswith(tag):
                return model, payload

    # Image detection — only check the last message
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "image_url":
                return VISION_MODEL, payload

    return DEFAULT_MODEL, payload

async def call_openrouter(data: dict, request: Request):
    headers = {
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("OR_PROXY_REFERER", "https://github.com/your-username/ultra-lite-proxy"),
        "X-Title": os.getenv("OR_PROXY_TITLE", "Ultra-Lite Proxy"),
    }
    if LLM_BACKEND == "openrouter":
        headers["Authorization"] = f"Bearer {OPENROUTER_KEY}"
        headers["OpenRouter-Enable-Prompt-Caching"] = "true"

    model = data.get("model", "")

    if model in REASONING_EFFORT:
        data["reasoning_effort"] = REASONING_EFFORT[model]
    if model == VISION_MODEL and "annotation_format" not in data:
        data.update(VISION_PARAMS)

    if LLM_BACKEND == "openrouter" and "provider" not in data:
        data["provider"] = {"sort": "latency", "ignore": ["openai"]}

    client = get_client()
    last_exception = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            async with client.stream(
                "POST", TARGET_URL,
                json=data, headers=headers
            ) as resp:
                if resp.status_code in (429, 502) and attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAYS[attempt])
                    continue
                if resp.status_code != 200:
                    error_text = await resp.aread()
                    error_data = {"error": f"Backend error {resp.status_code}: {error_text.decode()}"}
                    yield json.dumps(error_data).encode()
                    return

                async for chunk in resp.aiter_bytes():
                    if await request.is_disconnected():
                        break
                    if chunk:
                        yield chunk
                return
        except Exception as e:
            last_exception = e
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAYS[attempt])
                continue
    error_data = {"error": f"Proxy error after {MAX_RETRIES} retries: {str(last_exception)}"}
    yield json.dumps(error_data).encode()

@app.post("/v1/chat/completions")
async def chat(request: Request):
    data = await request.json()
    model, data = detect_routing(data)
    data["model"] = model
    print(f"→ Routed to: {model}  ({LLM_BACKEND})")
    stream_gen = call_openrouter(data, request)
    return StreamingResponse(stream_gen, media_type="text/event-stream")

@app.get("/v1/models")
async def models():
    return {
        "object": "list",
        "data": [{"id": m, "object": "model", "owned_by": "openrouter"} for m in KEYWORD_MAP.values()]
    }

if __name__ == "__main__":
    import uvicorn
    print(f"→ Backend: {LLM_BACKEND.upper()}  |  Target: {TARGET_URL}")
    uvicorn.run(app, host="127.0.0.1", port=8000)