# 📦 Instalación de NanoEditor

## ⚠️ IMPORTANTE: Instalar Dependencias del Sistema

Antes de ejecutar el editor, necesitas instalar **tkinter** (dependencia del sistema):

```bash
cd /home/user/model-ia/Nano_Editor
./install_system_deps.sh
```

O manualmente según tu distribución:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-tk python3-dev
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-tkinter python3-devel
```

**Arch/Manjaro:**
```bash
sudo pacman -S tk
```

## ✅ Instalación Completada

El entorno virtual y las dependencias Python ya están instaladas.

## 🚀 Ejecutar el Editor

### Opción 1: Script de ejecución (Recomendado)
```bash
cd /home/user/model-ia/Nano_Editor
./run.sh
```

### Opción 2: Comando directo
```bash
cd /home/user/model-ia/Nano_Editor
./env/bin/python3 main.py
```

### Opción 3: Activar entorno y ejecutar
```bash
cd /home/user/model-ia/Nano_Editor
source env/bin/activate
python3 main.py
```

## 📋 Dependencias Instaladas

- ✅ **customtkinter** (5.2.2) - UI moderna
- ✅ **pygments** (2.19.2) - Resaltado de sintaxis
- ✅ **jedi** (0.19.2) - Autocompletado de código
- ✅ **darkdetect** (0.8.0) - Detección de tema del sistema
- ✅ **packaging** (25.0) - Gestión de versiones
- ✅ **parso** (0.8.5) - Parser de Python

## 🤖 Configurar AI Assistant (Opcional)

Para usar las funcionalidades de AI Assistant con Gemini:

### 1. Instalar Gemini CLI
```bash
pip install google-generativeai
```

### 2. Configurar API Key
```bash
export GEMINI_API_KEY="tu-api-key-aqui"
```

O crear archivo `.env`:
```bash
echo "GEMINI_API_KEY=tu-api-key-aqui" > .env
```

### 3. Obtener API Key
1. Ve a https://makersuite.google.com/app/apikey
2. Crea una nueva API key
3. Copia y pega en la configuración

## 🔧 Verificar Instalación

```bash
cd /home/user/model-ia/Nano_Editor
./env/bin/python3 -c "import tkinter; import customtkinter; import pygments; import jedi; print('✅ Todas las dependencias instaladas')"
```

## 📁 Estructura del Proyecto

```
Nano_Editor/
├── env/                    # Entorno virtual (creado)
├── main.py                 # Punto de entrada
├── editor_view.py          # Ventana principal
├── text_area.py            # Editor de código
├── ai_assistant.py         # Asistente AI
├── ai_menu.py              # Menús AI
├── requirements.txt        # Dependencias
├── run.sh                  # Script de ejecución
├── install_system_deps.sh  # Instalar tkinter
└── README.md               # Documentación
```

## ⚠️ Solución de Problemas

### Error: "No module named 'tkinter'"
```bash
# Ejecuta el script de instalación
./install_system_deps.sh

# O instala manualmente:
# Ubuntu/Debian:
sudo apt-get install python3-tk

# Fedora:
sudo dnf install python3-tkinter

# Arch:
sudo pacman -S tk
```

### Error: "No module named 'customtkinter'"
```bash
./env/bin/pip install -r requirements.txt
```

### Error: "Permission denied: ./run.sh"
```bash
chmod +x run.sh
```

### Error: "Display not found"
Si estás en SSH sin X11:
```bash
export DISPLAY=:0
```

## 🎯 Próximos Pasos

1. **Instalar tkinter:**
   ```bash
   ./install_system_deps.sh
   ```

2. **Ejecutar el editor:**
   ```bash
   ./run.sh
   ```

3. **Abrir un archivo:**
   - File → Open
   - O doble clic en el árbol de archivos

4. **Probar AI Assistant:**
   - Selecciona código
   - AI Assistant → Explain Code

5. **Cambiar tema:**
   - Theme → Dark/Light

## 📚 Documentación Adicional

- [README.md](README.md) - Documentación general
- [README_AI_ASSISTANT.md](README_AI_ASSISTANT.md) - Guía del AI Assistant
