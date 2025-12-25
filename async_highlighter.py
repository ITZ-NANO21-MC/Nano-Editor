"""Asynchronous syntax highlighting with debouncing."""
import threading
from typing import Callable, Optional, List, Tuple, Any
from pygments import lex
from pygments.lexers import get_lexer_for_filename, TextLexer


class AsyncHighlighter:
    """Non-blocking syntax highlighter with debouncing."""
    
    def __init__(self, delay_ms: int = 300) -> None:
        self.delay_ms: int = delay_ms
        self.timer: Optional[threading.Timer] = None
        
    def highlight_async(self, text: str, filepath: str, callback: Callable[[List[Tuple[Any, str]]], None]) -> None:
        """Schedule highlighting with debouncing."""
        if self.timer:
            self.timer.cancel()
        
        self.timer = threading.Timer(
            self.delay_ms / 1000.0,
            self._do_highlight,
            args=(text, filepath, callback)
        )
        self.timer.start()
    
    def _do_highlight(self, text: str, filepath: str, callback: Callable) -> None:
        """Execute highlighting in background thread."""
        def worker() -> None:
            try:
                # Usar TextLexer si no se puede determinar el lenguaje
                try:
                    lexer = get_lexer_for_filename(filepath)
                except Exception:
                    lexer = TextLexer()
                
                tokens = list(lex(text, lexer))
                callback(tokens)
            except Exception as e:
                print(f"Error en worker de resaltado: {e}")
                callback([])  # Enviar lista vacía en caso de error
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def cancel(self) -> None:
        """Cancel pending highlighting."""
        if self.timer:
            self.timer.cancel()
            self.timer = None
