#!/bin/bash
# Script de validación de correcciones

echo "🔍 Validando correcciones implementadas..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de tests
PASSED=0
FAILED=0

# Test 1: Verificar que no hay excepciones genéricas
echo "Test 1: Verificando excepciones genéricas..."
GENERIC_EXCEPT=$(grep -rn "except:" *.py 2>/dev/null | grep -v "env/" | grep -v "#" | wc -l)
if [ "$GENERIC_EXCEPT" -eq 0 ]; then
    echo -e "${GREEN}✅ PASS: No se encontraron excepciones genéricas${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: Se encontraron $GENERIC_EXCEPT excepciones genéricas${NC}"
    ((FAILED++))
fi
echo ""

# Test 2: Verificar imports al inicio
echo "Test 2: Verificando imports al inicio del archivo..."
IMPORTS_IN_FUNCTIONS=$(grep -A 5 "def " editor_view_v3.py | grep "from ai_menu import" | wc -l)
if [ "$IMPORTS_IN_FUNCTIONS" -eq 0 ]; then
    echo -e "${GREEN}✅ PASS: Todos los imports están al inicio${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: Se encontraron $IMPORTS_IN_FUNCTIONS imports dentro de funciones${NC}"
    ((FAILED++))
fi
echo ""

# Test 3: Verificar type hints
echo "Test 3: Verificando type hints..."
TYPE_HINTS=$(grep -c "def.*) ->" editor_view_v3.py file_tree_vscode.py tab_manager.py ai_assistant.py 2>/dev/null | awk -F: '{sum+=$2} END {print sum}')
if [ "$TYPE_HINTS" -gt 40 ]; then
    echo -e "${GREEN}✅ PASS: Se encontraron $TYPE_HINTS funciones con type hints${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARN: Solo se encontraron $TYPE_HINTS funciones con type hints (esperado: >40)${NC}"
    ((FAILED++))
fi
echo ""

# Test 4: Verificar imports de typing
echo "Test 4: Verificando imports de typing..."
TYPING_IMPORTS=$(grep -l "from typing import" editor_view_v3.py file_tree_vscode.py tab_manager.py ai_assistant.py ai_file_operations.py gemini_client.py 2>/dev/null | wc -l)
if [ "$TYPING_IMPORTS" -ge 5 ]; then
    echo -e "${GREEN}✅ PASS: Se encontraron imports de typing en $TYPING_IMPORTS archivos${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: Solo se encontraron imports de typing en $TYPING_IMPORTS archivos${NC}"
    ((FAILED++))
fi
echo ""

# Test 5: Verificar que shlex está importado
echo "Test 5: Verificando import de shlex..."
if grep -q "import shlex" editor_view_v3.py; then
    echo -e "${GREEN}✅ PASS: shlex está importado correctamente${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: shlex no está importado${NC}"
    ((FAILED++))
fi
echo ""

# Test 6: Verificar que shutil está importado
echo "Test 6: Verificando import de shutil..."
if grep -q "import shutil" editor_view_v3.py; then
    echo -e "${GREEN}✅ PASS: shutil está importado correctamente${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: shutil no está importado${NC}"
    ((FAILED++))
fi
echo ""

# Test 7: Verificar excepciones específicas
echo "Test 7: Verificando excepciones específicas..."
SPECIFIC_EXCEPT=$(grep -c "except (.*Error" editor_view_v3.py file_tree_vscode.py tab_manager.py 2>/dev/null | awk -F: '{sum+=$2} END {print sum}')
if [ "$SPECIFIC_EXCEPT" -ge 8 ]; then
    echo -e "${GREEN}✅ PASS: Se encontraron $SPECIFIC_EXCEPT excepciones específicas${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARN: Solo se encontraron $SPECIFIC_EXCEPT excepciones específicas${NC}"
    ((FAILED++))
fi
echo ""

# Resumen
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RESUMEN DE VALIDACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Tests pasados: $PASSED${NC}"
echo -e "${RED}❌ Tests fallidos: $FAILED${NC}"
TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))
echo "📈 Porcentaje de éxito: $PERCENTAGE%"
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}🎉 ¡Todas las correcciones fueron implementadas correctamente!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Algunas correcciones necesitan revisión${NC}"
    exit 1
fi
