# 🔧 Reducir Acoplamiento - Guía Completa

## 📋 Problema Actual

### Alto Acoplamiento en NanoEditor

```python
# ❌ ANTES: App conoce TODO
class App:
    def open_file(self, path):
        # App debe conocer y actualizar TODOS los componentes
        self.tab_manager.new_tab(path)
        self.file_tree.load_directory(dirname(path))
        self.terminal.set_working_directory(dirname(path))
        self.status_bar.set_file_path(path)
        self.feedback.show_success("Opened")
        # 5 dependencias directas!
```

**Problemas:**
- App tiene 15+ dependencias directas
- Cambiar un componente afecta a App
- Difícil de testear
- Difícil de extender

---

## ✅ Solución: Event System (Observer Pattern)

### Concepto

```
Componente A → Emite evento → Event Bus → Componentes B, C, D escuchan
```

**Beneficios:**
- Componentes no se conocen entre sí
- Fácil agregar/quitar listeners
- Fácil de testear
- Extensible

---

## 🔧 Implementación Minimalista

### 1. Event Bus Simple

```python
# event_bus.py
from typing import Callable, Dict, List

class EventBus:
    """Simple event bus for decoupling components."""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event: str, callback: Callable):
        """Subscribe to an event."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)
    
    def emit(self, event: str, data=None):
        """Emit an event to all subscribers."""
        if event in self._listeners:
            for callback in self._listeners[event]:
                callback(data)
    
    def unsubscribe(self, event: str, callback: Callable):
        """Unsubscribe from an event."""
        if event in self._listeners:
            self._listeners[event].remove(callback)

# Global event bus
event_bus = EventBus()
```

### 2. Eventos Definidos

```python
# events.py
class Events:
    """Event names."""
    FILE_OPENED = "file_opened"
    FILE_SAVED = "file_saved"
    FILE_CLOSED = "file_closed"
    TAB_CHANGED = "tab_changed"
    THEME_CHANGED = "theme_changed"
    AI_STARTED = "ai_started"
    AI_COMPLETED = "ai_completed"
```

### 3. Refactorizar App

```python
# ✅ DESPUÉS: App solo emite eventos
class App:
    def __init__(self):
        self.event_bus = EventBus()
        # Componentes se suscriben ellos mismos
        self.tab_manager = TabManager(content, self.event_bus)
        self.file_tree = VSCodeFileTree(panel, self.event_bus)
        self.terminal = TerminalPanel(content, self.event_bus)
    
    def open_file(self, path):
        # Solo emitir evento
        self.event_bus.emit(Events.FILE_OPENED, {
            'path': path,
            'content': content
        })
        # ¡Los componentes se actualizan solos!
```

### 4. Componentes Escuchan

```python
# file_tree.py
class VSCodeFileTree:
    def __init__(self, parent, event_bus):
        self.event_bus = event_bus
        # Suscribirse a eventos
        self.event_bus.subscribe(Events.FILE_OPENED, self.on_file_opened)
    
    def on_file_opened(self, data):
        # Actualizar automáticamente
        self.load_directory(os.path.dirname(data['path']))

# terminal_panel.py
class TerminalPanel:
    def __init__(self, parent, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe(Events.FILE_OPENED, self.on_file_opened)
    
    def on_file_opened(self, data):
        self.set_working_directory(os.path.dirname(data['path']))
```

---

## 📊 Comparación

### Antes (Alto Acoplamiento)
```python
# App debe conocer TODO
def open_file(self, path):
    self.tab_manager.new_tab(path)          # Dependencia 1
    self.file_tree.load_directory(...)     # Dependencia 2
    self.terminal.set_working_directory(...) # Dependencia 3
    self.status_bar.set_file_path(...)     # Dependencia 4
    self.feedback.show_success(...)        # Dependencia 5
```

**Dependencias**: 5 directas

### Después (Bajo Acoplamiento)
```python
# App solo emite evento
def open_file(self, path):
    self.event_bus.emit(Events.FILE_OPENED, {'path': path})
```

**Dependencias**: 1 (event_bus)

---

## 🎯 Eventos en NanoEditor

### Eventos de Archivo
```python
FILE_OPENED   → file_tree, terminal, status_bar escuchan
FILE_SAVED    → status_bar, feedback escuchan
FILE_CLOSED   → tab_manager, file_tree escuchan
```

### Eventos de Tab
```python
TAB_CHANGED   → status_bar, syntax_highlighter escuchan
TAB_CREATED   → tab_manager actualiza UI
TAB_CLOSED    → tab_manager limpia recursos
```

