#!/usr/bin/env python3
"""Check available Gemini models using ListModels API."""

import sys
import os

# Get API key from command line or environment
if len(sys.argv) > 1:
    api_key = sys.argv[1]
else:
    api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("Usage: python check_models.py YOUR_API_KEY")
    print("Or set GEMINI_API_KEY environment variable")
    sys.exit(1)

try:
    import google.generativeai as genai
    
    print("🔍 Checking Available Gemini Models")
    print("=" * 70)
    print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    genai.configure(api_key=api_key)
    
    print("📋 Models that support generateContent:\n")
    
    available_models = []
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            available_models.append(model.name)
            print(f"✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description[:100]}...")
            print()
    
    print("=" * 70)
    print(f"\n✅ Found {len(available_models)} available models")
    
    if available_models:
        print("\n💡 Recommended for .env:")
        print(f"   AI_MODEL={available_models[0]}")
        
        print("\n📝 All available models:")
        for model in available_models:
            print(f"   - {model}")
    
    print("\n" + "=" * 70)
    
except ImportError:
    print("❌ google-generativeai not installed")
    print("Install: pip install google-generativeai")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
