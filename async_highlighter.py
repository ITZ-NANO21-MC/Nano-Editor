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
                from pygments.lexers import get_lexer_by_name
                # Use BashLexer for .env files
                if filepath.endswith('.env'):
                    lexer = get_lexer_by_name('bash')
                else:
                    try:
                        lexer = get_lexer_for_filename(filepath, text)
                    except Exception:
                        lexer = TextLexer()
                
                # Lex and merge consecutive tokens of the same type
                tokens = []
                gen = lex(text, lexer)
                try:
                    curr_token, curr_content = next(gen)
                    for next_token, next_content in gen:
                        if next_token == curr_token:
                            curr_content += next_content
                        else:
                            tokens.append((curr_token, curr_content))
                            curr_token, curr_content = next_token, next_content
                    tokens.append((curr_token, curr_content))
                except StopIteration:
                    pass

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
