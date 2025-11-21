# TradingAgents - LLM Provider Configuration Summary

## ✅ System Status

Your TradingAgents installation now supports **flexible LLM provider selection**! You can easily switch between OpenAI and Google Gemini (or other providers) based on your needs.

## 🎯 What You Can Do

### 1. Use OpenAI (Currently Configured)
- **Provider**: OpenAI
- **Quick-thinking model**: `gpt-4o-mini`
- **Deep-thinking model**: `o4-mini`
- **Status**: ✅ Working and tested

### 2. Use Google Gemini
- **Provider**: Google
- **Quick-thinking model**: `gemini-2.5-flash` or `gemini-1.5-flash`
- **Deep-thinking model**: `gemini-2.5-pro-preview-06-05`
- **Status**: ⚠️ API key configured, but has quota limits on free tier

### 3. Use Other Providers
- Anthropic Claude
- OpenRouter
- Ollama (local)

## 🚀 How to Switch Providers

### Method 1: Interactive CLI (Recommended)

When you run the application, you'll be prompted to select the provider:

```bash
python -m cli.main
```

The CLI will ask you:
1. **Step 5**: Select LLM Provider (OpenAI, Google, Anthropic, etc.)
2. **Step 6**: Select Quick-thinking model
3. **Step 6**: Select Deep-thinking model

This is the **easiest way** and doesn't require editing any files!

### Method 2: Edit Default Configuration

Edit `tradingagents/default_config.py`:

**For OpenAI** (current default):
```python
DEFAULT_CONFIG = {
    "llm_provider": "openai",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # ... other settings ...
}
```

**For Google Gemini**:
```python
DEFAULT_CONFIG = {
    "llm_provider": "google",
    "deep_think_llm": "gemini-2.5-pro-preview-06-05",
    "quick_think_llm": "gemini-2.5-flash",
    "backend_url": "https://generativelanguage.googleapis.com/v1",
    # ... other settings ...
}
```

## 📋 Current Configuration

### API Keys (in .env)
```
✅ OPENAI_API_KEY - Configured and working
✅ GOOGLE_API_KEY - Configured (quota limited on free tier)
✅ ALPHA_VANTAGE_API_KEY - Configured
```

### Default Provider
```
Current: OpenAI
Models: gpt-4o-mini (quick) + o4-mini (deep)
```

## 🔧 Files Modified

1. **`tradingagents/graph/trading_graph.py`**
   - Improved Google Gemini initialization
   - Better error handling for all providers
   - Cleaner provider selection logic

2. **`tradingagents/default_config.py`**
   - Updated documentation with clear examples
   - Added configuration examples for all providers

3. **`.env.example`**
   - Updated with all provider API key placeholders
   - Added helpful configuration examples

4. **`docs/LLM_PROVIDERS.md`** (NEW)
   - Comprehensive guide for all providers
   - Setup instructions
   - Model recommendations
   - Troubleshooting tips

5. **`test_llm_providers.py`** (NEW)
   - Test script to verify provider configuration
   - Validates API keys and model access

## 📖 Documentation

### Quick Reference
- **Main Guide**: `docs/LLM_PROVIDERS.md` - Complete setup guide for all providers
- **Example Config**: `.env.example` - API key template
- **Test Script**: `test_llm_providers.py` - Verify your setup

### Model Recommendations

| Use Case | OpenAI | Google Gemini | Anthropic |
|----------|---------|---------------|-----------|
| Quick Analysis | gpt-4o-mini | gemini-2.5-flash | claude-3-5-haiku |
| Deep Reasoning | o4-mini | gemini-2.5-pro | claude-sonnet-4-0 |
| Best Value | gpt-4o-mini | gemini-2.5-flash | - |
| Best Quality | o1 | gemini-2.5-pro | claude-opus-4-0 |

## 🎯 Next Steps

### To Use Google Gemini

1. **Check your quota** at https://ai.dev/usage?tab=rate-limit
2. **Wait for quota reset** (usually resets every minute/hour)
3. **Upgrade to paid tier** if needed for higher limits
4. **Or use alternative models** like `gemini-1.5-flash` which may have different quotas

### To Test Your Setup

Run the test script:
```bash
python test_llm_providers.py
```

This will verify both OpenAI and Google Gemini are working correctly.

### To Run Analysis

1. **Using OpenAI** (default):
   ```bash
   python -m cli.main
   ```
   Select "OpenAI" when prompted

2. **Using Google Gemini**:
   ```bash
   python -m cli.main
   ```
   Select "Google" when prompted

## 💡 Tips

1. **Start with OpenAI** - It's currently configured and working
2. **Try different models** - Each has strengths and weaknesses
3. **Monitor costs** - Check your API usage regularly
4. **Use local Ollama** - For free, private analysis (requires local setup)

## 🆘 Troubleshooting

### Google Gemini quota exceeded
- Wait for quota reset (check https://ai.dev/usage)
- Try `gemini-1.5-flash` instead of `gemini-2.0-flash-exp`
- Consider upgrading to paid tier

### API key not working
- Verify the key in `.env` file
- Check you're using the correct provider
- Ensure no extra spaces in the key

### Model not found
- Double-check model name spelling
- Verify the model is available for your account
- Try a different model from the same provider

## 📚 Additional Resources

- OpenAI Documentation: https://platform.openai.com/docs
- Google AI Studio: https://makersuite.google.com/
- Anthropic Documentation: https://docs.anthropic.com/
- TradingAgents GitHub: https://github.com/TauricResearch/TradingAgents

---

**Last Updated**: November 20, 2025
**System Version**: Compatible with langchain-google-genai 2.0.10
