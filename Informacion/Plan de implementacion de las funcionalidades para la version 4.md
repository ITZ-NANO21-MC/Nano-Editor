# Plan de Implementación: Fase 2 (Características IDE v4.0)

Este plan divide las funcionalidades complejas en módulos independientes y testeables. Se basa en crear primero la lógica pura (Backend/Core) con sus tests (`tests/`), y luego integrarla en la interfaz de usuario (`ui/`).

## 🐛 Sprint 1: Integración de Debugging Básico (Python)
**Objetivo:** Permitir gestionar Breakpoints y ejecutar código paso a paso usando `Pdb` o `debugpy`.
**Prioridad:** ALTA

### Parte 1.1: Gestor de Breakpoints (Core Lógico) ✅ COMPLETADO
- **Archivo:** `core/debugger/breakpoint_manager.py`
- **Funcionalidad:** `add_breakpoint`, `remove_breakpoint`, `get_breakpoints`.
- **Validación:** `tests/test_debugger.py` (Unit tests para CRUD de breakpoints).

### Parte 1.2: Panel Visual de Breakpoints (UI) ✅ COMPLETADO
- **Archivos:** `core/line_numbers.py`, `ui/debug_panel.py`.
- **Funcionalidad:** Dibujar círculos rojos `⬤` en el margen. Vincular clic con `BreakpointManager`.

### Parte 1.3: Controlador de Ejecución (Pdb Wrapper) ✅ COMPLETADO
- **Archivo:** `core/debugger/execution_controller.py`
- **Funcionalidad:** Iniciar/Detener proceso, inyectar breakpoints, capturar `locals()`.
- **Validación:** Mock de subprocesos para verificar comandos de Pdb.

---

## 🗃️ Sprint 2: Panel de Integración Git
**Objetivo:** Visualizar ramas, cambios y realizar operaciones básicas (Commit, Push, Pull).
**Prioridad:** ALTA

### Parte 2.1: Wrapper de Git (Core Lógico) ✅ COMPLETADO
- **Archivo:** `core/git/git_manager.py`
- **Funcionalidad:** `get_status`, `get_current_branch`, `commit(message)`.
- **Validación:** `tests/test_git.py` (Repositorio temporal en `/tmp` para pruebas).

### Parte 2.2: Interfaz Visual (Sidebar Git) ✅ COMPLETADO
- **Archivo:** `ui/git_panel.py`
- **Funcionalidad:** Árbol de archivos con estados (M, A, D), caja de commit.
- **Validación:** Mocking de `git_manager` para asegurar renderizado correcto.

### Parte 2.3: Diff Viewer ✅ COMPLETADO
- **Archivo:** `ui/diff_viewer.py`
- **Funcionalidad:** Vista dividida (Diff lado a lado o unificado).

---

## 🔨 Sprint 3: Herramientas de Refactorización
**Objetivo:** Automatizar cambios estructurales seguros.
**Prioridad:** MEDIA

### Parte 3.1: Renombrado Inteligente (Rename Symbol) ✅ COMPLETADO
- **Archivo:** `core/refactoring/renamer.py`
- **Funcionalidad:** Integración con `jedi.Script.rename`.
- **Validación:** `tests/test_refactoring.py` (Renombrado cross-file en entorno simulado).

### Parte 3.2: Extracción de Funciones (Extract Method) ✅ COMPLETADO
- **Archivo:** `core/refactoring/extractor.py`
- **Funcionalidad:** Análisis con `ast` para determinar alcance y variables.

---

### Parte 3.3: Extracción de Variable (Extract Variable) ✅ COMPLETADO
- **Archivo:** `core/refactoring/extractor.py`
- **Funcionalidad:** Extraer una expresión seleccionada a una nueva variable y reemplazar la expresión con el nombre de la variable.
- **UI:** Atajo de teclado (`Ctrl+Shift+L`), input dialog para el nombre de la variable.

### Parte 3.4: Mover a Archivo (Move to File) ✅ COMPLETADO
- **Archivo:** `core/refactoring/mover.py` (Nuevo)
- **Funcionalidad:** Mover una clase o función seleccionada a otro archivo, actualizando los imports según sea necesario (usando `jedi` o `ast`).
- **UI:** Atajo de teclado (`Ctrl+Shift+M`), file dialog para seleccionar el archivo destino.

---

## 🧪 Estrategia de Validación
Todas las nuevas funcionalidades **DEBEN** incluir:
1. Pruebas unitarias que validen la lógica sin necesidad de abrir la interfaz gráfica.
2. Mocks para dependencias externas (subprocesos de Git, procesos de Debug, Jedi).
3. Cobertura de casos de borde (ej: intentar debuguear archivos no guardados o git en carpetas sin repo).

---

**Fecha de creación:** 27 Febrero 2026
**Estado:** ✅ FASE 2 COMPLETADA (Pendiente 3.3 y 3.4) — Todos los 27 tests nuevos pasan (13 debugger + 6 git + 8 refactoring)
