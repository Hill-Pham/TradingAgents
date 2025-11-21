# Quick Start: Switch Between OpenAI and Gemini

## Option 1: Use CLI (Easiest) ⭐

```bash
python -m cli.main
```

When prompted:
- **Step 5**: Choose "OpenAI" or "Google"
- **Step 6**: Select your models

That's it! No file editing needed.

---

## Option 2: Edit Config File

### Switch to OpenAI

Edit `tradingagents/default_config.py`:

```python
"llm_provider": "openai",
"deep_think_llm": "o4-mini",
"quick_think_llm": "gpt-4o-mini",
"backend_url": "https://api.openai.com/v1",
```

Make sure `OPENAI_API_KEY` is in your `.env` file.

### Switch to Google Gemini

Edit `tradingagents/default_config.py`:

```python
"llm_provider": "google",
"deep_think_llm": "gemini-2.5-pro-preview-06-05",
"quick_think_llm": "gemini-2.5-flash",
"backend_url": "https://generativelanguage.googleapis.com/v1",
```

Make sure `GOOGLE_API_KEY` is in your `.env` file.

---

## Your API Keys (Already Configured)

✅ OpenAI API Key - Working  
✅ Google API Key - Configured (check quota limits)

---

## Test Your Setup

```bash
python test_llm_providers.py
```

This verifies both providers are working correctly.

---

## Recommended Models

### OpenAI
- Quick: `gpt-4o-mini` (fast, cheap)
- Deep: `o4-mini` (best reasoning)

### Google Gemini
- Quick: `gemini-2.5-flash` (fast, adaptive)
- Deep: `gemini-2.5-pro-preview-06-05` (most capable)

---

## Full Documentation

📖 Complete guide: `docs/LLM_PROVIDERS.md`  
📋 Configuration summary: `CONFIGURATION_SUMMARY.md`

---

**Current Status**: OpenAI is configured as default and working ✅
