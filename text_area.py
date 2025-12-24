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
        self.bind("<Control-space>", lambda event: self.show_completions())
        self.bind("<Up>", self._on_completion_up)
        self.bind("<Down>", self._on_completion_down)
        self.bind("<Return>", self._on_completion_select)
        self.bind("<Tab>", self._on_completion_select)
        self.bind("<Escape>", self._on_completion_hide)
        self.file_path = None
        self.completion_popup = None

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

    def show_completions(self):
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

    def yview(self, *args):
        try:
            result = super().yview(*args)
            if self.line_numbers:
                self.line_numbers.redraw()
            return "break"
        except tkinter.TclError:
            return "break"
