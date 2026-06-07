# Cursor Cline Addition — A £4–8/month AI Coding Assistant

By [@code20](https://github.com/code20)

[![Platform](https://img.shields.io/badge/platform-Windows%2011-0078D6)](https://www.microsoft.com/windows)
[![Cost](https://img.shields.io/badge/cost-£4–8%2Fmonth-10b981)](https://openrouter.ai)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A complete guide to building your own multi-model AI coding assistant that runs inside Cursor (free) and Cline, powered by OpenRouter. **96% cheaper than Cursor Ultra**, with full privacy and zero vendor lock-in.

---

## 🚀 TL;DR

I built a multi-model AI coding assistant that costs **£4–8/month** for typical use. It uses the **LLM Gateway pattern** — the same architecture as enterprise tools like [LiteLLM](https://www.litellm.ai/ai-gateway) — but in a single Python script you can set up in 10 minutes. DeepSeek, Kimi, Gemini, Perceptron — all switchable by hashtag, with full privacy and a hard spending cap.

**⚠️ Built and tested on Windows 11.** macOS and Linux instructions are provided as a courtesy.

---

## 🧠 What You're Building

This isn't just a proxy — it's a **self-built LLM Gateway** that:

- Routes requests to multiple AI models based on hashtags and prefixes
- Controls costs with OpenRouter's prepaid system (no surprise bills)
- Handles retries, provider filtering, and prompt caching
- Keeps your API keys secure on your machine
- Optionally route to your own local models (Ollama, vLLM, LM Studio, etc.) instead of OpenRouter

---

## 💰 What You'll Pay

| User Type         | Monthly Cost | vs. Cursor Ultra |
| ----------------- | :----------: | :--------------: |
| Casual            |     £2–4     | Saves £196/month |
| Typical Developer |   **£4–8**   | Saves £192/month |
| Power User        |    £12–16    | Saves £184/month |

---

## 🧠 Models at Your Fingertips

| Model             | Use via   | Best for                                  |
| ----------------- | --------- | ----------------------------------------- |
| DeepSeek V4 Pro   | Default   | Everyday workhorse                        |
| Gemini 2.5 Flash  | `#flash`  | Cheap bulk edits                          |
| Kimi K2.5         | `#kimi`   | Critical multi-step tasks                 |
| Perceptron Mk1    | `#vision` | Screenshots & UI analysis                 |
| DeepSeek Chat     | `#dc`     | Simple prompts on a budget                |
| Ring 2.6 1T       | `#ring`   | Deep reasoning (no tools)                 |
| DeepSeek V4 Pro   | `#pro`    | Explicit alias for planning               |
| DeepSeek V4 Flash | `#v4`     | Legacy workhorse (cheaper, less reliable) |

---

## 🛠️ What's Included

- A local proxy (~200 lines of Python) that routes requests to OpenRouter with hashtag-based model switching
- MCP servers for filesystem access, memory, and documentation (kept minimal to control token costs)
- A production-ready `.clinerules` file for code quality and browser safety
- Maintenance scripts to keep everything fresh
- An AI context block you can paste into DeepSeek Chat, ChatGPT, or Claude
- Real-world cost data from building a complete Next.js + Payload CMS app
- All code available as standalone files: `proxy.py`, `update-stack.ps1`, `check_models.ps1`

---

## 📖 Read the Full Guide

👉 **[View the Blog](https://code20.github.io/cursor-cline-addition/)**

It covers:

- Setting up OpenRouter with hard spending caps and privacy guardrails
- Building the LLM Gateway proxy with all production fixes
- Using your own local models instead of OpenRouter (Ollama, vLLM, etc.)
- Installing and configuring Cline with MCP servers
- The complete `.clinerules` file for browser safety and code quality
- Real-world cost data: £14.72 for a full production month
- Troubleshooting every bug encountered and fixed

---

## ⚡ Quick Start (Windows 11)

```powershell
# 1. Create the proxy directory
New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.config\ultra-lite-proxy
cd $env:USERPROFILE\.config\ultra-lite-proxy

# 2. Copy .env.example and add your OpenRouter key
Copy-Item .env.example .env
# Then edit .env and replace sk-or-v1-your-key-here with your real key

# 3. Set up Python
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn httpx python-dotenv

# 4. Install MCP servers
npm install -g @modelcontextprotocol/server-filesystem @modelcontextprotocol/server-memory @modelcontextprotocol/server-sequential-thinking @arabold/docs-mcp-server

# 5. Download the scripts from this repo into the folder:
#    - proxy.py
#    - update-stack.ps1
#    - check_models.ps1

# 6. Start the proxy
python proxy.py
```

Then read the blog for Cline configuration, `.clinerules`, and MCP setup.

---

## 📊 Real-World Test

This setup was battle-tested by building a complete production app:

- **Car-hire website** with Next.js 15 + Payload CMS 3
- **Admin panel** with 2FA, custom avatars, and rich content editing
- **Full documentation** (README, developer reference, owner guide)
- **81.5M tokens**, 2,000 requests, **$18.40 total** for the month

---

## 🤝 Who This Is For

- Developers who want powerful AI coding tools without a £160/month subscription
- Hobbyists and learners building side projects on a budget
- Anyone tired of vendor lock-in and wanting full privacy control
- Windows users who want a tested, working setup (Mac/Linux instructions included as courtesy)

---

## 🏗️ Architecture

This project follows the **LLM Gateway Pattern** — the same architecture used by [LiteLLM](https://www.litellm.ai/ai-gateway) and other enterprise AI infrastructure tools. Instead of connecting directly to each AI provider, all requests go through a single proxy that handles routing, cost control, error recovery, and API key security.

---

## 📁 Files in This Repo

| File                    | Purpose                                                 |
| ----------------------- | ------------------------------------------------------- |
| `index.html`            | The complete blog guide                                 |
| `proxy.py`              | The LLM Gateway proxy script                            |
| `update-stack.ps1`      | Weekly maintenance/health-check script                  |
| `check_models.ps1`      | Model availability watcher                              |
| `README.md`             | You're reading it                                       |
| `.env.example`          | Starter template — copy to `.env` and add your key      |
| `.clinerules.universal` | Universal rules — copy to your project as `.clinerules` |
| `.clinerules.example`   | Full template with project-specific examples            |
| `LICENSE`               | MIT                                                     |

---

## 📝 License

MIT — use it, modify it, share it. Just keep building cool stuff.

---

## 🔗 Links

- [OpenRouter](https://openrouter.ai) — API access to 400+ models
- [Cursor](https://cursor.com) — Free AI code editor
- [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) — Agentic coding extension
- [LiteLLM](https://www.litellm.ai/ai-gateway) — The enterprise LLM Gateway (what you're building, but simpler)
- [Full Blog Guide](https://code20.github.io/cursor-cline-addition/)
