#!/usr/bin/env python3
"""List supported AI model formats and examples."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import config

def list_models():
    print("🔍 Multi-Model AI Support (via LiteLLM)")
    print("=" * 60)
    
    print("\n📋 Common Model Formats (set in .env as AI_MODEL):\n")
    
    models = [
        ("Gemini", "gemini/gemini-1.5-flash", "GEMINI_API_KEY"),
        ("OpenAI", "openai/gpt-4o", "OPENAI_API_KEY"),
        ("Anthropic", "anthropic/claude-3-5-sonnet", "ANTHROPIC_API_KEY"),
        ("DeepSeek", "deepseek/deepseek-chat", "DEEPSEEK_API_KEY"),
        ("Groq", "groq/llama-3.1-70b-versatile", "GROQ_API_KEY"),
    ]
    
    for provider, model, key_name in models:
        key_val = config.get(key_name)
        status = "✅ Configured" if key_val and key_val != 'your-api-key-here' else "❌ Missing key"
        print(f"🔹 {provider:10} -> {model:30} [{status}: {key_name}]")

    print("\n" + "=" * 60)
    print("\n💡 To use a model, update .env:")
    print("   AI_MODEL=openai/gpt-4o")
    print("   OPENAI_API_KEY=sk-...")
    print("\n🔗 LiteLLM supports 100+ providers. Use provider/model-name format.")
    print()

if __name__ == "__main__":
    list_models()
