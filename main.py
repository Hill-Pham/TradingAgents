import sys
import io

# Set UTF-8 encoding for console output (fixes Unicode errors on Windows)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"  # Use a different model
config["backend_url"] = "https://generativelanguage.googleapis.com/v1" 
# config["deep_think_llm"] = "gemini-2.5-pro"  # Use a different model
config["deep_think_llm"] = "gemini-2.5-pro"  # Use a different model
config["quick_think_llm"] = "gemini-2.0-flash"  # Use a different model
config["max_debate_rounds"] = 2  # Increase debate rounds

# config = DEFAULT_CONFIG.copy()
# config["llm_provider"] = "openai"  # Use a different model
# config["deep_think_llm"] = "gpt-4.1-nano"  # Use a different model
# config["quick_think_llm"] = "gpt-4.1-nano"  # Use a different model
# config["max_debate_rounds"] = 2  # Increase debate rounds

# Configure data vendors (default uses yfinance and alpha_vantage)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: yfinance, alpha_vantage, local
    "technical_indicators": "yfinance",      # Options: yfinance, alpha_vantage, local
    "fundamental_data": "alpha_vantage",     # Options: openai, alpha_vantage, local
    "news_data": "alpha_vantage",            # Options: openai, alpha_vantage, google, local
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("XRP-USDT", "2025-11-28")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
