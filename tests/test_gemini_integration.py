"""
Test script for Gemini integration in openai.py

This script tests the Gemini provider functionality without making actual API calls.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_gemini_import():
    """Test that Gemini can be imported"""
    print("Testing Gemini import...")
    try:
        import google.generativeai as genai
        print("✓ google-generativeai is installed")
        return True
    except ImportError:
        print("✗ google-generativeai is NOT installed")
        print("  Install with: pip install google-generativeai")
        return False

def test_config_switching():
    """Test configuration switching between OpenAI and Gemini"""
    print("\nTesting configuration switching...")
    from tradingagents.dataflows.config import get_config, set_config
    
    # Test default (OpenAI)
    config = get_config()
    assert config["llm_provider"] == "openai", "Default should be OpenAI"
    print("✓ Default provider is OpenAI")
    
    # Test switching to Gemini
    set_config({"llm_provider": "google"})
    config = get_config()
    assert config["llm_provider"] == "google", "Should switch to Google"
    print("✓ Successfully switched to Google/Gemini")
    
    # Reset to OpenAI
    set_config({"llm_provider": "openai"})
    print("✓ Successfully reset to OpenAI")
    
    return True

def test_function_signatures():
    """Test that the functions have correct signatures"""
    print("\nTesting function signatures...")
    from tradingagents.dataflows import openai as openai_module
    
    # Check functions exist
    assert hasattr(openai_module, 'get_stock_news_openai'), "get_stock_news_openai should exist"
    assert hasattr(openai_module, 'get_global_news_openai'), "get_global_news_openai should exist"
    assert hasattr(openai_module, 'get_fundamentals_openai'), "get_fundamentals_openai should exist"
    print("✓ All required functions exist")
    
    # Check helper function
    assert hasattr(openai_module, '_get_response_with_search'), "_get_response_with_search should exist"
    print("✓ Helper function _get_response_with_search exists")
    
    return True

def test_gemini_error_handling():
    """Test error handling when Gemini is not configured"""
    print("\nTesting error handling...")
    from tradingagents.dataflows.config import set_config
    from tradingagents.dataflows.openai import _get_response_with_search
    
    # Set to Gemini without API key
    set_config({"llm_provider": "google", "quick_think_llm": "gemini-2.0-flash-exp"})
    
    # Remove GOOGLE_API_KEY if it exists
    old_key = os.environ.pop("GOOGLE_API_KEY", None)
    
    try:
        from tradingagents.dataflows.config import get_config
        config = get_config()
        _get_response_with_search("test prompt", config)
        print("✗ Should have raised ValueError for missing API key")
        result = False
    except ValueError as e:
        if "GOOGLE_API_KEY" in str(e):
            print("✓ Correctly raises ValueError when GOOGLE_API_KEY is missing")
            result = True
        else:
            print(f"✗ Unexpected ValueError: {e}")
            result = False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        result = False
    finally:
        # Restore API key if it existed
        if old_key:
            os.environ["GOOGLE_API_KEY"] = old_key
        # Reset to OpenAI
        set_config({"llm_provider": "openai"})
    
    return result

if __name__ == "__main__":
    print("=" * 60)
    print("Gemini Integration Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_gemini_import()
    all_passed &= test_config_switching()
    all_passed &= test_function_signatures()
    all_passed &= test_gemini_error_handling()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