### Eventos de IA
```python
AI_STARTED    → feedback muestra progress
AI_COMPLETED  → feedback muestra success
AI_ERROR      → feedback muestra error
```

### Eventos de Tema
```python
THEME_CHANGED → file_tree, sidebar, todos actualizan colores
```

---

## 💡 Ejemplo Completo

### Antes
```python
class App:
    def save_file(self):
        # Alto acoplamiento
        tab = self.tab_manager.get_current_tab()
        with open(tab.file_path, 'w') as f:
            f.write(content)
        
        self.tab_manager.update_tab_title()
        self.status_bar.set_file_path(f"Saved: {path}")
        self.feedback.show_success("File saved")
        logger.info(f"Saved: {path}")
```

### Después
```python
class App:
    def save_file(self):
        # Bajo acoplamiento
        tab = self.tab_manager.get_current_tab()
        with open(tab.file_path, 'w') as f:
            f.write(content)
        
        # Solo emitir evento
        self.event_bus.emit(Events.FILE_SAVED, {
            'path': tab.file_path
        })

# Componentes escuchan
class TabManager:
    def on_file_saved(self, data):
        self.update_tab_title()

class StatusBar:
    def on_file_saved(self, data):
        self.set_file_path(f"Saved: {data['path']}")

class VisualFeedback:
    def on_file_saved(self, data):
        self.show_success("File saved")
```

---

## 🚀 Implementación Gradual

### Fase 1: Crear Event Bus (30 min)
```python
# 1. Crear event_bus.py
# 2. Crear events.py con nombres
# 3. Agregar event_bus a App
```

### Fase 2: Migrar Eventos de Archivo (1 hora)
```python
# 1. FILE_OPENED
# 2. FILE_SAVED
# 3. FILE_CLOSED
```

### Fase 3: Migrar Eventos de Tab (1 hora)
```python
# 1. TAB_CHANGED
# 2. TAB_CREATED
# 3. TAB_CLOSED
```

### Fase 4: Migrar Eventos de IA (30 min)
```python
# 1. AI_STARTED
# 2. AI_COMPLETED
# 3. AI_ERROR
```

---

## 📈 Beneficios

| Aspecto | Antes | Después |
|---------|-------|---------|
| Dependencias en App | 15+ | 1 (event_bus) |
| Acoplamiento | Alto | Bajo |
| Testabilidad | Difícil | Fácil |
| Extensibilidad | Difícil | Fácil |
| Mantenibilidad | Media | Alta |

---

## 🧪 Testing Mejorado

### Antes (Difícil)
```python
# Necesitas mockear TODO
def test_open_file():
    app = App()
    app.tab_manager = Mock()
    app.file_tree = Mock()
    app.terminal = Mock()
    app.status_bar = Mock()
    app.feedback = Mock()
    # 5 mocks!
```

### Después (Fácil)
```python
# Solo mockear event_bus
def test_open_file():
    event_bus = Mock()
    app = App(event_bus)
    app.open_file("test.py")
    event_bus.emit.assert_called_with(Events.FILE_OPENED, ...)
```

---

## ⚠️ Consideraciones

### Ventajas
✅ Bajo acoplamiento
✅ Fácil de testear
✅ Fácil de extender
✅ Componentes independientes

### Desventajas
⚠️ Más indirección (eventos vs llamadas directas)
⚠️ Debugging más complejo (flujo no lineal)
⚠️ Requiere disciplina (documentar eventos)

---

## 🎯 Alternativas

### 1. Dependency Injection
```python
class App:
    def __init__(self, tab_manager, file_tree, terminal):
        # Inyectar dependencias
        self.tab_manager = tab_manager
```

### 2. Mediator Pattern
```python
class Mediator:
    def notify(self, sender, event):
        # Coordinar componentes
```

### 3. Command Pattern
```python
class OpenFileCommand:
    def execute(self):
        # Encapsular acción
```

---

## 📚 Conclusión

**Reducir acoplamiento** significa:
- Componentes no se conocen directamente
- Comunicación vía eventos
- Fácil de testear y extender

**Recomendación para NanoEditor**:
- Implementar Event Bus simple
- Migrar gradualmente (archivo → tab → IA)
- Mantener simplicidad

**Prioridad**: MEDIA (mejora arquitectura, no funcionalidad)

---

**Tiempo estimado**: 3-4 horas
**Impacto**: MEDIO (mejor código, misma funcionalidad)
**Complejidad**: MEDIA
