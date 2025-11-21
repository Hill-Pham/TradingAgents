# LLM Provider Configuration Guide

TradingAgents supports multiple LLM providers, allowing you to choose the best AI models for your trading analysis needs.

## Supported Providers

1. **OpenAI** - GPT-4, GPT-4o, o1, o3, o4 models
2. **Google** - Gemini 2.0, 2.5 models
3. **Anthropic** - Claude 3.5, 4.0 models
4. **OpenRouter** - Access to multiple models through one API
5. **Ollama** - Run models locally on your machine

## Quick Start

### 1. Set Up API Keys

Copy `.env.example` to `.env` and add your API key(s):

```bash
cp .env.example .env
```

Then edit `.env` and add your keys:

```env
# Choose the provider(s) you want to use
OPENAI_API_KEY=sk-your-actual-openai-key
GOOGLE_API_KEY=your-actual-google-key
ANTHROPIC_API_KEY=your-actual-anthropic-key
```

### 2. Configure Provider

You can configure the LLM provider in two ways:

#### Option A: Using CLI (Interactive)

When you run the CLI, you'll be prompted to select:
1. LLM Provider (OpenAI, Google, Anthropic, etc.)
2. Quick-thinking model (for fast analysis)
3. Deep-thinking model (for complex reasoning)

```bash
python -m cli.main
```

#### Option B: Using Configuration File

Edit `tradingagents/default_config.py`:

```python
DEFAULT_CONFIG = {
    # ... other settings ...
    
    "llm_provider": "google",  # Change to your preferred provider
    "deep_think_llm": "gemini-2.5-pro-preview-06-05",
    "quick_think_llm": "gemini-2.5-flash",
    "backend_url": "https://generativelanguage.googleapis.com/v1",
    
    # ... other settings ...
}
```

## Provider-Specific Configuration

### OpenAI

**API Key**: Get from https://platform.openai.com/api-keys

**Configuration**:
```python
"llm_provider": "openai"
"deep_think_llm": "o4-mini"        # or "o1", "o3-mini", "o3"
"quick_think_llm": "gpt-4o-mini"   # or "gpt-4o", "gpt-4.1-mini"
"backend_url": "https://api.openai.com/v1"
```

**Environment Variable**:
```env
OPENAI_API_KEY=sk-your-openai-api-key
```

**Recommended Models**:
- Quick-thinking: `gpt-4o-mini` (fast, cost-effective)
- Deep-thinking: `o4-mini` (advanced reasoning)

---

### Google Gemini

**API Key**: Get from https://makersuite.google.com/app/apikey

**Configuration**:
```python
"llm_provider": "google"
"deep_think_llm": "gemini-2.5-pro-preview-06-05"  # or "gemini-2.5-flash"
"quick_think_llm": "gemini-2.5-flash"              # or "gemini-2.0-flash"
"backend_url": "https://generativelanguage.googleapis.com/v1"
```

**Environment Variable**:
```env
GOOGLE_API_KEY=your-google-api-key
```

**Recommended Models**:
- Quick-thinking: `gemini-2.5-flash` (fast, adaptive thinking)
- Deep-thinking: `gemini-2.5-pro-preview-06-05` (most capable)

**Notes**:
- Gemini models automatically convert system messages to human messages
- Temperature is set to 0.1 for consistent financial analysis
- No need to specify `max_tokens` - handled automatically

---

### Anthropic Claude

**API Key**: Get from https://console.anthropic.com/

**Configuration**:
```python
"llm_provider": "anthropic"
"deep_think_llm": "claude-sonnet-4-0"           # or "claude-opus-4-0"
"quick_think_llm": "claude-3-5-sonnet-latest"   # or "claude-3-5-haiku-latest"
"backend_url": "https://api.anthropic.com/"
```

**Environment Variable**:
```env
ANTHROPIC_API_KEY=your-anthropic-api-key
```

**Recommended Models**:
- Quick-thinking: `claude-3-5-sonnet-latest` (balanced performance)
- Deep-thinking: `claude-sonnet-4-0` (excellent reasoning)

---

### OpenRouter

**API Key**: Get from https://openrouter.ai/keys

**Configuration**:
```python
"llm_provider": "openrouter"
"deep_think_llm": "deepseek/deepseek-chat-v3-0324:free"
"quick_think_llm": "google/gemini-2.0-flash-exp:free"
"backend_url": "https://openrouter.ai/api/v1"
```

**Environment Variable**:
```env
OPENROUTER_API_KEY=your-openrouter-api-key
```

