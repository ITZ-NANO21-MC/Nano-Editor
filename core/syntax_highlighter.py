from pygments import lex
from pygments.lexers.special import TextLexer
from pygments import lex
from pygments.lexers.special import TextLexer
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound
import tkinter


class SyntaxHighlighter:
    def __init__(self, text_widget, style="monokai"):
        self.text_widget = text_widget
        self.max_highlight_size = 100000
        self._highlight_after_id = None
        self._batch_size = 100
        
        try:
            self.style = get_style_by_name(style)
            self.style_name = style
        except ClassNotFound:
            self.style = get_style_by_name("default")
            self.style_name = "default"
        
        print(f"[DEBUG] SyntaxHighlighter initialized with style: {self.style_name}")
        
        self.configure_tags()

    def configure_tags(self):
        """Configura etiquetas dinámicamente basadas en el estilo de Pygments."""
        try:
            from pygments.token import Token
            
            # Tipos de tokens comunes a configurar
            tokens_to_style = [
                Token.Keyword, Token.Keyword.Declaration, Token.Keyword.Namespace,
                Token.Name, Token.Name.Function, Token.Name.Class, Token.Name.Variable,
                Token.String, Token.Comment, Token.Operator, Token.Number,
                Token.Punctuation, Token.Literal, Token.Text
            ]
            
            for token in tokens_to_style:
                tag_name = str(token).replace('.', '_')
                color = self._get_style_color(token)
                
                if color:
                    try:
                        self.text_widget.tag_config(tag_name, foreground=color)
                    except tkinter.TclError:
                        pass
                        
        except Exception as e:
            print(f"[ERROR] Error configurando etiquetas: {e}")

    def _get_style_color(self, token):
        """Extrae el color hexadecimal para un token dado el estilo actual."""
        try:
            style_for_token = self.style.style_for_token(token)
            if style_for_token and 'color' in style_for_token and style_for_token['color']:
                return f"#{style_for_token['color']}"
        except Exception:
            pass
        return None

    def highlight(self, file_path, debounce=False):
        """Resalta el texto (opcionalmente con debouncing)."""
        if debounce:
            if self._highlight_after_id:
                self.text_widget.after_cancel(self._highlight_after_id)
            self._highlight_after_id = self.text_widget.after(300, lambda: self.highlight(file_path, False))
            return

        try:
            data = self.text_widget.get("1.0", "end-1c")
            if len(data) > self.max_highlight_size:
                return
            
            self.clear_highlighting()
            try:
                if file_path.endswith('.env'):
                    lexer = get_lexer_by_name('bash')
                else:
                    lexer = guess_lexer_for_filename(file_path, data)
            except ClassNotFound:
                lexer = TextLexer()
            
            self.apply_lexing(data, lexer)
        except Exception as e:
            print(f"Error en highlight: {e}")


    def apply_lexing(self, text, lexer):
        """Aplica el lexing al texto con optimización de fusión de tokens."""
        try:
            self.text_widget.mark_set("range_start", "1.0")
            
            # Agrupar tokens consecutivos del mismo tipo para reducir llamadas a tag_add
            merged_tokens = []
            if not text: return
            
            gen = lex(text, lexer)
            try:
                curr_token, curr_content = next(gen)
                for next_token, next_content in gen:
                    if next_token == curr_token:
                        curr_content += next_content
                    else:
                        merged_tokens.append((curr_token, curr_content))
                        curr_token, curr_content = next_token, next_content
                merged_tokens.append((curr_token, curr_content))
            except StopIteration:
                pass

            for token, content in merged_tokens:
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
            print(f"Error en apply_lexing: {e}")

    def clear_highlighting(self):
        """Elimina todas las etiquetas de resaltado."""
        try:
            for tag in self.text_widget.tag_names():
                if tag not in ['sel', 'ghost']:  # No eliminar selección ni texto fantasma
                    self.text_widget.tag_remove(tag, "1.0", "end")
        except tkinter.TclError:
            pass

    def apply_tokens(self, tokens, callback=None):
        """Aplica tokens precomputados de forma no bloqueante (en trozos)."""
        try:
            self.clear_highlighting()
            self.text_widget.mark_set("range_start", "1.0")
            
            # Procesar en trozos para no bloquear el hilo principal
            self._process_token_chunk(iter(tokens), callback)
        except Exception as e:
            print(f"Error en apply_tokens: {e}")

    def _process_token_chunk(self, token_iter, callback=None):
        """Procesa un trozo de tokens y programa el siguiente."""
        try:
            count = 0
            for token, content in token_iter:
                if not content: continue
                
                try:
                    self.text_widget.mark_set("range_end", f"range_start + {len(content)}c")
                    tag_name = str(token).replace('.', '_')
                    
                    if tag_name in self.text_widget.tag_names():
                        self.text_widget.tag_add(tag_name, "range_start", "range_end")
                    
                    self.text_widget.mark_set("range_start", "range_end")
                except tkinter.TclError:
                    return

                count += 1
                if count >= self._batch_size:
                    # Programar el siguiente trozo
                    self.text_widget.after(1, lambda: self._process_token_chunk(token_iter, callback))
                    return
            
            # Finalizado con éxito
            if callback:
                callback()
        except Exception as e:
            print(f"Error en _process_token_chunk: {e}")
