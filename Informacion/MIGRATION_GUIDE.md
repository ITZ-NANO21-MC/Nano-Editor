# 🔄 Guía de Migración - NanoEditor v3.0

## 📋 Cambios Realizados

### ✅ Archivos Movidos a `legacy/`

Las versiones antiguas han sido archivadas:

```
legacy/
├── editor_view.py      (v1.0)
├── main.py             (v1.0)
├── file_tree.py        (v1.0)
├── run.sh              (v1.0)
├── editor_view_v2.py   (v2.0)
├── main_v2.py          (v2.0)
├── run_v2.sh           (v2.0)
└── README.md
```

### ✅ Nuevos Archivos Principales

```
main.py          → Apunta a editor_view_v3.py
run.sh           → Ejecuta v3.0 (antes ejecutaba v1.0)
run_v3.sh        → Ejecuta v3.0 (mantiene compatibilidad)
```

## 🚀 Cómo Ejecutar

### Versión Actual (v3.0) - RECOMENDADO

```bash
# Opción 1: Script principal
./run.sh

# Opción 2: Script específico v3
./run_v3.sh

# Opción 3: Directamente
python3 main.py

# Opción 4: Módulo específico
python3 editor_view_v3.py
```

### Versiones Antiguas (Legacy)

```bash
# Versión 1.0
cd legacy
./run.sh

# Versión 2.0
cd legacy
./run_v2.sh
```

## 🆕 Novedades en v3.0

### Interfaz
- ✨ Barra lateral estilo VS Code con iconos
- ✨ Explorador de archivos con iconos por tipo
- ✨ Menú superior moderno horizontal
- ✨ Paneles intercambiables (Explorer, Search, Source Control, Run, AI, Extensions, Settings)

### Atajos de Teclado Nuevos
- `Ctrl+Shift+E` - Explorer
- `Ctrl+Shift+F` - Search
- `Ctrl+Shift+G` - Source Control
- `Ctrl+Shift+D` - Run & Debug
- `Ctrl+Shift+A` - AI Assistant
- `Ctrl+Shift+X` - Extensions
- `Ctrl+,` - Settings

### AI Assistant
- ✨ Panel dedicado en barra lateral
- ✨ Organizado por categorías (Analysis, Generation, Modification, File Operations)
- ✨ Botones de acción rápida
- ✨ Todas las funciones accesibles desde menú y panel

## 🔧 Compatibilidad

### Archivos de Configuración
- `.env` - Compatible con todas las versiones
- `config.py` - Sin cambios

### Módulos Compartidos
Estos módulos funcionan en todas las versiones:
- `text_area.py`
- `line_numbers.py`
- `syntax_highlighter.py`
- `completion_popup.py`
- `terminal_panel.py`
- `gemini_panel.py`
- `gemini_client.py`
- `ai_assistant.py`
- `status_bar.py`
- `find_replace.py`
- `project_search.py`
- `goto_definition.py`

## ⚠️ Cambios Importantes

### Reemplazos de Módulos

| Antiguo | Nuevo | Razón |
|---------|-------|-------|
| `file_tree.py` | `file_tree_vscode.py` | Interfaz VS Code con iconos |
| `editor_view.py` | `editor_view_v3.py` | Barra lateral y paneles |
| `main.py` (v1.0) | `main.py` (v3.0) | Entry point actualizado |

### Estructura de Carpetas

```
Nano_Editor/
├── legacy/              ← Versiones antiguas
├── main.py              ← v3.0 (actualizado)
├── run.sh               ← v3.0 (actualizado)
├── editor_view_v3.py    ← GUI principal
├── file_tree_vscode.py  ← Explorador VS Code
├── sidebar_vscode.py    ← Barra lateral
├── ai_panel_vscode.py   ← Panel AI
└── [otros módulos...]
```

## 🐛 Solución de Problemas

### Error: "Module not found"
```bash
# Asegúrate de estar en la carpeta correcta
cd /home/user/model-ia/Nano_Editor
python3 main.py
```

### Error: "No module named 'customtkinter'"
```bash
# Instala dependencias
pip install -r requirements.txt
```

### Quiero volver a v1.0 o v2.0
```bash
cd legacy
./run.sh      # v1.0
./run_v2.sh   # v2.0
```

## 📚 Documentación

- `README.md` - Documentación principal
- `PROJECT_ANALYSIS.md` - Análisis del proyecto
- `legacy/README.md` - Info de versiones antiguas
- `CHANGELOG_V2.md` - Cambios v2.0
- `FEATURES_V2.1.md` - Características v2.1

## ✅ Checklist de Migración

- [x] Versiones antiguas movidas a `legacy/`
- [x] `main.py` actualizado a v3.0
- [x] `run.sh` actualizado a v3.0
- [x] Documentación actualizada
- [x] Permisos de ejecución configurados
- [x] Compatibilidad con `.env` mantenida

## 🎯 Próximos Pasos

1. Ejecuta v3.0: `./run.sh`
2. Explora las nuevas características
3. Configura tu API key de Gemini si no lo has hecho
4. Prueba los nuevos paneles de la barra lateral
5. Usa los atajos de teclado VS Code

---

**¡Disfruta NanoEditor v3.0!** 🚀
