from typing import Annotated
from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import os
import requests
import pandas as pd
import time
from .stockstats_utils import StockstatsUtils

def get_YFin_data_online(
    symbol: Annotated[str, "trading pair symbol like BTCUSDT, ETHUSDT, or stock symbols"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    interval: str = "1d"
):
    """
    Get OHLCV data from Binance API or fallback to yfinance for traditional stocks.
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT') or stock symbol (e.g., 'AAPL')
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format  
        interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
    
    Returns:
        CSV string with OHLCV data
    """
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")
    
    # First try Binance API for crypto pairs
    if _is_crypto_symbol(symbol):
        try:
            print(f"Trying Binance API for symbol {symbol}...")
            return _get_binance_data(symbol, start_date, end_date, interval)
        except Exception as e:
            print(f"Binance API failed for {symbol}: {e}")
            # Fall through to yfinance
    
    # Fallback to yfinance for traditional stocks
    try:
        return _get_yfinance_data(symbol, start_date, end_date)
    except Exception as e:
        return f"Error: Both Binance and yfinance failed for symbol '{symbol}': {e}"


def _is_crypto_symbol(symbol: str) -> bool:
    """Check if symbol looks like a crypto trading pair."""
    symbol = symbol.upper()
    # Common crypto pair patterns
    crypto_suffixes = ['USDT', 'USDC', 'BTC', 'ETH', 'BNB', 'XRP']
    return any(symbol.endswith(suffix) for suffix in crypto_suffixes)


def _get_binance_data(symbolRaw: str, start_date: str, end_date: str, interval: str = "1d") -> str:
    """Get OHLCV data from Binance REST API."""
    # Convert dates to timestamps (milliseconds)
    start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
    end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

    # parse BTC-USDT to BTCUSDT
    symbol = _parse_crypto_symnbol(symbolRaw)
    
    print(f"Fetching Binance data for {symbol} from {start_date} to {end_date}...")
    
    # Binance API endpoint
    url = "https://api.binance.com/api/v3/klines"
    
    all_data = []
    current_start = start_timestamp
    
    # Binance limits to 1000 klines per request
    while current_start < end_timestamp:
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "startTime": current_start,
            "endTime": end_timestamp,
            "limit": 1000
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            break
            
        all_data.extend(data)
        
        # Update start time to the last kline's close time + 1ms
        current_start = data[-1][6] + 1
        
        # Add small delay to respect rate limits
        time.sleep(0.1)
    
    if not all_data:
        raise Exception(f"No data found for symbol '{symbol}' between {start_date} and {end_date}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    # Convert timestamp to datetime
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Select and rename columns to match standard OHLCV format
    ohlcv_df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']].copy()
    ohlcv_df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    # Convert price columns to float
    price_columns = ['Open', 'High', 'Low', 'Close']
    for col in price_columns:
        ohlcv_df[col] = ohlcv_df[col].astype(float).round(8)
        
    ohlcv_df['Volume'] = ohlcv_df['Volume'].astype(float).round(8)
    
    # Set date as index
    ohlcv_df.set_index('Date', inplace=True)
    
    # Filter data to exact date range
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    ohlcv_df = ohlcv_df[(ohlcv_df.index >= start_dt) & (ohlcv_df.index <= end_dt)]
    
    # Add header information
    header = f"# Binance data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Interval: {interval}\n"
    header += f"# Total records: {len(ohlcv_df)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    return header + ohlcv_df.to_csv()


def _get_yfinance_data(symbol: str, start_date: str, end_date: str) -> str:
    """Get data from yfinance as fallback for traditional stocks."""
    # Create ticker object
    ticker = yf.Ticker(symbol.upper())

    # Fetch historical data for the specified date range
    data = ticker.history(start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        raise Exception(f"No data found for symbol '{symbol}' between {start_date} and {end_date}")

    # Remove timezone info from index for cleaner output
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # Round numerical values to 2 decimal places for cleaner display
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # Convert DataFrame to CSV string
    csv_string = data.to_csv()

    # Add header information
    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string

def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:

    best_ind_params = {
        # Moving Averages
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        # MACD Related
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        # Momentum Indicators
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        # Volatility Indicators
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        # Volume-Based Indicators
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - relativedelta(days=look_back_days)

    # Optimized: Get stock data once and calculate indicators for all dates
    try:
        indicator_data = _get_stock_stats_bulk(symbol, indicator, curr_date)
        
        # Generate the date range we need
        current_dt = curr_date_dt
        date_values = []
        
        while current_dt >= before:
            date_str = current_dt.strftime('%Y-%m-%d')
            
            # Look up the indicator value for this date
            if date_str in indicator_data:
                indicator_value = indicator_data[date_str]
            else:
                indicator_value = "N/A: Not a trading day (weekend or holiday)"
            
            date_values.append((date_str, indicator_value))
            current_dt = current_dt - relativedelta(days=1)
        
        # Build the result string
        ind_string = ""
        for date_str, value in date_values:
            ind_string += f"{date_str}: {value}\n"
        
    except Exception as e:
        print(f"Error getting bulk stockstats data: {e}")
        # Fallback to original implementation if bulk method fails
        ind_string = ""
        curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        while curr_date_dt >= before:
            indicator_value = get_stockstats_indicator(
                symbol, indicator, curr_date_dt.strftime("%Y-%m-%d")
            )
            ind_string += f"{curr_date_dt.strftime('%Y-%m-%d')}: {indicator_value}\n"
            curr_date_dt = curr_date_dt - relativedelta(days=1)

    result_str = (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {end_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "No description available.")
    )

    return result_str


def _get_stock_stats_bulk(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to calculate"],
    curr_date: Annotated[str, "current date for reference"]
) -> dict:
    """
    Optimized bulk calculation of stock stats indicators.
    Uses Binance data for crypto symbols, yfinance for stocks.
    Returns dict mapping date strings to indicator values.
    """
    from .config import get_config
    import pandas as pd
    from stockstats import wrap
    import os
    
    config = get_config()
    online = config["data_vendors"]["technical_indicators"] != "local"
    
    if not online:
        # Local data path
        try:
            data = pd.read_csv(
                os.path.join(
                    config.get("data_cache_dir", "data"),
                    f"{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
                )
            )
            df = wrap(data)
        except FileNotFoundError:
            raise Exception("Stockstats fail: Yahoo Finance data not fetched yet!")
    else:
        # Online data fetching with caching - try Binance first for crypto
        today_date = pd.Timestamp.today()
        curr_date_dt = pd.to_datetime(curr_date)
        
        end_date = today_date
        start_date = today_date - pd.DateOffset(years=5)  # Reduced to 5 years for better performance
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        os.makedirs(config["data_cache_dir"], exist_ok=True)
        
        # Try Binance data first for crypto symbols
        if _is_crypto_symbol(symbol):
            data_file = os.path.join(
                config["data_cache_dir"],
                f"{symbol}-Binance-data-{start_date_str}-{end_date_str}.csv",
            )
            
            if os.path.exists(data_file):
                data = pd.read_csv(data_file, index_col=0, parse_dates=True)
                data = data.reset_index()
                data.rename(columns={'Date': 'Date'}, inplace=True)
            else:
                # Fetch from Binance and convert to stockstats format
                try:
                    binance_csv = _get_binance_data(symbol, start_date_str, end_date_str, "1d")
                    # Parse the CSV content (skip header lines)
                    lines = binance_csv.split('\n')
                    csv_content = '\n'.join([line for line in lines if not line.startswith('#')])
                    
                    from io import StringIO
                    data = pd.read_csv(StringIO(csv_content), index_col=0, parse_dates=True)
                    data = data.reset_index()
                    
                    # Ensure proper column names for stockstats
                    if 'Date' not in data.columns and data.index.name:
                        data = data.reset_index()
                    
                    # Save to cache
                    data.to_csv(data_file, index=False)
                    print(f"Cached Binance data for {symbol}")
                    
                except Exception as e:
                    print(f"Binance fetch failed for {symbol}: {e}, falling back to yfinance")
                    # Fallback to yfinance for crypto (some exchanges might have it)
                    data = _fetch_yfinance_data(symbol, start_date_str, end_date_str, config)
        else:
            # Use yfinance for traditional stocks
            data = _fetch_yfinance_data(symbol, start_date_str, end_date_str, config)
        
        df = wrap(data)
        if 'Date' in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    
    # Calculate the indicator for all rows at once
    df[indicator]  # This triggers stockstats to calculate the indicator
    
    # Create a dictionary mapping date strings to indicator values
    result_dict = {}
    for _, row in df.iterrows():
        date_str = row["Date"] if 'Date' in row else str(row.name)
        indicator_value = row[indicator]
        
        # Handle NaN/None values
        if pd.isna(indicator_value):
            result_dict[date_str] = "N/A"
        else:
            result_dict[date_str] = str(indicator_value)
    
    return result_dict


def _fetch_yfinance_data(symbol: str, start_date_str: str, end_date_str: str, config: dict) -> pd.DataFrame:
    """Helper function to fetch data from yfinance with caching."""
    import os
    
    data_file = os.path.join(
        config["data_cache_dir"],
        f"{symbol}-YFin-data-{start_date_str}-{end_date_str}.csv",
    )
    
    if os.path.exists(data_file):
        data = pd.read_csv(data_file)
        data["Date"] = pd.to_datetime(data["Date"])
    else:
        data = yf.download(
            symbol,
            start=start_date_str,
            end=end_date_str,
            multi_level_index=False,
            progress=False,
            auto_adjust=True,
        )
        data = data.reset_index()
        data.to_csv(data_file, index=False)
        print(f"Cached yfinance data for {symbol}")
    
    return data


def get_stockstats_indicator(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
) -> str:

    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date = curr_date_dt.strftime("%Y-%m-%d")

    # For crypto symbols, try to use cached Binance data first
    if _is_crypto_symbol(symbol):
        try:
            # Try to get the indicator from bulk calculation (uses Binance cache)
            indicator_data = _get_stock_stats_bulk(symbol, indicator, curr_date)
            
            # Look up the specific date
            if curr_date in indicator_data:
                indicator_value = indicator_data[curr_date]
                if indicator_value != "N/A":
                    return str(indicator_value)
            
            # If not found in cache, fall through to StockstatsUtils
            print(f"Date {curr_date} not found in Binance cache for {symbol}, using StockstatsUtils fallback")
            
        except Exception as e:
            print(f"Error getting Binance indicator data for {symbol}: {e}, falling back to StockstatsUtils")

    # Fallback to original StockstatsUtils for stocks or if Binance fails
    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date,
        )
    except Exception as e:
        print(
            f"Error getting stockstats indicator data for indicator {indicator} on {curr_date}: {e}"
        )
        return ""

    return str(indicator_value)


def get_balance_sheet(
    ticker: Annotated[str, "ticker symbol of the company"],
    freq: Annotated[str, "frequency of data: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
):
    """Get balance sheet data from yfinance."""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        if freq.lower() == "quarterly":
            data = ticker_obj.quarterly_balance_sheet
        else:
            data = ticker_obj.balance_sheet
            
        if data.empty:
            return f"No balance sheet data found for symbol '{ticker}'"
            
        # Convert to CSV string for consistency with other functions
        csv_string = data.to_csv()
        
        # Add header information
        header = f"# Balance Sheet data for {ticker.upper()} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"Error retrieving balance sheet for {ticker}: {str(e)}"


def get_cashflow(
    ticker: Annotated[str, "ticker symbol of the company"],
    freq: Annotated[str, "frequency of data: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
):
    """Get cash flow data from yfinance."""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        if freq.lower() == "quarterly":
            data = ticker_obj.quarterly_cashflow
        else:
            data = ticker_obj.cashflow
            
        if data.empty:
            return f"No cash flow data found for symbol '{ticker}'"
            
        # Convert to CSV string for consistency with other functions
        csv_string = data.to_csv()
        
        # Add header information
        header = f"# Cash Flow data for {ticker.upper()} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"Error retrieving cash flow for {ticker}: {str(e)}"


def get_income_statement(
    ticker: Annotated[str, "ticker symbol of the company"],
    freq: Annotated[str, "frequency of data: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
):
    """Get income statement data from yfinance."""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        if freq.lower() == "quarterly":
            data = ticker_obj.quarterly_income_stmt
        else:
            data = ticker_obj.income_stmt
            
        if data.empty:
            return f"No income statement data found for symbol '{ticker}'"
            
        # Convert to CSV string for consistency with other functions
        csv_string = data.to_csv()
        
        # Add header information
        header = f"# Income Statement data for {ticker.upper()} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"Error retrieving income statement for {ticker}: {str(e)}"


def get_insider_transactions(
    ticker: Annotated[str, "ticker symbol of the company"]
):
    """Get insider transactions data from yfinance."""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = ticker_obj.insider_transactions
        
        if data is None or data.empty:
            return f"No insider transactions data found for symbol '{ticker}'"
            
        # Convert to CSV string for consistency with other functions
        csv_string = data.to_csv()
        
        # Add header information
        header = f"# Insider Transactions data for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"Error retrieving insider transactions for {ticker}: {str(e)}"
    
def _parse_crypto_symnbol(symbol: str) -> str:
    """Convert symbols like BTC-USDT to BTCUSDT for Binance API."""
    return symbol.replace("-", "").upper()    