**Recommended Models**:
- Quick-thinking: `google/gemini-2.0-flash-exp:free`
- Deep-thinking: `deepseek/deepseek-chat-v3-0324:free`

**Notes**:
- OpenRouter provides access to many models through one API
- Some models are free (marked with `:free`)
- Uses OpenAI-compatible API format

---

### Ollama (Local)

**Setup**: Install Ollama from https://ollama.ai/

**Configuration**:
```python
"llm_provider": "ollama"
"deep_think_llm": "llama3.1"   # or "qwen3"
"quick_think_llm": "llama3.2"  # or "llama3.1"
"backend_url": "http://localhost:11434/v1"
```

**No API Key Required** - runs locally!

**Setup Steps**:
1. Install Ollama
2. Pull models: `ollama pull llama3.2` and `ollama pull llama3.1`
3. Ensure Ollama is running: `ollama serve`

**Recommended Models**:
- Quick-thinking: `llama3.2` (8B parameters, fast)
- Deep-thinking: `llama3.1` (70B parameters, better reasoning)

**Notes**:
- Completely free and private
- No internet required (after model download)
- Requires good hardware (GPU recommended)

---

## Model Selection Guide

### Quick-Thinking Models
Used for fast analysis tasks like:
- Market data interpretation
- News sentiment analysis
- Social media analysis
- Technical indicator analysis

**Recommendations**:
- Budget-conscious: `gemini-2.5-flash` (Google) or `gpt-4o-mini` (OpenAI)
- Best performance: `claude-3-5-sonnet-latest` (Anthropic)
- Local/Private: `llama3.2` (Ollama)

### Deep-Thinking Models
Used for complex reasoning tasks like:
- Investment strategy formulation
- Risk analysis
- Portfolio management decisions
- Multi-step reasoning

**Recommendations**:
- Best reasoning: `o4-mini` (OpenAI) or `claude-sonnet-4-0` (Anthropic)
- Best value: `gemini-2.5-pro-preview-06-05` (Google)
- Local/Private: `llama3.1` (Ollama)

## Troubleshooting

### "Failed to initialize Google Gemini models"
- Check your `GOOGLE_API_KEY` in `.env` file
- Verify the model name is correct (e.g., `gemini-2.5-flash`)
- Ensure you have API access enabled in Google AI Studio

### "Invalid API key"
- Make sure you copied the full API key without spaces
- Check that your API key is for the correct provider
- Verify your API key hasn't expired

### "Model not found"
- Double-check the model name spelling
- Some models may require special access or billing setup
- For Ollama, ensure you've pulled the model: `ollama pull model-name`

### "Connection refused" (Ollama)
- Make sure Ollama is running: `ollama serve`
- Check that the port is correct (default: 11434)
- Verify no firewall is blocking localhost connections

## Cost Considerations

### Most Cost-Effective
1. **Ollama** - Free (local hardware costs)
2. **OpenRouter free models** - Free tier available
3. **Google Gemini Flash** - Very low cost per token

### Best Performance per Dollar
1. **Google Gemini 2.5 Flash** - Excellent balance
2. **OpenAI GPT-4o-mini** - Good for quick tasks
3. **Anthropic Haiku** - Fast and affordable

### Premium Options
1. **OpenAI o4-mini / o1** - Advanced reasoning
2. **Anthropic Claude Opus 4** - Highest quality
3. **Google Gemini Pro** - Strong all-around

## Switching Providers

You can easily switch between providers by changing the configuration:

1. Update `.env` with the new provider's API key
2. Either:
   - Use the CLI and select the new provider interactively, OR
   - Edit `default_config.py` to change the default provider
3. Restart the application

The system will automatically use the new provider and models!

## Mixed Provider Usage

You can even use different providers for quick vs deep thinking:

**Example**: OpenAI for deep thinking, Gemini for quick thinking
```python
# This requires using programmatic configuration
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"  # Primary provider
# Then manually override in code to use different providers for different models
```

Note: The CLI currently uses one provider for both models, but you can programmatically configure mixed usage.

## Support

For issues with:
- **OpenAI**: Check https://platform.openai.com/docs
- **Google**: Check https://ai.google.dev/docs
- **Anthropic**: Check https://docs.anthropic.com/
- **OpenRouter**: Check https://openrouter.ai/docs
- **Ollama**: Check https://github.com/ollama/ollama

For TradingAgents-specific issues, please open an issue on the GitHub repository.
