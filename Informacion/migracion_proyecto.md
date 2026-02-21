# 🏗️ Plan de Migración: Reestructuración de Directorios por Funcionalidad

**Proyecto:** NanoEditor v4.0  
**Fecha:** 2026-02-20  
**Estado:** Pendiente de aprobación

---

## 📊 Diagnóstico Actual

**Problema:** 40+ archivos `.py` en la raíz, sin organización por módulo.

| Métrica | Valor |
|---------|-------|
| Archivos Python en raíz | 40 |
| Imports inter-módulo | ~120 |
| Clusters funcionales identificados | 5 |

---

## 🎯 Estructura Objetivo

```
Nano-Editor/
├── main.py                     # Entry point
├── config.py                   # Configuración global
├── logger.py                   # Sistema de logging
├── event_bus.py                # Bus de eventos
│
├── core/                       # 🧱 Motor del Editor
│   ├── __init__.py
│   ├── editor_view.py          ← editor_view_v3.py
│   ├── text_area.py
│   ├── tab_manager.py
│   ├── line_numbers.py
│   ├── file_handler.py
│   ├── find_replace.py
│   ├── syntax_highlighter.py
│   ├── async_highlighter.py
│   └── completion_popup.py
│
├── ai/                         # 🤖 Inteligencia Artificial
│   ├── __init__.py
│   ├── client.py               ← ai_client.py
│   ├── assistant.py            ← ai_assistant.py
│   ├── handler.py              ← ai_handler.py
│   ├── prompts.py              ← ai_prompts.py
│   ├── utils.py                ← ai_utils.py
│   ├── completion.py           ← ai_completion.py
│   ├── file_operations.py      ← ai_file_operations.py
│   ├── agent.py                ← ai_agent.py
│   ├── tools.py                ← ai_tools.py
│   ├── security.py             ← ai_security.py
│   └── ghost_text.py           ← ghost_text_manager.py
│
├── ui/                         # 🖥️ Interfaz de Usuario
│   ├── __init__.py
│   ├── sidebar.py              ← sidebar_vscode.py
│   ├── file_tree.py            ← file_tree_vscode.py
│   ├── ai_panel.py             ← ai_panel_vscode.py
│   ├── ai_menu.py
│   ├── ai_completion_popup.py
│   ├── gemini_panel.py
│   ├── gemini_client.py
│   ├── agent_panel.py
│   ├── menu_bar.py
│   ├── status_bar.py
│   ├── visual_feedback.py
│   ├── about_window.py
│   ├── shortcuts_window.py
│   └── references_window.py
│
├── terminal/                   # 💻 Terminal Integrada
│   ├── __init__.py
│   ├── panel.py                ← terminal_panel.py
│   └── process.py              ← terminal_process.py
│
├── navigation/                 # 🧭 Navegación de Código
│   ├── __init__.py
│   ├── goto_definition.py
│   ├── project_context.py
│   └── project_search.py
│
├── scripts/                    # (sin cambios)
├── tests/                      # (actualizar imports)
├── Informacion/                # (sin cambios)
└── legacy/                     # (sin cambios)
```

---

## ⚙️ Fases de Implementación

### Fase 1: Terminal (Riesgo: BAJO)
**Archivos:** 2 | **Imports a actualizar:** ~5

#### Parte 1.1: Crear directorio y mover archivos
- [ ] Crear `terminal/` con `__init__.py`
- [ ] `git mv terminal_panel.py terminal/panel.py`
- [ ] `git mv terminal_process.py terminal/process.py`

#### Parte 1.2: Actualizar imports
- [ ] En `terminal/panel.py`: actualizar import de `terminal_process` → `from terminal.process import ...`
- [ ] En `editor_view_v3.py`: `from terminal_panel import ...` → `from terminal.panel import ...`
- [ ] En `agent_panel.py`: actualizar referencia a terminal

