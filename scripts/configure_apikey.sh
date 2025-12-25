#!/bin/bash
# Script interactivo para configurar Gemini API Key

echo "🔑 Configuración de Gemini API Key"
echo "===================================="
echo ""
echo "1. Obtén tu API key en:"
echo "   https://aistudio.google.com/app/apikey"
echo ""
read -p "2. Pega tu API key aquí: " API_KEY

if [ -z "$API_KEY" ]; then
    echo "❌ No ingresaste ninguna API key"
    exit 1
fi

echo ""
echo "📝 Configurando API key..."

# Agregar a ~/.bashrc
if ! grep -q "GEMINI_API_KEY" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Gemini API Key para NanoEditor" >> ~/.bashrc
    echo "export GEMINI_API_KEY=\"$API_KEY\"" >> ~/.bashrc
    echo "✅ API key agregada a ~/.bashrc"
else
    echo "⚠️  GEMINI_API_KEY ya existe en ~/.bashrc"
    read -p "¿Deseas actualizarla? (s/n): " UPDATE
    if [ "$UPDATE" = "s" ] || [ "$UPDATE" = "S" ]; then
        sed -i "/export GEMINI_API_KEY=/c\export GEMINI_API_KEY=\"$API_KEY\"" ~/.bashrc
        echo "✅ API key actualizada en ~/.bashrc"
    fi
fi

# Exportar para la sesión actual
export GEMINI_API_KEY="$API_KEY"

echo ""
echo "✅ Configuración completada"
echo ""
echo "Para aplicar en esta terminal:"
echo "  source ~/.bashrc"
echo ""
echo "O simplemente ejecuta el editor:"
echo "  ./run.sh"
echo ""
