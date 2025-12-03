#!/usr/bin/env python3
"""List available Gemini models."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import config

def list_models():
    print("🔍 Listing Available Gemini Models")
    print("=" * 60)
    
    api_key = config.get('GEMINI_API_KEY')
    if not api_key or api_key == 'your-api-key-here':
        print("❌ API key not configured")
        print("Run: ./setup_env.sh")
        return
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        print("\n📋 Available models:\n")
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ {model.name}")
                print(f"   Display: {model.display_name}")
                print(f"   Description: {model.description[:80]}...")
                print()
        
        print("=" * 60)
        print("\n💡 To use a model, update .env:")
        print("   AI_MODEL=models/gemini-1.5-flash-latest")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_models()
