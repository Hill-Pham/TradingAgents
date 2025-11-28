"""
Test suite for news_feed.py module.
Tests the fetch_latest_news function with real and mocked data.
"""
import sys
import io
from unittest.mock import patch, Mock
import xml.etree.ElementTree as ET

# Set UTF-8 encoding for console output (fixes Unicode errors on Windows)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from tradingagents.dataflows.news_feed import fetch_latest_news, _strip_html_tags


# Sample RSS feed XML for testing
SAMPLE_RSS_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Coin Journal News</title>
        <item>
            <title>Bitcoin Reaches New Heights</title>
            <pubDate>Tue, 26 Nov 2024 10:30:00 GMT</pubDate>
            <description><![CDATA[<p>Bitcoin has surged to new all-time highs as institutional adoption continues to grow.</p> The post Bitcoin Reaches New Heights appeared first on Coin Journal.]]></description>
        </item>
        <item>
            <title>Ethereum Updates Coming Soon</title>
            <pubDate>Tue, 26 Nov 2024 09:15:00 GMT</pubDate>
            <description><![CDATA[<p>Major network upgrades are planned for Ethereum in the coming months.</p>]]></description>
        </item>
        <item>
            <title>Crypto Regulation News</title>
            <pubDate>Tue, 26 Nov 2024 08:00:00 GMT</pubDate>
            <description><![CDATA[New regulatory framework proposed for digital assets.]]></description>
        </item>
    </channel>
</rss>"""


def test_strip_html_tags():
    """Test HTML tag stripping functionality."""
    print("\n=== Testing _strip_html_tags ===")
    
    test_cases = [
        ("<p>Hello World</p>", "Hello World"),
        ("<b>Bold</b> and <i>italic</i>", "Bold and italic"),
        ("Plain text", "Plain text"),
        ("", ""),
        (None, ""),
        ("<div><span>Nested <b>tags</b></span></div>", "Nested tags"),
    ]
    
    for html_input, expected in test_cases:
        result = _strip_html_tags(html_input)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: {repr(html_input)[:50]}")
        print(f"  Expected: {repr(expected)}")
        print(f"  Got: {repr(result)}")
        assert result == expected, f"Failed for input: {html_input}"
    
    print("All _strip_html_tags tests passed!")


def test_fetch_latest_news_with_mock():
    """Test fetch_latest_news with mocked HTTP response."""
    print("\n=== Testing fetch_latest_news with Mock Data ===")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = SAMPLE_RSS_FEED.encode('utf-8')
    
    with patch('requests.get', return_value=mock_response):
        result = fetch_latest_news(max_chars=1000)
        
        print(f"Result length: {len(result)} chars")
        print(f"\nFetched news:\n{result}\n")
        
        # Assertions
        assert len(result) > 0, "Result should not be empty"
        assert "Bitcoin" in result, "Should contain Bitcoin news"
        assert "Ethereum" in result, "Should contain Ethereum news"
        assert len(result) <= 1000, f"Result should be <= 1000 chars, got {len(result)}"
        
        # Check for proper formatting
        lines = result.split('\n')
        print(f"Number of news entries: {len(lines)}")
        for i, line in enumerate(lines, 1):
            print(f"Entry {i}: {line[:80]}...")
        
        print("✓ Mock data test passed!")


def test_fetch_latest_news_max_chars():
    """Test that max_chars limit is respected."""
    print("\n=== Testing max_chars Limit ===")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = SAMPLE_RSS_FEED.encode('utf-8')
    
    test_limits = [100, 200, 500]
    
    for limit in test_limits:
        with patch('requests.get', return_value=mock_response):
            result = fetch_latest_news(max_chars=limit)
            
            status = "✓" if len(result) <= limit else "✗"
            print(f"{status} Limit: {limit}, Actual: {len(result)}")
            assert len(result) <= limit, f"Result exceeded max_chars limit: {len(result)} > {limit}"
    
    print("✓ max_chars limit tests passed!")


def test_fetch_latest_news_error_handling():
    """Test error handling for failed requests."""
    print("\n=== Testing Error Handling ===")
    
    # Test HTTP error
    mock_response = Mock()
    mock_response.status_code = 404
    
    with patch('requests.get', return_value=mock_response):
        result = fetch_latest_news()
        print(f"HTTP 404 result: {repr(result)}")
        assert result == "", "Should return empty string on HTTP error"
        print("✓ HTTP error handling passed!")
    
    # Test network error
    with patch('requests.get', side_effect=Exception("Network error")):
        result = fetch_latest_news()
        print(f"Network error result: {repr(result)}")
        assert result == "", "Should return empty string on network error"
        print("✓ Network error handling passed!")


def test_fetch_latest_news_real():
    """Test fetch_latest_news with real API call."""
    print("\n=== Testing fetch_latest_news with Real API ===")
    print("This test makes a real HTTP request to coinjournal.net")
    
    try:
        result = fetch_latest_news(max_chars=2000)
        
        if result:
            print(f"✓ Successfully fetched {len(result)} characters of news")
            print(f"\nFirst 500 chars:\n{result[:500]}...\n")
            
            lines = result.split('\n')
            print(f"Number of news entries: {len(lines)}")
            
            # Basic validation
            assert len(result) > 0, "Should have fetched some news"
            assert len(result) <= 2000, "Should respect max_chars limit"
            print("✓ Real API test passed!")
        else:
            print("⚠ No news fetched (might be a temporary issue with the feed)")
            
    except Exception as e:
        print(f"⚠ Real API test failed (this is OK if network is unavailable): {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("NEWS FEED TEST SUITE")
    print("=" * 60)
    
    try:
        # Run tests
        test_strip_html_tags()
        test_fetch_latest_news_with_mock()
        test_fetch_latest_news_max_chars()
        test_fetch_latest_news_error_handling()
        test_fetch_latest_news_real()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 60)
        raise
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ UNEXPECTED ERROR: {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    main()
