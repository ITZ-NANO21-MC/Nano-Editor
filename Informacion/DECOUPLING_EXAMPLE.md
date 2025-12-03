# 🔧 Ejemplo Práctico: Reducir Acoplamiento

## 📊 Comparación Directa

### ❌ ANTES: Alto Acoplamiento

```python
# editor_view_v3.py
class App:
    def __init__(self):
        # App conoce TODOS los componentes
        self.tab_manager = TabManager(content)
        self.file_tree = VSCodeFileTree(panel, self)
        self.terminal = TerminalPanel(content)
        self.status_bar = StatusBar(main)
        self.feedback = VisualFeedback(self)
        # 5+ dependencias directas
    
    def open_file(self, path):
        # App debe actualizar TODOS manualmente
        content = open(path).read()
        
        # Dependencia 1
        tab_index = self.tab_manager.new_tab(path)
        tab = self.tab_manager.tabs[tab_index]
        tab.content = content
        self.tab_manager.switch_tab(tab_index)
        
        # Dependencia 2
        self.file_tree.load_directory(os.path.dirname(path))
        
        # Dependencia 3
        self.terminal.set_working_directory(os.path.dirname(path))
        
        # Dependencia 4
        self.status_bar.set_file_path(path)
        
        # Dependencia 5
        self.feedback.show_success(f"Opened: {os.path.basename(path)}")
        
        # Dependencia 6
        logger.info(f"Opened: {path}")
```

**Problemas:**
- 6 dependencias directas
- App debe conocer cómo actualizar cada componente
- Cambiar un componente requiere cambiar App
- Difícil de testear (6 mocks necesarios)

---

### ✅ DESPUÉS: Bajo Acoplamiento

```python
# editor_view_v3.py
from event_bus import event_bus, Events

class App:
    def __init__(self):
        # Componentes se suscriben ellos mismos
        self.tab_manager = TabManager(content, event_bus)
        self.file_tree = VSCodeFileTree(panel, event_bus)
        self.terminal = TerminalPanel(content, event_bus)
        self.status_bar = StatusBar(main, event_bus)
        self.feedback = VisualFeedback(self, event_bus)
        # Solo 1 dependencia: event_bus
    
    def open_file(self, path):
        # Solo leer archivo y emitir evento
        content = open(path).read()
        
        # Emitir UN evento
        event_bus.emit(Events.FILE_OPENED, {
            'path': path,
            'content': content,
            'dirname': os.path.dirname(path),
            'basename': os.path.basename(path)
        })
        # ¡Los componentes se actualizan solos!
```

**Beneficios:**
- 1 dependencia (event_bus)
- App no conoce detalles de componentes
- Fácil agregar/quitar componentes
- Fácil de testear (1 mock)

---

## 🔧 Componentes Refactorizados

### TabManager

```python
# tab_manager.py
class TabManager:
    def __init__(self, parent, event_bus):
        super().__init__(parent)
        self.event_bus = event_bus
        
        # Suscribirse a eventos
        self.event_bus.subscribe(Events.FILE_OPENED, self.on_file_opened)
        self.event_bus.subscribe(Events.FILE_SAVED, self.on_file_saved)
    
    def on_file_opened(self, data):
        """Responder a FILE_OPENED."""
        tab_index = self.new_tab(data['path'])
        tab = self.tabs[tab_index]
        tab.content = data['content']
        self.switch_tab(tab_index)
        
        # Emitir evento de tab cambiado
        self.event_bus.emit(Events.TAB_CHANGED, {
            'tab_index': tab_index,
            'file_path': data['path']
        })
    
    def on_file_saved(self, data):
        """Responder a FILE_SAVED."""
        self.update_tab_title()
```

### FileTree

```python
# file_tree_vscode.py
class VSCodeFileTree:
    def __init__(self, parent, event_bus):
        super().__init__(parent)
        self.event_bus = event_bus
        
        # Suscribirse
        self.event_bus.subscribe(Events.FILE_OPENED, self.on_file_opened)
    
    def on_file_opened(self, data):
        """Actualizar árbol cuando se abre archivo."""
        self.load_directory(data['dirname'])
```

### Terminal

```python
# terminal_panel.py
class TerminalPanel:
    def __init__(self, parent, event_bus):
        super().__init__(parent)
        self.event_bus = event_bus
        
        # Suscribirse
        self.event_bus.subscribe(Events.FILE_OPENED, self.on_file_opened)
    
    def on_file_opened(self, data):
        """Cambiar directorio cuando se abre archivo."""
        self.set_working_directory(data['dirname'])
```

### StatusBar

