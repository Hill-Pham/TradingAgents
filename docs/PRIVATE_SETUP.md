# Private/Local Setup Guide

This guide explains how to set up TradingAgents for **completely private and local operation** without relying on external cloud APIs. This setup uses [Ollama](https://ollama.ai/) to run large language models locally on your machine.

## Why Go Private?

- **Privacy**: Your financial analysis data never leaves your machine
- **No API Costs**: No charges for LLM API usage after initial hardware investment
- **Offline Operation**: Works without internet (after initial model download)
- **Data Security**: Complete control over your data and analysis

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 16 GB | 32+ GB |
| GPU VRAM | 8 GB (optional) | 16+ GB |
| Storage | 20 GB free | 50+ GB free |
| CPU | Modern multi-core | Apple Silicon / NVIDIA GPU |

> **Note**: While CPU-only operation is possible, a GPU significantly improves performance.

### Software Requirements

- Python 3.13+ (required by TradingAgents)
- [Ollama](https://ollama.ai/) installed and running
- Git

## Quick Setup

### Step 1: Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai/) and run the installer.

### Step 2: Download Local Models

Pull the recommended models for TradingAgents:

```bash
# Quick-thinking model (smaller, faster)
ollama pull llama3.2

# Deep-thinking model (larger, more capable)
ollama pull llama3.1
```

**Alternative models by capability:**

| Use Case | Model | Size | Notes |
|----------|-------|------|-------|
| Lightweight | `llama3.2:1b` | ~1 GB | Very fast, basic analysis |
| Balanced | `llama3.2` | ~4 GB | Good balance of speed and quality |
| Capable | `llama3.1` | ~8 GB | Better reasoning |
| Advanced | `llama3.1:70b` | ~40 GB | Best quality, requires 32+ GB RAM |
| Reasoning | `qwen3` | ~8 GB | Strong reasoning capabilities |

### Step 3: Start Ollama

Ensure Ollama is running before using TradingAgents:

```bash
ollama serve
```

> **Tip**: On most systems, Ollama runs as a background service automatically after installation.

### Step 4: Clone and Setup TradingAgents

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents

# Create virtual environment
conda create -n tradingagents python=3.13
conda activate tradingagents

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure for Private Use

Create your `.env` file:

```bash
cp .env.example .env
```

Edit `.env` to configure for Ollama (no API keys needed for LLM):

```env
# No LLM API keys needed for Ollama!
# Just leave these commented out or remove them:
# OPENAI_API_KEY=
# GOOGLE_API_KEY=
# ANTHROPIC_API_KEY=

# Optional: If you want market data, add Alpha Vantage key
# You can get a free key at https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

### Step 6: Run TradingAgents with Ollama

**Using CLI (Recommended):**

```bash
python -m cli.main
```

When prompted:
- **Step 5 (LLM Provider)**: Select `Ollama`
- **Step 6 (Quick-thinking)**: Select `llama3.2`
- **Step 6 (Deep-thinking)**: Select `llama3.1`

**Using Python:**

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create private/local config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "ollama"
config["quick_think_llm"] = "llama3.2"
config["deep_think_llm"] = "llama3.1"
config["backend_url"] = "http://localhost:11434/v1"

# Initialize and run
ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

## Data Source Options for Private Setup

By default, TradingAgents uses external APIs for market data. For a fully private setup, you have these options:

### Option 1: Use yfinance (Free, No API Key)

yfinance fetches data from Yahoo Finance and doesn't require an API key:

```python
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",  # or "local" if available
    "news_data": "alpha_vantage",          # or "local" if available
}
```

### Option 2: Use Local Data

If you have your own data sources, configure local data vendors:

```python
config["data_vendors"] = {
    "core_stock_apis": "local",
    "technical_indicators": "local",
    "fundamental_data": "local",
    "news_data": "local",
}
```

> **Note**: Local data vendor support is still in development. Check for updates on the Tauric TradingDB.

### Option 3: Hybrid Setup (Recommended)

Use yfinance for stock data and Alpha Vantage for fundamentals/news:

```python
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage",
}
```

This requires only an Alpha Vantage API key (free tier available).

## Complete Private Configuration Example

Here's a complete example for maximum privacy:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Maximum privacy configuration
config = DEFAULT_CONFIG.copy()

# Use local Ollama models
config["llm_provider"] = "ollama"
config["quick_think_llm"] = "llama3.2"
config["deep_think_llm"] = "llama3.1"
config["backend_url"] = "http://localhost:11434/v1"

# Reduce API calls with lower debate rounds
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# Use yfinance for stock data (no API key needed)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",  # requires free API key
    "news_data": "alpha_vantage",          # requires free API key
}

# Initialize with private config
ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis
_, decision = ta.propagate("AAPL", "2024-05-10")
print(decision)
```

## Troubleshooting

### "Connection refused" Error

Ensure Ollama is running:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### "Model not found" Error

Pull the required model:

```bash
ollama pull llama3.2
ollama list  # Verify the model is available
```

### Slow Performance

1. **Use a smaller model**: Try `llama3.2:1b` for faster responses
2. **Enable GPU acceleration**: Ensure your GPU drivers are installed
3. **Reduce debate rounds**: Set `max_debate_rounds` to 1

### Out of Memory

1. **Use smaller models**: `llama3.2:1b` requires less RAM
2. **Close other applications**: Free up system memory
3. **Run one model at a time**: Avoid running multiple Ollama instances

## Performance Tips

1. **Model Caching**: Ollama automatically caches models in memory
2. **GPU Acceleration**: Install CUDA (NVIDIA) or use Apple Silicon for faster inference
3. **SSD Storage**: Store models on SSD for faster loading
4. **Batch Analysis**: Run multiple analyses in sequence to benefit from cached models

## Security Considerations

When running locally:

- ✅ Your analysis data stays on your machine
- ✅ No API keys for LLMs are transmitted
- ✅ No telemetry or usage tracking from LLM providers
- ⚠️ Still requires internet for stock data (unless using local data)
- ⚠️ Model files are stored locally and should be secured

## Support

- **Ollama Issues**: https://github.com/ollama/ollama/issues
- **TradingAgents Issues**: https://github.com/TauricResearch/TradingAgents/issues
- **Community**: [Discord](https://discord.com/invite/hk9PGKShPK)

---

**See also:**
- [LLM Providers Guide](./LLM_PROVIDERS.md) - Complete guide for all LLM providers
- [Quick Start](../QUICK_START.md) - General setup instructions
- [README](../README.md) - Project overview
