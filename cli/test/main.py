from typing import Annotated
from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import os
import requests
import pandas as pd
import time

# # Defining main function

def get_YFin_data_online(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # Create ticker object
    ticker = yf.Ticker(symbol.upper())

    # Fetch historical data for the specified date range
    data = ticker.history(start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        return (
            f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        )

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
    header = f"# `Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string


def test_openrouter_api():
    # from openai import OpenAI

    # client = OpenAI(
    # base_url="https://openrouter.ai/api/v1",
    # api_key="sk-d85e680b00fd46b195654e1df42b3654",
    # )
    import os
    from openai import OpenAI
    client = OpenAI(
        # The API keys for the Singapore and Beijing regions are different. To get an API key, see https://www.alibabacloud.com/help/en/model-studio/get-api-key
        # api_key=os.getenv("DASHSCOPE_API_KEY"), 
        api_key="sk-d85e680b00fd46b195654e1df42b3654", 
        # The following is the base_url for the Singapore region. If you use a model in the Beijing region, replace the base_url with https://dashscope.aliyuncs.com/compatible-mode/v1
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )
    completion = client.chat.completions.create(
        model="qwen-plus", # Model list: https://www.alibabacloud.com/help/en/model-studio/getting-started/models
        messages=[{"role": "user", "content": "Who are you?"}]
    )
    print(completion.choices[0].message.content)
        

def get_YFin_data_online_debug(symbol, start_date, end_date):
    try:
        print(f"Attempting to fetch data for {symbol}")
        
        # Create ticker object
        ticker = yf.Ticker(symbol.upper())
        print(f"Ticker object created: {ticker}")
        
        # Try to get basic info first
        try:
            info = ticker.info
            print(f"Ticker info available: {bool(info)}")
        except Exception as e:
            print(f"Error getting ticker info: {e}")
        
        # Fetch historical data
        print(f"Fetching data from {start_date} to {end_date}")
        data = ticker.history(start=start_date, end=end_date)
        print(f"Data shape: {data.shape}")
        print(f"Data empty: {data.empty}")
        
        if not data.empty:
            print(f"First few rows:\n{data.head()}")
            return data.to_csv()
        else:
            return f"No data returned for {symbol}"
            
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")
        return f"Error: {e}"


def get_binance_data(
    symbol: Annotated[str, "trading pair symbol like BTCUSDT, ETHUSDT"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    interval: Annotated[str, "Kline interval like 1d, 1h, 4h"] = "1d"
):
    """
    Get OHLCV data from Binance REST API
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format  
        interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
    
    Returns:
        CSV string with OHLCV data
    """
    try:
        # Convert dates to timestamps (milliseconds)
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)
        
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
            
            print(f"Fetching data for {symbol} from {datetime.fromtimestamp(current_start/1000)} to {datetime.fromtimestamp(end_timestamp/1000)}")
            
            response = requests.get(url, params=params)
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
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        
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
        
    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def test_binance_connection():
    """Test basic connection to Binance API"""
    try:
        url = "https://api.binance.com/api/v3/ping"
        response = requests.get(url)
        response.raise_for_status()
        print("✓ Binance API connection successful")
        return True
    except Exception as e:
        print(f"✗ Binance API connection failed: {e}")
        return False


def get_binance_symbols():
    """Get list of available trading pairs from Binance"""
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
        return symbols[:20]  # Return first 20 for testing
    except Exception as e:
        return f"Error getting symbols: {e}"

def _get_binance_data_1(symbol: str, start_date: str, end_date: str, interval: str = "1d") -> str:
    """Get OHLCV data from Binance REST API."""
    # Convert dates to timestamps (milliseconds)
    start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
    end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)
    
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


# Using the special variable 
# __name__
if __name__=="__main__":
    from tradingagents.dataflows.reddit_utils import fetch_top_from_category
    
    # print("=== Testing fetch_latest_news ===")
    # news = fetch_top_from_category(max_chars=2000, symbol="XRPUSDT")
    
    # if news:
    #     print(f"\n✓ Successfully fetched {len(news)} characters of news\n")
    #     print(news)
    # else:
    #     print("\n✗ No news data fetched\n")


    # Test Binance connection first
    print("=== Testing Binance API ===")
    if test_binance_connection():
        print("\n=== Getting BTCUSDT data ===")
        btc_data = _get_binance_data_1("BTCUSDT", "2025-11-01", "2025-11-19", "1d")
        print(btc_data)  # Print first 500 characters
        
        # print("\n=== Getting ETHUSDT data ===") 
        # eth_data = get_binance_data("ETHUSDT", "2024-11-10", "2024-11-15", "4h")
        # print(eth_data[:500])  # Print first 500 characters
        
        # print("\n=== Available symbols (first 20) ===")
        # symbols = get_binance_symbols()
        # print(symbols)
    
    # Original Yahoo Finance test (commented out)
    # test_openrouter_api()
    # print("aaa")
    # print(get_YFin_data_online("AAPL", "2024-11-01", "2024-11-15"))
    # Test with debug version
    # print(get_YFin_data_online_debug("AAPL", "2024-11-01", "2024-11-15"))