```python
# status_bar.py
class StatusBar:
    def __init__(self, parent, event_bus):
        super().__init__(parent)
        self.event_bus = event_bus
        
        # Suscribirse
        self.event_bus.subscribe(Events.FILE_OPENED, self.on_file_opened)
        self.event_bus.subscribe(Events.FILE_SAVED, self.on_file_saved)
    
    def on_file_opened(self, data):
        self.set_file_path(data['path'])
    
    def on_file_saved(self, data):
        self.set_file_path(f"Saved: {data['path']}")
```

### VisualFeedback

```python
# visual_feedback.py
class VisualFeedback:
    def __init__(self, parent, event_bus):
        super().__init__(parent)
        self.event_bus = event_bus
        
        # Suscribirse
        self.event_bus.subscribe(Events.FILE_OPENED, self.on_file_opened)
        self.event_bus.subscribe(Events.FILE_SAVED, self.on_file_saved)
        self.event_bus.subscribe(Events.AI_STARTED, self.on_ai_started)
        self.event_bus.subscribe(Events.AI_COMPLETED, self.on_ai_completed)
    
    def on_file_opened(self, data):
        self.show_success(f"Opened: {data['basename']}")
    
    def on_file_saved(self, data):
        self.show_success("File saved")
    
    def on_ai_started(self, data):
        self.show_progress(data.get('message', 'Processing...'))
    
    def on_ai_completed(self, data):
        self.hide_progress()
        self.show_success("AI completed")
```

---

## 📊 Diagrama de Flujo

### Antes (Alto Acoplamiento)
```
App.open_file()
    ├─> TabManager.new_tab()
    ├─> FileTree.load_directory()
    ├─> Terminal.set_working_directory()
    ├─> StatusBar.set_file_path()
    └─> Feedback.show_success()
```

### Después (Bajo Acoplamiento)
```
App.open_file()
    └─> event_bus.emit(FILE_OPENED)
            ├─> TabManager.on_file_opened()
            ├─> FileTree.on_file_opened()
            ├─> Terminal.on_file_opened()
            ├─> StatusBar.on_file_opened()
            └─> Feedback.on_file_opened()
```

---

## 🧪 Testing Mejorado

### Antes
```python
def test_open_file():
    # Necesitas mockear TODO
    app = App()
    app.tab_manager = Mock()
    app.file_tree = Mock()
    app.terminal = Mock()
    app.status_bar = Mock()
    app.feedback = Mock()
    
    app.open_file("test.py")
    
    # Verificar 5 llamadas
    app.tab_manager.new_tab.assert_called()
    app.file_tree.load_directory.assert_called()
    app.terminal.set_working_directory.assert_called()
    app.status_bar.set_file_path.assert_called()
    app.feedback.show_success.assert_called()
```

### Después
```python
def test_open_file():
    # Solo mockear event_bus
    event_bus = Mock()
    app = App(event_bus)
    
    app.open_file("test.py")
    
    # Verificar 1 llamada
    event_bus.emit.assert_called_with(
        Events.FILE_OPENED,
        {'path': 'test.py', ...}
    )
```

---

## 📈 Métricas

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Dependencias en App | 15+ | 1 | ✅ 93% |
| Líneas en open_file() | 20+ | 5 | ✅ 75% |
| Mocks en tests | 5+ | 1 | ✅ 80% |
| Acoplamiento | Alto | Bajo | ✅ 100% |
| Extensibilidad | Difícil | Fácil | ✅ 100% |

---

## 🚀 Migración Paso a Paso

### Paso 1: Crear Event Bus
```bash
# Crear event_bus.py
# Ya está listo ✅
```

### Paso 2: Migrar open_file()
```python
# 1. Agregar event_bus a __init__
# 2. Cambiar open_file() para emitir evento
# 3. Agregar listeners en componentes
```

### Paso 3: Migrar save_file()
```python
# Similar a open_file()
```

### Paso 4: Migrar operaciones IA
```python
# AI_STARTED, AI_COMPLETED, AI_ERROR
```

---

## 💡 Conclusión

**Reducir acoplamiento** transforma:
```python
# De esto (15 líneas, 5 dependencias)
def open_file(self, path):
    content = open(path).read()
    self.tab_manager.new_tab(path)
    self.file_tree.load_directory(...)
    self.terminal.set_working_directory(...)
    self.status_bar.set_file_path(...)
    self.feedback.show_success(...)

# A esto (3 líneas, 1 dependencia)
def open_file(self, path):
    content = open(path).read()
    event_bus.emit(Events.FILE_OPENED, {'path': path, 'content': content})
```

**Beneficio**: Código más limpio, mantenible y testeable ✅
