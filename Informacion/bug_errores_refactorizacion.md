# 🐛 Bugs y Errores Pendientes de Refactorización

**Fecha de detección:** 2026-02-22  
**Estado:** Pendiente (resolver después de completar la migración de directorios)

---

## Bug 1: Crash X11 — `X_CreatePixmap` con valor `0x0`

**Severidad:** 🔴 Alta (causa crash del editor)  
**Componente:** UI / Renderizado  

### Error
```
X Error of failed request:  BadValue (integer parameter out of range for operation)
  Major opcode of failed request:  53 (X_CreatePixmap)
  Value in failed request:  0x0
  Serial number of failed request:  578922
  Current serial number in output stream:  578930
```

### Descripción
Un widget de `customtkinter` intenta crear un pixmap (buffer gráfico) con dimensiones **0×0 píxeles**, lo cual es inválido en X11. Esto causa un crash inmediato del editor.

### Causas Probables
1. **SVG no convertido a CTkImage** — El warning al inicio confirma esto:
   ```
   CTkButton Warning: Given image is not CTkImage but <class 'tksvg.SvgImage'>.
   Image can not be scaled on HighDPI displays, use CTkImage instead.
   ```
   Un ícono SVG sin dimensiones válidas podría generar un pixmap de tamaño 0.
2. **Panel colapsado a 0px** — Un panel que se renderiza antes de tener dimensiones asignadas.
3. **Widget sin tamaño en layout** — Algún componente que no tiene `width`/`height` explícito.

### Pasos para Reproducir
1. Ejecutar `./run.sh`
2. Usar el editor normalmente (el crash parece intermitente)
3. El crash ocurre cuando se intenta renderizar el widget problemático

### Solución Propuesta
- [ ] Buscar todos los usos de `tksvg.SvgImage` y convertirlos a `CTkImage`
- [ ] Agregar validación de dimensiones mínimas (>0) antes de crear pixmaps
- [ ] Investigar qué widget específico causa el crash con logs de depuración

---

## Bug 2: Nano-Agent alucina contenido cuando el archivo no existe

**Severidad:** 🟡 Media  
**Componente:** AI / Agent (`ai/agent.py`)

### Descripción
Cuando el agente recibe una tarea sobre un archivo que no existe (ej: `api.py`), en lugar de reportar el error al usuario, genera código inventado (un juego de consola completo) como su "pensamiento" y reporta haber completado la tarea exitosamente.

### Log Relevante
```
INFO: Executing tool: fs_read_file with args: {'path': 'api.py'}
INFO: ❌ Error: File not found: .../api.py
INFO: 🔄 Agent Step 2/10
INFO: Executing tool: fs_list_dir with args: {'path': '.'}
INFO: 🔄 Agent Step 3/10
INFO: 🤖 Agent Thought: [~250 líneas de código inventado]
Final Answer: The api.py file has been refactored.
INFO: ✅ Agent finished (no more tools).
```

### Solución Propuesta
- [ ] Agregar validación en `ai/agent.py`: si el archivo objetivo no existe, abortar la tarea e informar al usuario
- [ ] Mejorar el system prompt (`ai/prompts.py`) para instruir al agente a no inventar archivos
- [ ] Implementar un mecanismo de verificación post-tarea que compare el estado antes/después

---

## Bug 3: Tool `terminal_run` se registra dos veces

**Severidad:** 🟢 Baja (no causa errores funcionales, solo es ineficiente)  
**Componente:** AI / Tools (`ai/tools.py`)

### Log
```
INFO: Tool registered: terminal_run
INFO: Tool registered: terminal_run
```

### Descripción
La herramienta `terminal_run` se registra dos veces durante la inicialización. El sistema ya maneja duplicados (reemplaza en lugar de duplicar), pero el doble registro es innecesario.

### Solución Propuesta
- [ ] Identificar dónde se llama `register_tool("terminal_run", ...)` por segunda vez
- [ ] Eliminar el registro duplicado
