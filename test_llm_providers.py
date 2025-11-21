"""
Test script to verify LLM provider configurations
This script tests both OpenAI and Google Gemini providers
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

def test_openai():
    """Test OpenAI provider"""
    print("\n" + "="*60)
    print("Testing OpenAI Provider")
    print("="*60)
    
    try:
        # Check API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found in .env file")
            return False
        
        print(f"✓ API Key found: {api_key[:20]}...")
        
        # Initialize model
        model = ChatOpenAI(
            model="gpt-4o-mini",
            base_url="https://api.openai.com/v1"
        )
        print("✓ Model initialized: gpt-4o-mini")
        
        # Test simple query
        response = model.invoke("Hello! Please respond with exactly: 'OpenAI is working!'")
        print(f"✓ Response received: {response.content}")
        
        print("\n✅ OpenAI provider is working correctly!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ OpenAI test failed: {e}\n")
        return False

def test_google_gemini():
    """Test Google Gemini provider"""
    print("\n" + "="*60)
    print("Testing Google Gemini Provider")
    print("="*60)
    
    try:
        # Check API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in .env file")
            return False
        
        print(f"✓ API Key found: {api_key[:20]}...")
        
        # Initialize model (using gemini-1.5-flash which has better free tier limits)
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            convert_system_message_to_human=True
        )
        print("✓ Model initialized: gemini-1.5-flash")
        
        # Test simple query
        response = model.invoke("Hello! Please respond with exactly: 'Google Gemini is working!'")
        print(f"✓ Response received: {response.content}")
        
        print("\n✅ Google Gemini provider is working correctly!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Google Gemini test failed: {e}\n")
        return False

def test_both_providers():
    """Test both providers and summarize results"""
    print("\n" + "="*60)
    print("LLM Provider Configuration Test")
    print("="*60)
    
    openai_works = test_openai()
    gemini_works = test_google_gemini()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    if openai_works:
        print("✅ OpenAI: Ready to use")
    else:
        print("❌ OpenAI: Not configured or not working")
    
    if gemini_works:
        print("✅ Google Gemini: Ready to use")
    else:
        print("❌ Google Gemini: Not configured or not working")
    
    print("\n" + "="*60)
    
    if openai_works and gemini_works:
        print("\n🎉 Both providers are working! You can use either one.")
        print("\nTo switch between providers:")
        print("1. Run: python -m cli.main")
        print("2. Select your preferred provider in the CLI")
        print("3. Or edit tradingagents/default_config.py")
    elif openai_works or gemini_works:
        print("\n⚠️  One provider is working. You can use that one.")
        print("\nTo configure the other provider:")
        print("1. Get an API key from the provider")
        print("2. Add it to your .env file")
        print("3. Run this test again")
    else:
        print("\n⚠️  No providers are working. Please configure at least one.")
        print("\nSetup steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your API key(s) to .env")
        print("3. Run this test again")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_both_providers()
