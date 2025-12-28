#!/usr/bin/env python3
"""Test Gemini API configuration."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config

def test_api():
    print("🔍 Testing Gemini API Configuration")
    print("=" * 60)
    
    # Test 1: Check if .env exists
    env_file = Path(__file__).parent / '.env'
    print(f"\n1️⃣ Checking .env file...")
    if env_file.exists():
        print(f"   ✅ .env file found")
    else:
        print(f"   ❌ .env file not found")
        print(f"   Run: ./setup_env.sh")
        return False
    
    # Test 2: Check API key
    print(f"\n2️⃣ Checking API key...")
    api_key = config.get('GEMINI_API_KEY')
    if api_key and api_key != 'your-api-key-here':
        print(f"   ✅ API key configured")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print(f"   ❌ API key not configured")
        print(f"   Edit .env and set GEMINI_API_KEY")
        return False
    
    # Test 3: Check google-generativeai
    print(f"\n3️⃣ Checking google-generativeai...")
    try:
        import google.generativeai as genai
        print(f"   ✅ google-generativeai installed")
    except ImportError:
        print(f"   ❌ google-generativeai not installed")
        print(f"   Run: ./env/bin/pip install google-generativeai")
        return False
    
    # Test 4: Test API connection
    print(f"\n4️⃣ Testing API connection...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content("Say 'Hello' in one word")
        print(f"   ✅ API connection successful")
        print(f"   Response: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"   ❌ API connection failed")
        print(f"   Error: {str(e)}")
        if "API key" in str(e):
            print(f"   💡 Verify your API key is correct")
        elif "not found" in str(e):
            print(f"   💡 Try updating: pip install --upgrade google-generativeai")
        return False

if __name__ == "__main__":
    print("\n")
    success = test_api()
    print("\n" + "=" * 60)
    
    if success:
        print("✅ All tests passed!")
        print("\nYou can now use:")
        print("  - Gemini Panel (bottom of editor)")
        print("  - AI Assistant menu")
    else:
        print("❌ Some tests failed")
        print("\nFix the issues above and try again")
    
    print("=" * 60 + "\n")
    sys.exit(0 if success else 1)
