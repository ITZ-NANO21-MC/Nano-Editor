#!/bin/bash
# Script para configurar archivo .env

echo "🔧 Configuración de NanoEditor"
echo "==============================="
echo ""

ENV_FILE=".env"

# Verificar si .env ya existe
if [ -f "$ENV_FILE" ]; then
    echo "⚠️  El archivo .env ya existe"
    read -p "¿Deseas sobrescribirlo? (s/n): " OVERWRITE
    if [ "$OVERWRITE" != "s" ] && [ "$OVERWRITE" != "S" ]; then
        echo "❌ Configuración cancelada"
        exit 0
    fi
fi

echo "📝 Configurando variables de entorno..."
echo ""

# Solicitar API Key
echo "1️⃣  Gemini API Key"
echo "   Obtén tu API key en: https://aistudio.google.com/app/apikey"
read -p "   Ingresa tu API key: " API_KEY

if [ -z "$API_KEY" ]; then
    echo "❌ API key es requerida"
    exit 1
fi

# Solicitar configuraciones opcionales
echo ""
echo "2️⃣  Configuración del Editor (opcional, presiona Enter para usar valores por defecto)"
read -p "   Tema (dark/light) [dark]: " THEME
THEME=${THEME:-dark}

read -p "   Tamaño de fuente [14]: " FONT_SIZE
FONT_SIZE=${FONT_SIZE:-14}

read -p "   Timeout de AI en segundos [60]: " AI_TIMEOUT
AI_TIMEOUT=${AI_TIMEOUT:-60}

# Crear archivo .env
cat > "$ENV_FILE" << EOF
# Configuración de NanoEditor
# Generado el $(date)

# Gemini API Key (Requerido para AI Assistant)
GEMINI_API_KEY=$API_KEY

# Configuración del Editor
EDITOR_THEME=$THEME
EDITOR_FONT_SIZE=$FONT_SIZE
EDITOR_FONT_FAMILY=monospace

# Configuración de AI
AI_TIMEOUT=$AI_TIMEOUT
AI_MAX_TOKENS=2048
AI_MODEL=gemini-pro

# Configuración de Autocompletado
AUTOCOMPLETE_ENABLED=true
AUTOCOMPLETE_DELAY=500

# Configuración de Resaltado de Sintaxis
SYNTAX_HIGHLIGHT_ENABLED=true
SYNTAX_HIGHLIGHT_STYLE=monokai
EOF

echo ""
echo "✅ Archivo .env creado exitosamente"
echo ""
echo "📄 Contenido de .env:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$ENV_FILE" | grep -v "GEMINI_API_KEY"
echo "GEMINI_API_KEY=*********************"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Ahora puedes ejecutar el editor:"
echo "   ./run.sh"
echo ""
echo "💡 Para editar la configuración:"
echo "   nano .env"
echo ""
