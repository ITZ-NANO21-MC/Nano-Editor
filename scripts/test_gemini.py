#!/usr/bin/env python3
"""Script para probar la conexión con Gemini CLI."""

import subprocess
import sys

def test_gemini():
    print("🔍 Probando conexión con Gemini CLI...\n")
    
    # Test 1: Verificar si gemini está instalado
    print("1️⃣ Verificando instalación de Gemini CLI...")
    try:
        result = subprocess.run(
            ['which', 'gemini'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"   ✅ Gemini CLI encontrado en: {result.stdout.strip()}")
        else:
            print("   ❌ Gemini CLI no encontrado")
            print("\n   Instala con: pip install google-generativeai")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Probar comando simple
    print("\n2️⃣ Probando comando simple...")
    try:
        result = subprocess.run(
            ['gemini', 'ask', 'Say hello in one word'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"   ✅ Respuesta: {result.stdout.strip()[:50]}...")
            return True
        else:
            print(f"   ❌ Error: {result.stderr}")
            if "API key" in result.stderr or "authentication" in result.stderr.lower():
                print("\n   💡 Configura tu API key:")
                print("      export GEMINI_API_KEY='tu-api-key'")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️ Timeout - Gemini tardó más de 30 segundos")
        print("   💡 Esto puede ser normal en la primera ejecución")
        print("   💡 Intenta aumentar el timeout en ai_assistant.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST DE GEMINI CLI")
    print("=" * 60 + "\n")
    
    success = test_gemini()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Gemini CLI está funcionando correctamente")
        print("\nPuedes usar el AI Assistant en NanoEditor")
    else:
        print("❌ Hay problemas con Gemini CLI")
        print("\nPasos para solucionar:")
        print("1. Instala: pip install google-generativeai")
        print("2. Configura API key: export GEMINI_API_KEY='tu-key'")
        print("3. Obtén API key en: https://makersuite.google.com/app/apikey")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
