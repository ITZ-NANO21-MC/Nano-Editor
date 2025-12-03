from pygments import lex
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound
import tkinter
import re


class SyntaxHighlighter:
    def __init__(self, text_widget, style="monokai"):
        self.text_widget = text_widget
        self.max_highlight_size = 100000  # 100KB limit
        
        try:
            self.style = get_style_by_name(style)
        except ClassNotFound:
            self.style = get_style_by_name("default")
        
        self.configure_tags()

    def configure_tags(self):
        try:
            for token, style in self.style:
                if not isinstance(style, dict):
                    continue
                
                color = style.get('color')
                if color and self._is_valid_color(color):
                    try:
                        self.text_widget.tag_config(
                            str(token), 
                            foreground=f"#{color}"
                        )
                    except tkinter.TclError:
                        continue
        except (TypeError, AttributeError):
            pass
    
    def _is_valid_color(self, color):
        if not color:
            return False
        return bool(re.match(r'^[0-9A-Fa-f]{6}$', str(color)))

    def highlight(self, file_path):
        try:
            data = self.text_widget.get("1.0", "end-1c")
            
            if len(data) > self.max_highlight_size:
                return
            
            try:
                lexer = guess_lexer_for_filename(file_path, data)
            except ClassNotFound:
                return
            except (ValueError, TypeError):
                return
            
            self.text_widget.mark_set("range_start", "1.0")
            
            for token, content in lex(data, lexer):
                if not content:
                    continue
                
                try:
                    self.text_widget.mark_set("range_end", f"range_start + {len(content)}c")
                    self.text_widget.tag_add(str(token), "range_start", "range_end")
                    self.text_widget.mark_set("range_start", "range_end")
                except tkinter.TclError:
                    break
                    
        except tkinter.TclError:
            pass
        except Exception:
            pass
    
    def apply_tokens(self, tokens):
        """Apply pre-computed tokens from async highlighting."""
        try:
            self.text_widget.mark_set("range_start", "1.0")
            
            for token, content in tokens:
                if not content:
                    continue
                
                try:
                    self.text_widget.mark_set("range_end", f"range_start + {len(content)}c")
                    self.text_widget.tag_add(str(token), "range_start", "range_end")
                    self.text_widget.mark_set("range_start", "range_end")
                except tkinter.TclError:
                    break
        except (tkinter.TclError, Exception):
            pass
