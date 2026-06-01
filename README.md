# Cursor Cline Addition — A £4–8/month AI Coding Assistant

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
- Works with Cline for agentic coding (file editing, terminal commands, browser screenshots)

---

## 💰 What You'll Pay

| User Type | Monthly Cost | vs. Cursor Ultra |
|-----------|:-----------:|:----------------:|
| Casual | £2–4 | Saves £196/month |
| Typical Developer | **£4–8** | Saves £192/month |
| Power User | £12–16 | Saves £184/month |

---

## 🧠 Models at Your Fingertips

| Model | Use via | Best for |
|-------|---------|----------|
| DeepSeek V4 Pro | Default | Everyday workhorse |
| Gemini 2.5 Flash | `#flash` | Cheap bulk edits |
| Kimi K2.5 | `#kimi` | Critical multi-step tasks |
| Perceptron Mk1 | `#vision` | Screenshots & UI analysis |
| DeepSeek Chat | `#dc` | Simple prompts on a budget |
| Ring 2.6 1T | `#ring` | Deep reasoning (no tools) |

---

## 🛠️ What's Included

- A local proxy (~200 lines of Python) that routes requests to OpenRouter with hashtag-based model switching
- MCP servers for filesystem access, memory, browser screenshots, GitHub analysis, and documentation
- A production-ready `.clinerules` file for code quality and browser safety
- Maintenance scripts to keep everything fresh
- An AI context block you can paste into DeepSeek Chat, ChatGPT, or Claude
- Real-world cost data from building a complete Next.js + Payload CMS app

---

## 📖 Read the Full Guide

👉 **[View the Blog](https://code20.github.io/cursor-cline-addition/)**

It covers:
- Setting up OpenRouter with hard spending caps and privacy guardrails
- Building the LLM Gateway proxy with all production fixes
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

# 2. Create .env with your OpenRouter key
"OPENROUTER_API_KEY=sk-or-v1-..." | Out-File -Encoding ascii .env
"DEFAULT_MODEL=deepseek/deepseek-v4-pro" | Out-File -Encoding ascii -Append .env

# 3. Set up Python
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn httpx python-dotenv

# 4. Install MCP servers
npm install -g @modelcontextprotocol/server-filesystem @modelcontextprotocol/server-memory @modelcontextprotocol/server-sequential-thinking @hisma/server-puppeteer gitingest-mcp @arabold/docs-mcp-server

# 5. Download proxy.py from the repo and start it
python proxy.py