#### Parte 1.3: Crear re-exports en `__init__.py`
```python
# terminal/__init__.py
from terminal.panel import TerminalPanel
from terminal.process import TerminalProcess
```

#### Parte 1.4: Verificación
- [ ] `./run.sh` → editor abre correctamente
- [ ] Terminal integrada funciona
- [ ] Agente puede ejecutar `terminal_run`

---

### Fase 2: Navegación (Riesgo: BAJO)
**Archivos:** 3 | **Imports a actualizar:** ~8

#### Parte 2.1: Crear directorio y mover archivos
- [ ] Crear `navigation/` con `__init__.py`
- [ ] `git mv goto_definition.py navigation/`
- [ ] `git mv project_context.py navigation/`
- [ ] `git mv project_search.py navigation/`

#### Parte 2.2: Actualizar imports
- [ ] En `navigation/project_context.py`: imports de `tab_manager`, `file_tree_vscode`, `config`
- [ ] En `editor_view_v3.py`: actualizar 3 imports de navegación
- [ ] En `text_area.py`: referencia a `goto_definition`

#### Parte 2.3: Verificación
- [ ] `./run.sh` → editor abre
- [ ] Ctrl+Click (Goto Definition) funciona
- [ ] Búsqueda en proyecto funciona

---

### Fase 3: AI & Agente (Riesgo: MEDIO)
**Archivos:** 12 | **Imports a actualizar:** ~35

#### Parte 3.1: Crear directorio y mover archivos
- [ ] Crear `ai/` con `__init__.py`
- [ ] Mover archivos con `git mv`:
    - `ai_client.py` → `ai/client.py`
    - `ai_assistant.py` → `ai/assistant.py`
    - `ai_handler.py` → `ai/handler.py`
    - `ai_prompts.py` → `ai/prompts.py`
    - `ai_utils.py` → `ai/utils.py`
    - `ai_completion.py` → `ai/completion.py`
    - `ai_file_operations.py` → `ai/file_operations.py`
    - `ai_agent.py` → `ai/agent.py`
    - `ai_tools.py` → `ai/tools.py`
    - `ai_security.py` → `ai/security.py`
    - `ghost_text_manager.py` → `ai/ghost_text.py`

#### Parte 3.2: Actualizar imports internos del módulo `ai/`
- [ ] Todos los archivos en `ai/` que se importan entre sí
- [ ] Ejemplo: `from ai_client import AIClient` → `from ai.client import AIClient`

#### Parte 3.3: Actualizar imports externos
- [ ] `editor_view_v3.py` (~8 imports de AI)
- [ ] `text_area.py` (~3 imports: completion, ghost_text)
- [ ] `gemini_panel.py` (~2 imports: ai_utils)
- [ ] `agent_panel.py` (~2 imports: ai_agent, ai_utils)

#### Parte 3.4: Crear `ai/__init__.py` con re-exports
```python
# ai/__init__.py
from ai.client import AIClient
from ai.assistant import AIAssistant
from ai.agent import AIAgent
from ai.completion import completion_engine
```

#### Parte 3.5: Verificación
- [ ] `./run.sh` → editor abre
- [ ] Chat Gemini funciona
- [ ] Autocompletado AI funciona
- [ ] Agent Panel funciona

---

### Fase 4: UI & Paneles (Riesgo: MEDIO-ALTO)
**Archivos:** 14 | **Imports a actualizar:** ~25

#### Parte 4.1: Crear directorio y mover archivos
- [ ] Crear `ui/` con `__init__.py`
- [ ] Mover con `git mv`:
    - `sidebar_vscode.py` → `ui/sidebar.py`
    - `file_tree_vscode.py` → `ui/file_tree.py`
    - `ai_panel_vscode.py` → `ui/ai_panel.py`
    - `ai_menu.py` → `ui/ai_menu.py`
    - `ai_completion_popup.py` → `ui/ai_completion_popup.py`
    - `gemini_panel.py` → `ui/gemini_panel.py`
    - `gemini_client.py` → `ui/gemini_client.py`
    - `agent_panel.py` → `ui/agent_panel.py`
    - `menu_bar.py` → `ui/menu_bar.py`
    - `status_bar.py` → `ui/status_bar.py`
    - `visual_feedback.py` → `ui/visual_feedback.py`
    - `about_window.py` → `ui/about_window.py`
    - `shortcuts_window.py` → `ui/shortcuts_window.py`
    - `references_window.py` → `ui/references_window.py`

