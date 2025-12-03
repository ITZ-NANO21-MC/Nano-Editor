# 🤖 AI Assistant Integration - Gemini Copilot

## Funcionalidades Implementadas

### 1. **Explicar Código** (AI Assistant → Explain Code)
- Selecciona código y obtén una explicación detallada
- Si no hay selección, explica todo el archivo
- Útil para entender código complejo o de terceros

### 2. **Generar Código** (AI Assistant → Generate Code...)
- Describe lo que necesitas en lenguaje natural
- Gemini genera el código en el lenguaje del archivo actual
- Puedes insertar directamente en el editor

### 3. **Refactorizar Código** (AI Assistant → Refactor Code)
- Selecciona código para mejorar
- Gemini sugiere mejoras de legibilidad y eficiencia
- Mantiene la funcionalidad original

### 4. **Corregir Errores** (AI Assistant → Fix Errors...)
- Selecciona código con errores
- Describe el error o pega el mensaje de error
- Gemini proporciona código corregido

### 5. **Optimizar Código** (AI Assistant → Optimize Code)
- Analiza código seleccionado
- Recibe sugerencias de optimización
- Mejora performance y uso de recursos

### 6. **Generar Documentación** (AI Assistant → Generate Docstring)
- Selecciona función o clase
- Genera docstring automáticamente
- Formato apropiado para el lenguaje

### 7. **Traducir Código** (AI Assistant → Translate Code...)
- Selecciona código en un lenguaje
- Especifica lenguaje destino
- Obtén traducción funcional

## Uso

### Ejemplo 1: Explicar Código
```python
# 1. Selecciona este código:
def fibonacci(n):
    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)

# 2. AI Assistant → Explain Code
# 3. Obtienes: "Esta función calcula el n-ésimo número de Fibonacci..."
```

### Ejemplo 2: Generar Código
```
1. AI Assistant → Generate Code...
2. Escribe: "función para validar email con regex"
3. Gemini genera:
   import re
   def validate_email(email):
       pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
       return re.match(pattern, email) is not None
4. Click "Insert" para agregar al editor
```

### Ejemplo 3: Refactorizar
```python
# Código original (seleccionado):
def calc(a, b, op):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        return a / b

# Después de refactorizar:
def calculate(num1, num2, operation):
    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y
    }
    return operations.get(operation, lambda x, y: None)(num1, num2)
```

## Atajos Recomendados (Futuro)

- `Ctrl+Shift+E` - Explicar código
- `Ctrl+Shift+G` - Generar código
- `Ctrl+Shift+R` - Refactorizar
- `Ctrl+Shift+F` - Corregir errores
- `Ctrl+Shift+O` - Optimizar
- `Ctrl+Shift+D` - Generar docstring

## Requisitos

1. **Gemini CLI instalado:**
   ```bash
   # Instalar Gemini CLI
   pip install google-generativeai
   ```

2. **Configurar API Key:**
   ```bash
   export GEMINI_API_KEY="tu-api-key"
   ```

## Arquitectura

```
┌─────────────────┐
│  editor_view.py │  ← Menú AI Assistant
└────────┬────────┘
         │
         ├─→ ┌──────────────┐
         │   │ ai_menu.py   │  ← Diálogos UI
         │   └──────────────┘
         │
         └─→ ┌─────────────────┐
             │ ai_assistant.py │  ← Lógica AI
             └────────┬────────┘
                      │
                      └─→ Gemini CLI
```

## Flujo de Trabajo

1. **Usuario selecciona código** (o no selecciona nada)
2. **Elige acción del menú** AI Assistant
3. **Sistema detecta lenguaje** automáticamente
4. **Envía prompt a Gemini** con contexto
5. **Muestra resultado** en diálogo
6. **Usuario puede:**
   - Copiar resultado
   - Insertar en editor
   - Cerrar diálogo

## Ventajas vs GitHub Copilot

✅ **Gratis** - No requiere suscripción
✅ **Local** - Usa tu propia API key
✅ **Personalizable** - Código abierto
✅ **Multilenguaje** - Soporta todos los lenguajes
✅ **Explicaciones** - No solo genera, también explica
✅ **Refactorización** - Mejora código existente

## Limitaciones Actuales

⚠️ Requiere Gemini CLI instalado
⚠️ Timeout de 30 segundos
⚠️ No hay autocompletado inline (como Copilot)
⚠️ Requiere selección manual de código

## Mejoras Futuras

- [ ] Autocompletado inline mientras escribes
- [ ] Sugerencias automáticas en tiempo real
- [ ] Cache de respuestas frecuentes
- [ ] Historial de interacciones
- [ ] Configuración de prompts personalizados
- [ ] Soporte para múltiples modelos AI
- [ ] Integración con GitHub Copilot API
- [ ] Análisis de código completo del proyecto
