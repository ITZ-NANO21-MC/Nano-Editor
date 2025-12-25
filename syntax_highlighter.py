from pygments import lex
from pygments.lexers import guess_lexer_for_filename, TextLexer
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound
import tkinter
import re


class SyntaxHighlighter:
    def __init__(self, text_widget, style="monokai"):
        self.text_widget = text_widget
        self.max_highlight_size = 100000
        
        try:
            self.style = get_style_by_name(style)
            self.style_name = style
        except ClassNotFound:
            self.style = get_style_by_name("default")
            self.style_name = "default"
        
        # Mapeo básico de colores para empezar
        self.token_colors = {
            'Token.Keyword': '#ff79c6',
            'Token.Name': '#50fa7b',
            'Token.String': '#f1fa8c',
            'Token.Comment': '#6272a4',
            'Token.Operator': '#ff79c6',
            'Token.Number': '#bd93f9',
            'Token.Punctuation': '#f8f8f2',
        }
        
        self.configure_tags()

    def configure_tags(self):
        """Configura etiquetas básicas para resaltado."""
        try:
            # Configurar etiquetas con colores básicos
            for token_type, color in self.token_colors.items():
                tag_name = token_type.replace('.', '_')
                try:
                    self.text_widget.tag_config(
                        tag_name,
                        foreground=color
                    )
                except tkinter.TclError:
                    pass
                    
        except Exception as e:
            print(f"Error configurando etiquetas: {e}")

    def highlight(self, file_path):
        """Resalta el texto sincrónicamente."""
        try:
            data = self.text_widget.get("1.0", "end-1c")
            
            if len(data) > self.max_highlight_size:
                return
            
            # Limpiar etiquetas anteriores
            self.clear_highlighting()
            
            try:
                lexer = guess_lexer_for_filename(file_path, data)
            except ClassNotFound:
                lexer = TextLexer()
            
            self.apply_lexing(data, lexer)
                    
        except Exception as e:
            print(f"Error en highlight: {e}")

    def apply_lexing(self, text, lexer):
        """Aplica el lexing al texto."""
        try:
            self.text_widget.mark_set("range_start", "1.0")
            
            for token, content in lex(text, lexer):
                if not content:
                    continue
                
                try:
                    self.text_widget.mark_set("range_end", f"range_start + {len(content)}c")
                    
                    # Convertir tipo de token a nombre de etiqueta
                    token_type = str(token)
                    tag_name = token_type.replace('.', '_')
                    
                    # Solo aplicar si tenemos esa etiqueta configurada
                    if tag_name in self.text_widget.tag_names():
                        self.text_widget.tag_add(tag_name, "range_start", "range_end")
                    
                    self.text_widget.mark_set("range_start", "range_end")
                except tkinter.TclError:
                    break
                    
        except Exception as e:
            print(f"Error en apply_lexing: {e}")

    def clear_highlighting(self):
        """Elimina todas las etiquetas de resaltado."""
        try:
            for tag in self.text_widget.tag_names():
                if tag not in ['sel']:  # No eliminar selección
                    self.text_widget.tag_remove(tag, "1.0", "end")
        except tkinter.TclError:
            pass

    def apply_tokens(self, tokens):
        """Aplica tokens precomputados."""
        try:
            self.clear_highlighting()
            self.text_widget.mark_set("range_start", "1.0")
            
            for token, content in tokens:
                if not content:
                    continue
                
                try:
                    self.text_widget.mark_set("range_end", f"range_start + {len(content)}c")
                    tag_name = str(token).replace('.', '_')
                    
                    if tag_name in self.text_widget.tag_names():
                        self.text_widget.tag_add(tag_name, "range_start", "range_end")
                    
                    self.text_widget.mark_set("range_start", "range_end")
                except tkinter.TclError:
                    break
        except Exception as e:
            print(f"Error en apply_tokens: {e}")
