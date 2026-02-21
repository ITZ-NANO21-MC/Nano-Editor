# 🗺️ Plan Maestro de Migración: De Asistente a Agente Autónomo (Nano-Agent)

Este documento detalla la hoja de ruta técnica para transformar a NanoEditor de un asistente reactivo (que responde preguntas) a un agente autónomo (que ejecuta tareas complejas por sí mismo), similar a Antigravity.

---

## 🏗️ Fase 1: Cimientos del Agente (Infraestructura)
**Objetivo:** Habilitar la capacidad de "ejecutar acciones" (Function Calling) sin romper la funcionalidad actual.

### Parte 1.1: Preparación del Cliente AI (`ai_client.py`)
- [x] **Soporte para `tools`**: Modificar el método `generate_content` en `AIClient` para aceptar definiciones de herramientas (JSON Schema).
- [x] **Manejo de `tool_calls`**: Detectar cuando el modelo quiere usar una herramienta en lugar de responder texto.
- [ ] **Bucle de Ejecución**: Implementar la lógica para recibir una `tool_call`, ejecutarla localmente y devolver el resultado al modelo.

### Parte 1.2: Registro de Herramientas (`ai_tools.py`)
- [x] **Crear `ToolRegistry`**: Una clase central para registrar funciones seguras.
- [x] **Implementar Herramientas Básicas**:
    - `fs_read_file(path)`: Leer contenido.
    - `fs_list_dir(path)`: Ver estructura.
    - `fs_write_file(path, content)`: Crear/Editar (con confirmación/backup).
    - `terminal_run(command)`: Ejecutar comandos de sistema (con confirmación).

---

## 🧠 Fase 2: El Cerebro (Lógica de Agente)
**Objetivo:** Crear el bucle de razonamiento "Pensar -> Actuar -> Observar -> Repetir".

### Parte 2.1: Clase Agente (`ai_agent.py`)
- [x] **Estado del Agente**: Memoria de corto plazo (historial de chat + resultados de herramientas).
- [x] **Thinking Loop**:
    1.  Recibir objetivo del usuario.
    2.  Analizar estado actual.
    3.  Decidir siguiente paso (Llamar herramienta o Responder).
    4.  Ejecutar herramienta.
    5.  Observar salida (stdout/stderr).
    6.  Repetir hasta cumplir objetivo o llegar a límite de pasos.

### Parte 2.2: Sistema de Prompts de Agente (`ai_prompts.py`)
- [x] **System Prompt de Agente**: Definir la personalidad "autónoma" (eres un ingeniero experto que usa herramientas).
- [x] **Reglas de Seguridad**: Instrucciones estrictas sobre no borrar archivos sin permiso, etc.

---

## 🖥️ Fase 3: Integración con la UI
**Objetivo:** Que el usuario pueda ver y controlar al agente.

### Parte 3.1: Panel de Agente (`agent_panel.py`)
- [x] **Visualización de Pasos**: UI para ver qué está "pensando" y "haciendo" el agente.
    - Ejemplo: `[🧠 Pensando...]` -> `[🛠️ Ejecutando: ls -la]` -> `[✅ Hecho]`
- [x] **Botones de Control**: `Aprobar Acción` (Auto), `Cancelar` (Stop), `Pausar` (No impl).

### Parte 3.2: Puente con la Terminal (`terminal_bridge.py`)
- [x] **Captura de Salida**: Conectar la salida del `TerminalPanel` real con el agente, para que "vea" si sus comandos funcionaron.

---

## 🛡️## Fase 4: Seguridad y Human-in-the-loop (NUEVO)
**Objetivo:** Evitar que el agente rompa cosas sin querer.

### Parte 4.1: Sistema de Permisos (`ai_security.py`)
- [x] **Niveles de Seguridad**: Crear sistema con niveles `PARANOID`, `SAFE`, `AUTONOMOUS`.
- [x] **Reglas**: Definir qué herramientas son seguras (ej. `list_dir`) y cuáles peligrosas (ej. `write_file`, `terminal_run`).

### Parte 4.2: Callback de Aprobación
- [x] **Hook en AIAgent**: Modificar el agente para pausar antes de ejecutar herramientas peligrosas y pedir permiso.
- [x] **UI de Aprobación**: Mostrar un modal emergente en el `AgentPanel` con los detalles de qué quiere hacer el agente y botones de "Aceptar" y "Rechazar".

---

## 🚀 Resumen del Flujo de Trabajo (Ejemplo)

**Usuario:** "Arregla los tests que están fallando."

1.  **Agente (Piensa)**: "Primero necesito ver qué tests fallan."
2.  **Agente (Acción)**: `terminal_run("pytest")`
3.  **Sistema**: Ejecuta comando y devuelve output.
4.  **Agente (Observa)**: "Veo un error en `test_login.py` línea 15."
5.  **Agente (Piensa)**: "Leeré ese archivo para entender el error."
6.  **Agente (Acción)**: `fs_read_file("test_login.py")`
7.  **Agente (Piensa)**: "Ah, falta un import. Lo corregiré."
8.  **Agente (Acción)**: `fs_write_file("test_login.py", content=...)`
9.  **Agente (Piensa)**: "Ahora correré los tests de nuevo para verificar."
10. **Agente (Acción)**: `terminal_run("pytest")`
11. **Agente (Observa)**: "Todos pasaron."
12. **Agente (Responde)**: "He arreglado el error de importación en `test_login.py`. Todo funciona ahora."

---
