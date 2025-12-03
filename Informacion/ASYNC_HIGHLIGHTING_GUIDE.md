# 🚀 Syntax Highlighting Asíncrono - Guía de Implementación

## 📋 Problema

El highlighting actual se ejecuta en cada tecla presionada, bloqueando la UI en archivos grandes.

---

## ✅ Solución: Debouncing + Threading

### Concepto

1. **Debouncing**: Esperar X ms después de la última tecla antes de resaltar
2. **Threading**: Ejecutar el resaltado en un hilo separado
3. **Cancelación**: Cancelar resaltados pendientes si hay nuevos cambios

---

## 🔧 Implementación Minimalista

### 1. Módulo Async Highlighter (`async_highlighter.py`)

```python
"""Asynchronous syntax highlighting."""
import threading
from typing import Callable, Optional
from pygments import lex
from pygments.lexers import get_lexer_for_filename, TextLexer

class AsyncHighlighter:
    """Non-blocking syntax highlighter with debouncing."""
    
    def __init__(self, delay_ms: int = 300):
        self.delay_ms = delay_ms
        self.timer: Optional[threading.Timer] = None
        self.current_thread: Optional[threading.Thread] = None
        
    def highlight_async(self, text: str, filepath: str, callback: Callable):
        """Schedule highlighting with debouncing."""
        # Cancel previous timer
        if self.timer:
            self.timer.cancel()
        
        # Schedule new highlighting
        self.timer = threading.Timer(
            self.delay_ms / 1000.0,
            self._do_highlight,
            args=(text, filepath, callback)
        )
        self.timer.start()
    
    def _do_highlight(self, text: str, filepath: str, callback: Callable):
        """Execute highlighting in background thread."""
        def worker():
            try:
                lexer = get_lexer_for_filename(filepath)
            except:
                lexer = TextLexer()
            
            tokens = list(lex(text, lexer))
            callback(tokens)
        
        self.current_thread = threading.Thread(target=worker, daemon=True)
        self.current_thread.start()
    
    def cancel(self):
        """Cancel pending highlighting."""
        if self.timer:
            self.timer.cancel()
```

### 2. Integración en TextArea

```python
# En text_area.py o CodeEditor

from async_highlighter import AsyncHighlighter

class CodeEditor(ctk.CTkTextbox):
    def __init__(self, master):
        super().__init__(master)
        self.highlighter = AsyncHighlighter(delay_ms=300)
        self.bind("<KeyRelease>", self.on_text_change)
    
    def on_text_change(self, event=None):
        """Trigger async highlighting."""
        if not self.file_path:
            return
        
        text = self.get("1.0", "end-1c")
        self.highlighter.highlight_async(
            text, 
            self.file_path,
            self.apply_highlighting
        )
    
    def apply_highlighting(self, tokens):
        """Apply highlighting tokens to text (runs in main thread)."""
        # Schedule in main thread
        self.after(0, lambda: self._apply_tokens(tokens))
    
    def _apply_tokens(self, tokens):
        """Apply tokens to text widget."""
        # Remove old tags
        for tag in self.tag_names():
            if tag.startswith("Token."):
                self.tag_remove(tag, "1.0", "end")
        
        # Apply new tags
        pos = "1.0"
        for token_type, value in tokens:
            end_pos = f"{pos}+{len(value)}c"
            tag = f"Token.{token_type}"
            self.tag_add(tag, pos, end_pos)
            pos = end_pos
```

---

## 📊 Comparación

| Aspecto | Síncrono | Asíncrono |
|---------|----------|-----------|
| **Bloqueo UI** | Sí | No |
| **Delay** | 0ms | 300ms |
| **CPU** | Picos altos | Distribuido |
| **Archivos grandes** | Lento | Rápido |
| **Complejidad** | Baja | Media |

---

## 🎯 Optimizaciones Adicionales

### 1. Highlighting Incremental

```python
def highlight_visible_only(self):
    """Only highlight visible lines."""
    first_visible = self.index("@0,0")
    last_visible = self.index(f"@0,{self.winfo_height()}")
    # Solo resaltar líneas visibles
```

### 2. Cache de Tokens

```python
class AsyncHighlighter:
    def __init__(self):
        self.cache = {}  # filepath -> tokens
    
    def get_cached(self, filepath, text_hash):
        """Return cached tokens if available."""
        key = (filepath, text_hash)
        return self.cache.get(key)
```

### 3. Límite de Tamaño

```python
MAX_HIGHLIGHT_SIZE = 100_000  # 100KB

def should_highlight(self, text):
    """Skip highlighting for very large files."""
    return len(text) < MAX_HIGHLIGHT_SIZE
```

---

## 🔍 Ejemplo Completo Minimalista

```python
# async_highlighter.py
import threading
from typing import Callable

class AsyncHighlighter:
    def __init__(self, delay_ms=300):
        self.delay_ms = delay_ms
        self.timer = None
    
    def highlight(self, text, filepath, callback):
        if self.timer:
            self.timer.cancel()
        
        self.timer = threading.Timer(
            self.delay_ms / 1000.0,
            lambda: self._highlight(text, filepath, callback)
        )
        self.timer.start()
    
    def _highlight(self, text, filepath, callback):
        def worker():
            from pygments import lex
            from pygments.lexers import get_lexer_for_filename
            
            try:
                lexer = get_lexer_for_filename(filepath)
                tokens = list(lex(text, lexer))
                callback(tokens)
            except:
                pass
        
        threading.Thread(target=worker, daemon=True).start()
```

---

## ✅ Beneficios

1. **UI Responsiva**: No se congela al escribir
2. **Mejor UX**: Experiencia fluida en archivos grandes
3. **Eficiencia**: Solo resalta después de pausas
4. **Cancelación**: Evita trabajo innecesario

---

## ⚠️ Consideraciones

1. **Thread Safety**: Usar `after()` para actualizar UI
2. **Memoria**: Cancelar timers al cerrar tabs
3. **Testing**: Más complejo de testear
4. **Delay**: 300ms es un buen balance

---

## 📈 Impacto Esperado

| Métrica | Antes | Después |
|---------|-------|---------|
| Lag al escribir | Alto | Ninguno |
| CPU usage | Picos | Suave |
| Archivos >10KB | Lento | Rápido |
| Complejidad | Baja | Media |

---

## 🚀 Implementación Recomendada

### Fase 1: Debouncing Simple (1 hora)
```python
# Solo agregar delay, sin threading
def on_key_release(self):
    if self.timer:
        self.after_cancel(self.timer)
    self.timer = self.after(300, self.highlight_text)
```

### Fase 2: Threading (2 horas)
- Agregar AsyncHighlighter
- Mover highlighting a thread
- Usar after() para aplicar resultados

### Fase 3: Optimizaciones (opcional)
- Cache de tokens
- Highlighting incremental
- Límites de tamaño

---

## 💡 Conclusión

El highlighting asíncrono es una mejora importante para archivos grandes:

- ✅ **Fácil**: Debouncing simple ya mejora mucho
- ✅ **Efectivo**: Threading elimina lag completamente
- ✅ **Escalable**: Funciona con archivos de cualquier tamaño

