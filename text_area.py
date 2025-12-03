import customtkinter
import tkinter
import jedi
from syntax_highlighter import SyntaxHighlighter
from completion_popup import CompletionPopup
from async_highlighter import AsyncHighlighter


class CodeEditor(customtkinter.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(font=("monospace", 14))
        self.line_numbers = None
        self.highlighter = SyntaxHighlighter(self)
        self.async_highlighter = AsyncHighlighter(delay_ms=300)
        self.bind("<<Modified>>", self.on_text_changed)
        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<Control-space>", lambda event: self.get_completions())
        self.bind("<Up>", self.handle_popup_key_event)
        self.bind("<Down>", self.handle_popup_key_event)
        self.bind("<Return>", self.handle_popup_key_event)
        self.bind("<Escape>", self.handle_popup_key_event)
        self.file_path = None
        self.completion_popup = None

    def handle_popup_key_event(self, event):
        try:
            if self.completion_popup and self.completion_popup.winfo_exists():
                self.completion_popup.handle_key_event(event)
                return "break"
        except tkinter.TclError:
            self.completion_popup = None
        return None

    def on_key_release(self, event):
        try:
            if self.completion_popup and self.completion_popup.winfo_exists():
                if event.keysym not in ["Up", "Down", "Return", "Escape",
                                        "Control_L", "Control_R", "Shift_L", "Shift_R",
                                        "Alt_L", "Alt_R", "period"]:
                    try:
                        self.completion_popup.hide()
                        self.completion_popup.destroy()
                    except tkinter.TclError:
                        pass
                    finally:
                        self.completion_popup = None

            if event.keysym == 'period':
                self.get_completions()
            elif event.keysym == 'space' and event.state & 0x4:
                self.get_completions()
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

    def get_completions(self):
        try:
            code = self.get("1.0", "end-1c")
            cursor_pos = self.index(customtkinter.INSERT)
            line, col = map(int, cursor_pos.split('.'))

            script = jedi.Script(code)
            completions = script.complete(line=line, column=col)

            if self.completion_popup:
                try:
                    self.completion_popup.hide()
                    self.completion_popup.destroy()
                except tkinter.TclError:
                    pass
                finally:
                    self.completion_popup = None

            if completions:
                self.completion_popup = CompletionPopup(self.master, self, completions)
                self.completion_popup.show()

            return completions
        except (tkinter.TclError, ValueError, AttributeError):
            return []
        except Exception:
            return []

    def yview(self, *args):
        try:
            result = super().yview(*args)
            if self.line_numbers:
                self.line_numbers.redraw()
            return "break"
        except tkinter.TclError:
            return "break"
