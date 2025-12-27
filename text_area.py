import customtkinter
import tkinter
import jedi
from syntax_highlighter import SyntaxHighlighter
from completion_popup import CompletionPopup
from async_highlighter import AsyncHighlighter
from ai_completion import completion_engine
from ai_completion_popup import AICompletionPopup
from logger import logger


class CodeEditor(customtkinter.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(font=("monospace", 14))
        self.line_numbers = None
        self.highlighter = SyntaxHighlighter(self)
        self.async_highlighter = AsyncHighlighter(delay_ms=300)
        self.bind("<<Modified>>", self.on_text_changed)
        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<Control-space>", lambda event: self.show_completions())
        self.bind("<Control-l>", lambda event: self.show_ai_completions())
        self.bind("<Up>", self._on_completion_up)
        self.bind("<Down>", self._on_completion_down)
        self.bind("<Return>", self._on_completion_select)
        self.bind("<Tab>", self._on_completion_select)
        self.bind("<Escape>", self._on_completion_hide)
        
        # Vincular eventos de scroll del mouse y configuración
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.bind("<Button-5>", self._on_mousewheel)  # Linux scroll down
        self.bind("<Configure>", self._on_configure)
        
        # Vincular al frame principal para capturar eventos cuando el mouse está sobre números de línea
        if self.master:
            self.master.bind("<MouseWheel>", self._forward_mousewheel)
            self.master.bind("<Button-4>", self._forward_mousewheel)
            self.master.bind("<Button-5>", self._forward_mousewheel)
        
        self.file_path = None
        self.completion_popup = None
        
        # Configurar sincronización de barra de desplazamiento
        self.after(200, self._configure_scrollbar_sync)

    def _configure_scrollbar_sync(self):
        """Configure the internal scrollbar to sync with line numbers."""
        # CTkTextbox tiene un atributo _scrollbar interno
        if hasattr(self, '_scrollbar') and self._scrollbar:
            # Guardar el comando original (que mueve el texto)
            self._original_scrollbar_command = self._scrollbar.cget("command")
            # Reemplazar con nuestro comando que mueve ambos
            self._scrollbar.configure(command=self._on_scrollbar_scroll)
        else:
            # Reintentar si el widget aún no está totalmente listo
            self.after(100, self._try_find_scrollbar)

    def _try_find_scrollbar(self):
        """Try to find the scrollbar widget among children."""
        for child in self.winfo_children():
            if "scrollbar" in str(child).lower():
                self._original_scrollbar_command = child.cget("command")
                child.configure(command=self._on_scrollbar_scroll)
                break

    def _on_scrollbar_scroll(self, *args):
        """Handle scrollbar movement to sync line numbers."""
        # Llamar al comando original para mover el texto
        if hasattr(self, '_original_scrollbar_command') and self._original_scrollbar_command:
            self._original_scrollbar_command(*args)
        
        # Sincronizar números de línea inmediatamente
        self._sync_line_numbers()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling with line number sync."""
        try:
            scroll_delta = 0
            if event.num == 4: scroll_delta = -1
            elif event.num == 5: scroll_delta = 1
            elif hasattr(event, 'delta'):
                scroll_delta = -1 if event.delta > 0 else 1
            
            if scroll_delta != 0:
                self.yview_scroll(scroll_delta, "units")
                self._sync_line_numbers()
            return "break"
        except Exception:
            return "break"

    def _forward_mousewheel(self, event):
        """Forward mouse wheel events from parent widget."""
        self._on_mousewheel(event)
        return "break"

    def _on_configure(self, event):
        """Redraw line numbers when widget is resized."""
        if self.line_numbers:
            self.line_numbers.redraw()
            self._sync_line_numbers()

    def _sync_line_numbers(self):
        """Sync line numbers position with text widget."""
        if self.line_numbers:
            try:
                # Obtener la vista vertical del widget de texto (interno)
                # CTkTextbox.yview() devuelve (start, end)
                y_pos = self.yview()
                if y_pos:
                    # Mover los números de línea a la misma posición fraccional
                    self.line_numbers.yview_moveto(y_pos[0])
                    # Forzar redibujado
                    self.line_numbers.redraw()
            except tkinter.TclError:
                pass

    def yview(self, *args):
        """Override yview to synchronize with line numbers."""
        try:
            result = super().yview(*args)
            
            if self.line_numbers:
                if args:
                    # Si hay argumentos, estamos moviendo la vista
                    self.line_numbers.yview(*args)
                else:
                    # Si no hay argumentos, es una consulta de posición.
                    # Aprovechamos para sincronizar.
                    self._sync_line_numbers()
            
            return result
        except (tkinter.TclError, AttributeError):
            return (0.0, 1.0)


    def _on_completion_up(self, event):
        if self.completion_popup:
            self.completion_popup.move_selection(-1)
            return "break"

    def _on_completion_down(self, event):
        if self.completion_popup:
            self.completion_popup.move_selection(1)
            return "break"

    def _on_completion_select(self, event):
        if self.completion_popup:
            self.completion_popup.confirm_selection()
            self.completion_popup = None
            return "break"

    def _on_completion_hide(self, event):
        if self.completion_popup:
            self.completion_popup.hide()
            self.completion_popup = None
            return "break"

    def on_key_release(self, event):
        try:
            # Hide popup on most keys, but not navigation/selection keys
            if self.completion_popup:
                if event.keysym not in ("Up", "Down", "Return", "Tab", "Escape",
                                        "Control_L", "Control_R", "Shift_L", "Shift_R",
                                        "Alt_L", "Alt_R"):
                    self.completion_popup.hide()
                    self.completion_popup = None

            # Trigger completions automatically
            if event.keysym == 'period':
                self.show_completions()
            elif event.keysym == 'space' and event.state & 0x4: # Ctrl+Space
                self.show_completions()
        except Exception:
            pass

    def set_line_numbers(self, line_numbers):
        self.line_numbers = line_numbers

    def on_text_changed(self, *args):
        try:
            if self.line_numbers:
                self.line_numbers.redraw()

            if self.edit_modified():
                self.highlight_text_async()
                self.edit_modified(False)
        except tkinter.TclError:
            pass

    def highlight_text(self, *args):
        if self.file_path:
            self.highlighter.highlight(self.file_path)
    
    def highlight_text_async(self):
        """Async highlighting with debouncing."""
        if not self.file_path:
            return
        
        text = self.get("1.0", "end-1c")
        self.async_highlighter.highlight_async(
            text,
            self.file_path,
            self._apply_highlighting
        )
    
    def _apply_highlighting(self, tokens):
        """Apply highlighting tokens in main thread."""
        self.after(0, lambda: self.highlighter.apply_tokens(tokens))

    def show_completions(self, event=None):
        """Get and show completions from Jedi."""
        try:
            if self.completion_popup:
                self.completion_popup.hide()
                self.completion_popup = None

            code = self.get("1.0", "end-1c")
            cursor_pos = self.index(customtkinter.INSERT)
            line, col = map(int, cursor_pos.split('.'))

            script = jedi.Script(code, path=self.file_path or "temp.py")
            completions = script.complete(line=line, column=col)

            if completions:
                self.completion_popup = CompletionPopup(self.master, self, completions)
                self.completion_popup.show()

        except (tkinter.TclError, ValueError, AttributeError):
            pass # Silently fail
        except Exception:
            pass # Silently fail on other errors

    def show_ai_completions(self, event=None):
        """Request AI completions and display them in a popup."""
        try:
            logger.info("AI Completion requested via shortcut")
            # Get current code and cursor position
            code = self.get("1.0", "end-1c")
            cursor_pos = self.index(customtkinter.INSERT)
            line, col = map(int, cursor_pos.split('.'))

            # Callback to handle suggestions
            def _callback(suggestions):
                logger.info(f"AI Completion callback received {len(suggestions)} suggestions")
                def _show():
                    # Compute screen coordinates for popup
                    bbox = self.bbox(customtkinter.INSERT)
                    if not bbox:
                        return
                    x = self.winfo_rootx() + bbox[0]
                    y = self.winfo_rooty() + bbox[1] + bbox[3]
                    
                    # Create popup and show it
                    # Note: We pass a simple insert callback. 
                    # Advanced replacement logic could be added here if needed.
                    popup = AICompletionPopup(
                        self.master, 
                        self, 
                        lambda txt: self.insert(customtkinter.INSERT, txt)
                    )
                    popup.show(suggestions, x, y)
                
                # Ensure UI updates happen in main thread
                self.after(0, _show)

            # Request completion from engine (asynchronous)
            completion_engine.request_completion(
                code=code,
                cursor_line=line,
                cursor_col=col,
                file_path=self.file_path,
                callback=_callback,
            )
        except Exception:
            pass  # Silently ignore errors

    def yview(self, *args):
        """Override yview to synchronize with line numbers."""
        try:
            # Mover el texto primero
            result = super().yview(*args)
            
            # Sincronizar números de línea DINÁMICAMENTE
            if self.line_numbers and args:
                # Calcular posición actual para sincronización precisa
                if len(args) >= 2 and args[0] == 'moveto':
                    # Movimiento absoluto
                    self.line_numbers.yview_moveto(args[1])
                elif len(args) >= 2 and args[0] == 'scroll':
                    # Desplazamiento relativo
                    units = int(args[1])
                    what = args[2] if len(args) > 2 else "units"
                    self.line_numbers.yview_scroll(units, what)
                
                # Forzar redibujado inmediato
                self.line_numbers.redraw()
            
            return result
        except tkinter.TclError:
            return (0.0, 1.0)

    def yview_scroll(self, number, what):
        """Override yview_scroll for better synchronization."""
        try:
            super().yview_scroll(number, what)
            # Actualizar números de línea inmediatamente después del scroll
            if self.line_numbers:
                self.after(10, self._sync_line_numbers)
        except tkinter.TclError:
            pass

