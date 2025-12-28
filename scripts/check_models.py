#!/usr/bin/env python3
"""Check available Gemini models using ListModels API."""

import sys
import os


# Add project root to sys.path to import config
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from config import config

# Get API key from command line or config
if len(sys.argv) > 1:
    api_key = sys.argv[1]
else:
    api_key = config.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found.")
    print("Usage: python check_models.py YOUR_API_KEY")
    print("Or ensure .env file exists in project root with GEMINI_API_KEY defined")
    sys.exit(1)

try:
    from google import genai
    
    print("🔍 Checking Available Gemini Models")
    print("=" * 70)
    print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    client = genai.Client(api_key=api_key)
    
    print("📋 Models that support generateContent:\n")
    
    available_models = []
    # List models using the new API
    for model in client.models.list():
        # Check if model supports generation (filtering might differ in new SDK, keeping simple for now)
        # The new SDK model objects might have different attributes.
        # Usually it returns Model objects.
        
        # New SDK filter approach or just check name
        if 'gemini' in model.name:
            available_models.append(model.name)
            print(f"✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            # Description might be missing or named differently
            desc = getattr(model, 'description', '')
            print(f"   Description: {desc[:100]}...")
            print()
    
    print("=" * 70)
    print(f"\n✅ Found {len(available_models)} available models")
    
    if available_models:
        print("\n💡 Recommended for .env:")
        # Try to find a flash model for recommendation
        rec_model = next((m for m in available_models if 'flash' in m), available_models[0])
        print(f"   AI_MODEL={rec_model}")
        
        print("\n📝 All available models:")
        for model in available_models:
            print(f"   - {model}")
    
    print("\n" + "=" * 70)
    
except ImportError:
    print("❌ google-genai not installed")
    print("Install: pip install google-genai")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
