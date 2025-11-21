import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.path.join(os.path.dirname(__file__), "..", "FR1-data"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",  # Options: "openai", "google" (Gemini), "anthropic", "ollama", "openrouter"
    "deep_think_llm": "o4-mini",  # Model for complex reasoning tasks
    "quick_think_llm": "gpt-4o-mini",  # Model for quick analysis tasks
    "backend_url": "https://api.openai.com/v1",  # API endpoint (varies by provider)
    # 
    # Example configurations:
    # OpenAI:
    #   llm_provider: "openai"
    #   deep_think_llm: "o4-mini" or "o1" or "o3-mini"
    #   quick_think_llm: "gpt-4o-mini" or "gpt-4o"
    #   backend_url: "https://api.openai.com/v1"
    #
    # Google Gemini:
    #   llm_provider: "google"
    #   deep_think_llm: "gemini-2.5-pro-preview-06-05" or "gemini-2.5-flash"
    #   quick_think_llm: "gemini-2.0-flash" or "gemini-2.5-flash"
    #   backend_url: "https://generativelanguage.googleapis.com/v1"
    #
    # Anthropic:
    #   llm_provider: "anthropic"
    #   deep_think_llm: "claude-sonnet-4-0" or "claude-opus-4-0"
    #   quick_think_llm: "claude-3-5-sonnet-latest"
    #   backend_url: "https://api.anthropic.com/"
    #
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: yfinance, alpha_vantage, local
        "technical_indicators": "yfinance",  # Options: yfinance, alpha_vantage, local
        "fundamental_data": "alpha_vantage", # Options: openai, alpha_vantage, local
        "news_data": "alpha_vantage",        # Options: openai, alpha_vantage, google, local
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
        # Example: "get_news": "openai",               # Override category default
    },
}

