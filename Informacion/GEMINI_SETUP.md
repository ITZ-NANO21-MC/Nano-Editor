# 🤖 Configuración de Gemini CLI

## ⚠️ Problema: "Request timed out after 30 seconds"

Este error ocurre cuando Gemini CLI tarda demasiado en responder. Causas comunes:

1. **Primera ejecución** - Gemini puede tardar más la primera vez
2. **Conexión lenta** - Internet lento o problemas de red
3. **API key no configurada** - Gemini no puede autenticar
4. **Gemini CLI no instalado** - El comando no existe

## 🔧 Soluciones

### 1. Verificar Instalación y Configuración

Ejecuta el script de diagnóstico:

```bash
cd /home/user/model-ia/Nano_Editor
./env/bin/python3 test_gemini.py
```

### 2. Instalar Gemini CLI

Si no está instalado:

```bash
# Opción 1: En el entorno virtual
./env/bin/pip install google-generativeai

# Opción 2: Global
pip install google-generativeai
```

### 3. Configurar API Key

**Obtener API Key:**
1. Ve a https://makersuite.google.com/app/apikey
2. Crea una nueva API key
3. Copia la key

**Configurar (Opción 1 - Temporal):**
```bash
export GEMINI_API_KEY="tu-api-key-aqui"
./run.sh
```

**Configurar (Opción 2 - Permanente):**
```bash
# Agregar a ~/.bashrc o ~/.zshrc
echo 'export GEMINI_API_KEY="tu-api-key-aqui"' >> ~/.bashrc
source ~/.bashrc
```

**Configurar (Opción 3 - Archivo .env):**
```bash
cd /home/user/model-ia/Nano_Editor
echo 'GEMINI_API_KEY=tu-api-key-aqui' > .env
```

### 4. Aumentar Timeout (Ya Aplicado)

El timeout se ha aumentado de 30 a 60 segundos en:
- `ai_assistant.py`
- `gemini_client.py`

Si aún es insuficiente, edita manualmente:

```python
# En ai_assistant.py y gemini_client.py
def __init__(self):
    self.timeout = 120  # Cambiar a 120 segundos (2 minutos)
```

### 5. Probar Gemini CLI Manualmente

```bash
# Test simple
gemini ask "Say hello"

# Si funciona, el problema es el timeout
# Si no funciona, hay problema de configuración
```

## 🔍 Diagnóstico de Errores

### Error: "gemini: command not found"
```bash
# Instalar Gemini CLI
pip install google-generativeai
```

### Error: "API key not configured"
```bash
# Configurar API key
export GEMINI_API_KEY="tu-api-key"
```

### Error: "Connection timeout"
```bash
# Verificar conexión a internet
ping google.com

# Verificar firewall
# Asegúrate de que no bloquee conexiones a Google AI
```

### Error: "Invalid API key"
```bash
# Verificar que la API key sea correcta
echo $GEMINI_API_KEY

# Regenerar API key en:
# https://makersuite.google.com/app/apikey
```

## 🎯 Alternativas si Gemini CLI no Funciona

### Opción 1: Usar API Directamente

Modifica `ai_assistant.py` para usar la API de Python directamente:

```python
import google.generativeai as genai

class AIAssistant:
    def __init__(self):
        genai.configure(api_key="tu-api-key")
        self.model = genai.GenerativeModel('gemini-pro')
    
    def explain_code(self, code, callback):
        response = self.model.generate_content(f"Explain: {code}")
        callback(response.text)
```

### Opción 2: Deshabilitar AI Assistant

Si no necesitas AI Assistant, simplemente no uses el menú "AI Assistant".
El resto del editor funciona normalmente.

### Opción 3: Usar Otro Modelo

Modifica `ai_assistant.py` para usar:
- OpenAI API
- Anthropic Claude
- Ollama (local)
- LM Studio (local)

## 📊 Tiempos Esperados

| Operación | Tiempo Normal | Timeout Actual |
|-----------|---------------|----------------|
| Explicar código | 5-15s | 60s |
| Generar código | 10-20s | 60s |
| Refactorizar | 10-25s | 60s |
| Primera ejecución | 20-40s | 60s |

## ✅ Verificación Final

Después de configurar, verifica:

```bash
# 1. Test de Gemini CLI
./env/bin/python3 test_gemini.py

# 2. Si pasa, ejecuta el editor
./run.sh

# 3. Prueba AI Assistant:
#    - Selecciona código
#    - AI Assistant → Explain Code
#    - Espera hasta 60 segundos
```

## 💡 Consejos

1. **Primera vez siempre es más lenta** - Espera pacientemente
2. **Código corto responde más rápido** - Selecciona 5-10 líneas
3. **Verifica tu internet** - Gemini requiere conexión estable
4. **Usa prompts simples** - Descripciones cortas funcionan mejor

## 🆘 Soporte

Si sigues teniendo problemas:

1. Ejecuta: `./env/bin/python3 test_gemini.py`
2. Copia el output completo
3. Verifica logs de error en la terminal
4. Revisa que tu API key sea válida
