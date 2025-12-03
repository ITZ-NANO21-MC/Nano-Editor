# 🚀 Inicio Rápido - NanoEditor

## 📋 Pasos para Configurar Gemini AI

### 1️⃣ Obtener API Key

Ve a: **https://aistudio.google.com/app/apikey**

- Inicia sesión con tu cuenta de Google
- Click en "Create API Key"
- Copia la API key generada

### 2️⃣ Configurar API Key (Método Fácil)

```bash
cd /home/user/model-ia/Nano_Editor
./configure_apikey.sh
```

El script te pedirá la API key y la configurará automáticamente.

### 3️⃣ Ejecutar el Editor

```bash
./run.sh
```

---

## 🔧 Configuración Manual (Alternativa)

Si prefieres configurar manualmente:

### Opción A: Temporal (solo esta sesión)
```bash
export GEMINI_API_KEY="tu-api-key-aqui"
./run.sh
```

### Opción B: Permanente (todas las sesiones)
```bash
echo 'export GEMINI_API_KEY="tu-api-key-aqui"' >> ~/.bashrc
source ~/.bashrc
./run.sh
```

### Opción C: Archivo .env (en el directorio del proyecto)
```bash
cd /home/user/model-ia/Nano_Editor
echo 'GEMINI_API_KEY=tu-api-key-aqui' > .env
./run.sh
```

---

## ✅ Verificar Configuración

```bash
# Verificar que la API key está configurada
echo $GEMINI_API_KEY

# Debería mostrar tu API key
# Si está vacío, la configuración no funcionó
```

---

## 🎯 Usar AI Assistant

1. **Abre un archivo** en el editor
2. **Selecciona código** (o deja todo el archivo)
3. **Menú: AI Assistant** → Elige una opción:
   - Explain Code
   - Generate Code
   - Refactor Code
   - Fix Errors
   - Optimize Code
   - Generate Docstring
   - Translate Code

---

## ⚠️ Solución de Problemas

### Error: "GEMINI_API_KEY not configured"

**Solución:**
```bash
./configure_apikey.sh
```

### Error: "google-generativeai not installed"

**Solución:**
```bash
./env/bin/pip install google-generativeai
```

### La API key no se guarda

**Verifica:**
```bash
cat ~/.bashrc | grep GEMINI_API_KEY
```

**Si no aparece, agrégala manualmente:**
```bash
nano ~/.bashrc
# Agrega al final:
export GEMINI_API_KEY="tu-api-key"
# Guarda: Ctrl+O, Enter, Ctrl+X
source ~/.bashrc
```

---

## 📍 Ubicación de la API Key

La API key NO se guarda en ningún archivo del proyecto.
Se configura como **variable de entorno** en tu sistema:

- **Temporal:** Solo en la terminal actual
- **Permanente:** En `~/.bashrc` (se carga al abrir terminal)
- **Proyecto:** En `.env` (solo para este proyecto)

El código en `ai_assistant.py` lee la variable con:
```python
api_key = os.getenv('GEMINI_API_KEY')
```

---

## 🔒 Seguridad

- ✅ La API key NO se sube a Git (está en .gitignore)
- ✅ La API key NO está en el código fuente
- ✅ La API key es personal y privada
- ⚠️ NO compartas tu API key con nadie
- ⚠️ NO la subas a repositorios públicos

---

## 📚 Más Información

- [INSTALL.md](INSTALL.md) - Instalación completa
- [README_AI_ASSISTANT.md](README_AI_ASSISTANT.md) - Guía del AI Assistant
- [GEMINI_SETUP.md](GEMINI_SETUP.md) - Configuración avanzada
