import logging
import os
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from typing import List, Optional, Dict, Any
import xml.etree.ElementTree as ET

import requests


logger = logging.getLogger(__name__)

NEWS_FEED_URL = "https://coinjournal.net/news/feed/"
FMP_API_BASE_URL = "https://financialmodelingprep.com/api/v4/crypto_news"


def _strip_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    cleaned = unescape(text)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def fetch_fmp_crypto_news(
    symbol: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 0,
    limit: int = 50,
    api_key: Optional[str] = None,
    max_chars: int = 4000,
) -> str:
    """
    Fetch crypto news from Financial Modeling Prep API.
    
    Args:
        symbol: Crypto symbol (e.g., "BTCUSD", "ETHUSD"). Optional.
        from_date: Start date in YYYY-MM-DD format. Optional.
        to_date: End date in YYYY-MM-DD format. Optional.
        page: Page number for pagination (default: 0).
        limit: Maximum number of articles to return (default: 50, max: 1000).
        api_key: FMP API key. If not provided, will try to get from FMP_API_KEY environment variable.
        max_chars: Maximum characters to return in formatted output (default: 4000).
    
    Returns:
        Formatted news entries as a string.
        
    Example:
        # Get latest Bitcoin news
        news = fetch_fmp_crypto_news(symbol="BTCUSD", limit=10)
        
        # Get news for specific date range
        news = fetch_fmp_crypto_news(
            symbol="ETHUSD",
            from_date="2024-01-01",
            to_date="2024-03-01",
            limit=20
        )
    """
    try:
        # Get API key from parameter or environment
        if api_key is None:
            # api_key = os.getenv("FMP_API_KEY")
            api_key = "GqAgzmUoPRckTa5c6Zp4e5HIEdttrPFT"
            if not api_key:
                logger.warning("FMP_API_KEY not provided and not found in environment variables")
                return ""
        
        # Build query parameters
        params: Dict[str, Any] = {
            "page": page,
            "limit": min(limit, 1000),  # API max is 1000
            "apikey": api_key,
        }
        
        if symbol:
            params["symbol"] = symbol.upper()
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        
        # Make API request
        response = requests.get(FMP_API_BASE_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.warning("Failed to fetch FMP crypto news: status %s", response.status_code)
            return ""
        
        articles = response.json()
        
        if not articles or not isinstance(articles, list):
            logger.info("No crypto news articles found")
            return ""
        
        # Format articles
        entries: List[str] = []
        
        for article in articles:
            published_date = article.get("publishedDate", "")
            title = article.get("title", "")
            text = article.get("text", "")
            url = article.get("url", "")
            site = article.get("site", "")
            tickers = article.get("tickers", [])
            
            # Format timestamp
            formatted_time = published_date
            if published_date:
                try:
                    # Parse ISO format: 2022-10-05T15:57:27.000Z
                    parsed = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
                    formatted_time = parsed.strftime("%Y-%m-%d %H:%M:%SZ")
                except Exception:
                    formatted_time = published_date
            
            # Build entry text
            parts = []
            if formatted_time:
                parts.append(formatted_time)
            if title:
                parts.append(title)
            
            entry_text = " | ".join(parts)
            
            # Add summary (first 200 chars of text)
            if text:
                summary = text[:200].strip()
                if len(text) > 200:
                    summary += "..."
                entry_text = f"{entry_text}: {summary}" if entry_text else summary
            
            # Add source and tickers
            metadata_parts = []
            if site:
                metadata_parts.append(f"Source: {site}")
            if tickers:
                metadata_parts.append(f"Tickers: {', '.join(tickers)}")
            if url:
                metadata_parts.append(f"URL: {url}")
            
            if metadata_parts:
                entry_text += f" [{'; '.join(metadata_parts)}]"
            
            entry_text = entry_text.strip()
            if not entry_text:
                continue
            
            # Check character limit
            existing_text = "\n".join(entries)
            candidate_text = f"{existing_text}\n{entry_text}" if existing_text else entry_text
            
            if len(candidate_text) > max_chars:
                remaining = max_chars - len(existing_text)
                if existing_text:
                    remaining -= 1
                if remaining <= 0:
                    break
                truncated = entry_text[:remaining].rstrip()
                if truncated:
                    if len(truncated) < len(entry_text):
                        truncated = truncated.rstrip(" .,;:-") + "..."
                    entries.append(truncated)
                break
            
            entries.append(entry_text)
        
        return "\n".join(entries)
        
    except Exception as err:
        logger.warning("Failed to fetch FMP crypto news: %s", err)
        return ""


def fetch_latest_news(max_chars: int = 4000, coin: Optional[str] = None) -> str:
    """
    Fetch latest cryptocurrency news from coinjournal.net RSS feed.
    
    Args:
        max_chars: Maximum characters to return (default: 4000)
        coin: Optional coin symbol to filter news (e.g., "BTC", "ETH", "XRP").
              If provided, only news containing the coin name will be included.
    
    Returns:
        Formatted news entries as a string
    """
    try:
        response = requests.get(NEWS_FEED_URL, timeout=10)
        if response.status_code != 200:
            logger.warning("Failed to fetch news feed: status %s", response.status_code)
            return ""

        root = ET.fromstring(response.content)
        channel = root.find("channel")
        if channel is None:
            return ""

        entries: List[str] = []
        
        # Prepare coin filter keywords if specified
        coin_keywords = []
        if coin:
            coin_upper = coin.upper()
            # Handle common coin symbols and their full names
            coin_map = {
                "BTC": ["BTC", "BITCOIN"],
                "ETH": ["ETH", "ETHEREUM"],
                "XRP": ["XRP", "RIPPLE"],
                "ADA": ["ADA", "CARDANO"],
                "SOL": ["SOL", "SOLANA"],
                "DOGE": ["DOGE", "DOGECOIN"],
                "MATIC": ["MATIC", "POLYGON"],
                "DOT": ["DOT", "POLKADOT"],
                "AVAX": ["AVAX", "AVALANCHE"],
                "LINK": ["LINK", "CHAINLINK"],
            }
            
            # Get keywords for known coins, otherwise use the coin symbol itself
            coin_keywords = coin_map.get(coin_upper, [coin_upper])
            # Also add the coin symbol without suffix (e.g., "XRP" from "XRP-USDT")
            if "-" in coin:
                base_symbol = coin.split("-")[0].upper()
                if base_symbol not in coin_keywords:
                    coin_keywords.append(base_symbol)

        for item in channel.findall("item"):
            title = _strip_html_tags(item.findtext("title") or "")
            pub_date_raw = (item.findtext("pubDate") or "").strip()
            summary_raw = item.findtext("description") or ""

            summary = _strip_html_tags(summary_raw)
            summary = re.sub(r"The post .*? appeared first on .*", "", summary, flags=re.IGNORECASE).strip()
            
            # Filter by coin if specified
            if coin_keywords:
                combined_text = f"{title} {summary}".upper()
                if not any(keyword in combined_text for keyword in coin_keywords):
                    continue

            formatted_time = pub_date_raw
            if pub_date_raw:
                try:
                    parsed = parsedate_to_datetime(pub_date_raw)
                    if parsed is not None:
                        if parsed.tzinfo is None:
                            parsed = parsed.replace(tzinfo=timezone.utc)
                        else:
                            parsed = parsed.astimezone(timezone.utc)
                        formatted_time = parsed.strftime("%Y-%m-%d %H:%M:%SZ")
                except Exception:
                    formatted_time = pub_date_raw

            parts = []
            if formatted_time:
                parts.append(formatted_time)
            if title:
                parts.append(title)

            entry_text = " | ".join(parts)
            if summary:
                entry_text = f"{entry_text}: {summary}" if entry_text else summary

            entry_text = entry_text.strip()
            if not entry_text:
                continue

            existing_text = "\n".join(entries)
            candidate_text = f"{existing_text}\n{entry_text}" if existing_text else entry_text
            if len(candidate_text) > max_chars:
                remaining = max_chars - len(existing_text)
                if existing_text:
                    remaining -= 1
                if remaining <= 0:
                    break
                truncated = entry_text[:remaining].rstrip()
                if truncated:
                    if len(truncated) < len(entry_text):
                        truncated = truncated.rstrip(" .,;:-") + "..."
                    entries.append(truncated)
                break

            entries.append(entry_text)

        return "\n".join(entries)

    except Exception as err:
        logger.warning("Failed to process news feed: %s", err)
        return ""