#### Parte 4.2: Actualizar imports
- [ ] Imports internos de `ui/` entre sí
- [ ] `editor_view_v3.py` (~12 imports de UI)
- [ ] Imports de módulos `ai/` que referencian paneles

#### Parte 4.3: Verificación
- [ ] `./run.sh` → editor abre
- [ ] Sidebar y todos los paneles funcionan
- [ ] Menús de IA funcionan

---

### Fase 5: Core del Editor (Riesgo: ALTO)
**Archivos:** 8 | **Imports a actualizar:** ~30

#### Parte 5.1: Crear directorio y mover archivos
- [ ] Crear `core/` con `__init__.py`
- [ ] Mover con `git mv`:
    - `editor_view_v3.py` → `core/editor_view.py`
    - `text_area.py` → `core/text_area.py`
    - `tab_manager.py` → `core/tab_manager.py`
    - `line_numbers.py` → `core/line_numbers.py`
    - `file_handler.py` → `core/file_handler.py`
    - `find_replace.py` → `core/find_replace.py`
    - `syntax_highlighter.py` → `core/syntax_highlighter.py`
    - `async_highlighter.py` → `core/async_highlighter.py`
    - `completion_popup.py` → `core/completion_popup.py`

#### Parte 5.2: Actualizar `main.py`
```python
# main.py (actualizado)
from core.editor_view import App
App().mainloop()
```

#### Parte 5.3: Actualizar todos los imports restantes
- [ ] Todos los módulos `ai/`, `ui/`, `navigation/` que referencian `core/`
- [ ] `core/` imports internos

#### Parte 5.4: Verificación Final
- [ ] `./run.sh` → editor abre completamente
- [ ] Todas las funcionalidades verificadas
- [ ] Tests pasan

---

### Fase 6: Limpieza Final (Riesgo: BAJO)
- [ ] Eliminar archivos huérfanos de la raíz
- [ ] Limpiar `__pycache__/` recursivamente
- [ ] Actualizar `tests/` con nuevos imports
- [ ] Actualizar `scripts/` con nuevos imports
- [ ] Actualizar `README.md` con nueva estructura
- [ ] Actualizar `.gitignore` si es necesario
- [ ] Commit final: `refactor: Reorganize project into functional directories`

---

## ⚠️ Reglas de Seguridad

1. **Un commit por fase** → fácil rollback si algo falla
2. **`./run.sh` tras cada fase** → verificar que nada se rompió
3. **`git mv`** siempre → preservar historial de Git
4. **Limpiar `__pycache__`** tras cada fase → evitar imports fantasma
5. **No mezclar fases** → si la Fase 3 falla, no empezar la Fase 4

---

## 📋 Resumen de Esfuerzo

| Fase | Archivos | Imports | Riesgo | Estimado |
|------|----------|---------|--------|----------|
| 1. Terminal | 2 | ~5 | 🟢 Bajo | 5 min |
| 2. Navegación | 3 | ~8 | 🟢 Bajo | 10 min |
| 3. AI & Agente | 12 | ~35 | 🟡 Medio | 30 min |
| 4. UI & Paneles | 14 | ~25 | 🟠 Medio-Alto | 25 min |
| 5. Core Editor | 8 | ~30 | 🔴 Alto | 30 min |
| 6. Limpieza | - | ~10 | 🟢 Bajo | 10 min |
| **Total** | **39** | **~113** | - | **~2 horas** |
