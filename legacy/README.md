# Legacy Versions - NanoEditor

Esta carpeta contiene versiones antiguas de NanoEditor archivadas para retrocompatibilidad.

## 📦 Contenido

### Versión 1.0
- `editor_view.py` - GUI original con menú tradicional
- `main.py` - Entry point v1.0
- `file_tree.py` - Explorador de archivos con ttk.Treeview
- `run.sh` - Script de ejecución v1.0

**Características v1.0:**
- Editor básico con syntax highlighting
- Menú tradicional tkinter
- File tree simple
- Gemini panel básico

### Versión 2.0
- `editor_view_v2.py` - GUI con tabs y terminal
- `main_v2.py` - Entry point v2.0
- `run_v2.sh` - Script de ejecución v2.0

**Características v2.0:**
- Sistema multi-tab
- Terminal integrado
- Gemini panel mejorado
- Goto definition (F12)
- Project search

## 🚀 Uso

Para ejecutar versiones antiguas desde la carpeta legacy:

```bash
# Versión 1.0
cd legacy
./run.sh

# Versión 2.0
cd legacy
./run_v2.sh
```

## ⚠️ Nota

Estas versiones están archivadas y no reciben actualizaciones.

**Versión actual recomendada:** NanoEditor v3.0 (`editor_view_v3.py`)

## 🔄 Migración a v3.0

Si estás usando v1.0 o v2.0, considera migrar a v3.0 que incluye:

- ✅ Interfaz moderna estilo VS Code
- ✅ Barra lateral con iconos
- ✅ Panel de AI Assistant mejorado
- ✅ Explorador de archivos con iconos
- ✅ Mejor organización de paneles
- ✅ Atajos de teclado VS Code
- ✅ Todas las características de v1.0 y v2.0

Para ejecutar v3.0:
```bash
cd ..
./run_v3.sh
```
