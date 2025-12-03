# 📝 Configuración con Archivo .env

## 🎯 Ventajas del Archivo .env

- ✅ **Centralizado** - Todas las configuraciones en un solo lugar
- ✅ **Seguro** - No se sube a Git (está en .gitignore)
- ✅ **Fácil** - Editar con cualquier editor de texto
- ✅ **Portable** - Copiar entre máquinas fácilmente
- ✅ **Versionable** - .env.example como plantilla

## 🚀 Configuración Rápida

### Método 1: Script Interactivo (Recomendado)

```bash
cd /home/user/model-ia/Nano_Editor
./setup_env.sh
```

El script te guiará paso a paso.

### Método 2: Copiar y Editar

```bash
cd /home/user/model-ia/Nano_Editor
cp .env.example .env
nano .env
```

Edita el archivo y cambia `your-api-key-here` por tu API key real.

### Método 3: Crear Manualmente

```bash
cd /home/user/model-ia/Nano_Editor
cat > .env << 'EOF'
GEMINI_API_KEY=tu-api-key-aqui
EDITOR_THEME=dark
EDITOR_FONT_SIZE=14
AI_TIMEOUT=60
AI_MODEL=gemini-pro
EOF
```

## 📋 Variables Disponibles

### Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key de Gemini | `AIza...` |

### Opcionales - Editor

| Variable | Descripción | Default | Valores |
|----------|-------------|---------|---------|
| `EDITOR_THEME` | Tema del editor | `dark` | `dark`, `light` |
| `EDITOR_FONT_SIZE` | Tamaño de fuente | `14` | `10-24` |
| `EDITOR_FONT_FAMILY` | Familia de fuente | `monospace` | Cualquier fuente |

### Opcionales - AI Assistant

| Variable | Descripción | Default | Valores |
|----------|-------------|---------|---------|
| `AI_TIMEOUT` | Timeout en segundos | `60` | `30-300` |
| `AI_MAX_TOKENS` | Máximo de tokens | `2048` | `512-8192` |
| `AI_MODEL` | Modelo de Gemini | `gemini-pro` | `gemini-pro`, `gemini-pro-vision` |

### Opcionales - Autocompletado

| Variable | Descripción | Default | Valores |
|----------|-------------|---------|---------|
| `AUTOCOMPLETE_ENABLED` | Activar autocompletado | `true` | `true`, `false` |
| `AUTOCOMPLETE_DELAY` | Delay en ms | `500` | `100-2000` |

### Opcionales - Sintaxis

| Variable | Descripción | Default | Valores |
|----------|-------------|---------|---------|
| `SYNTAX_HIGHLIGHT_ENABLED` | Activar resaltado | `true` | `true`, `false` |
| `SYNTAX_HIGHLIGHT_STYLE` | Estilo de color | `monokai` | Ver estilos Pygments |

## 📄 Ejemplo de .env Completo

```env
# Gemini API
GEMINI_API_KEY=AIzaSyD...your-key-here

# Editor
EDITOR_THEME=dark
EDITOR_FONT_SIZE=14
EDITOR_FONT_FAMILY=monospace

# AI Assistant
AI_TIMEOUT=60
AI_MAX_TOKENS=2048
AI_MODEL=gemini-pro

# Autocompletado
AUTOCOMPLETE_ENABLED=true
AUTOCOMPLETE_DELAY=500

# Resaltado de Sintaxis
SYNTAX_HIGHLIGHT_ENABLED=true
SYNTAX_HIGHLIGHT_STYLE=monokai
```

## 🔧 Editar Configuración

```bash
# Con nano
nano .env

# Con vim
vim .env

# Con cualquier editor
gedit .env
code .env
```

## ✅ Verificar Configuración

```bash
# Ver contenido (oculta API key)
cat .env | grep -v "GEMINI_API_KEY"

# Verificar que se carga correctamente
./env/bin/python3 -c "from config import config; print('API Key configurada:', bool(config.get('GEMINI_API_KEY')))"
```

## 🔒 Seguridad

### ✅ Buenas Prácticas

- ✅ `.env` está en `.gitignore` (no se sube a Git)
- ✅ Usa `.env.example` como plantilla sin datos reales
- ✅ No compartas tu archivo `.env`
- ✅ Regenera API key si se expone

### ❌ NO Hacer

- ❌ NO subas `.env` a Git
- ❌ NO compartas tu API key
- ❌ NO uses la misma API key en múltiples proyectos públicos
- ❌ NO incluyas `.env` en backups públicos

## 🔄 Migrar de Variables de Entorno

Si ya tienes configurado con `export`:

```bash
# Crear .env desde variables actuales
cat > .env << EOF
GEMINI_API_KEY=$GEMINI_API_KEY
EDITOR_THEME=dark
AI_TIMEOUT=60
EOF

# Ahora puedes eliminar de ~/.bashrc
nano ~/.bashrc
# Elimina la línea: export GEMINI_API_KEY=...
```

## 📦 Compartir Configuración

Para compartir tu configuración (sin API key):

```bash
# Crear plantilla desde tu .env
cp .env .env.example
nano .env.example
# Reemplaza tu API key con: your-api-key-here
```

## 🆘 Solución de Problemas

### Error: "GEMINI_API_KEY not configured"

```bash
# Verificar que .env existe
ls -la .env

# Verificar contenido
cat .env | grep GEMINI_API_KEY

# Si no existe, crear:
./setup_env.sh
```

### .env no se carga

```bash
# Verificar que config.py existe
ls -la config.py

# Probar carga manual
./env/bin/python3 -c "from config import config; print(config.config)"
```

### Cambios no se aplican

```bash
# Reiniciar el editor
# Los cambios en .env se cargan al iniciar
./run.sh
```

## 📚 Más Información

- [QUICK_START.md](QUICK_START.md) - Inicio rápido
- [INSTALL.md](INSTALL.md) - Instalación completa
- [README_AI_ASSISTANT.md](README_AI_ASSISTANT.md) - Guía del AI Assistant
