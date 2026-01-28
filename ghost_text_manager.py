import tkinter
import customtkinter
from ai_completion import completion_engine
from logger import logger

class GhostTextManager:
    """
    Manages AI Ghost Text suggestions in the editor.
    Handles requesting, displaying, clearing, and accepting suggestions.
    """
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.active = False
        self.typing_timer = None
        self._request_pos = None
        
        # Configure tag
        try:
            self.text_widget.tag_config("ghost", foreground="gray50")
        except AttributeError:
            if hasattr(self.text_widget, "_textbox"):
                self.text_widget._textbox.tag_config("ghost", foreground="gray50")

    def schedule_request(self, delay_ms=1500):
        """Schedule a completion request after a pause in typing."""
        self.cancel_timer()
        self.typing_timer = self.text_widget.after(delay_ms, self._on_typing_pause)

    def cancel_timer(self):
        """Cancel any pending completion request."""
        if self.typing_timer:
            self.text_widget.after_cancel(self.typing_timer)
            self.typing_timer = None

    def _on_typing_pause(self):
        """Called when user stops typing. Requests completion."""
        # Don't request if already active or popup is open
        if self.active or (hasattr(self.text_widget, 'completion_popup') and self.text_widget.completion_popup):
            return
            
        try:
            code = self.text_widget.get("1.0", "end-1c")
            cursor_pos = self.text_widget.index(customtkinter.INSERT)
            self._request_pos = cursor_pos
            line, col = map(int, cursor_pos.split('.'))
            
            # Request completion
            completion_engine.request_completion(
                code=code,
                cursor_line=line,
                cursor_col=col,
                file_path=self.text_widget.file_path,
                callback=self._handle_completion
            )
        except Exception:
            pass

    def _handle_completion(self, suggestions):
        """Callback for completion engine."""
        if not suggestions:
            return
            
        # Take the best suggestion
        best_suggestion = suggestions[0]
        # Schedule display on main thread
        self.text_widget.after(0, lambda: self.show(best_suggestion.text))

    def show(self, text):
        """Display ghost text at current cursor position."""
        if self.active or not text:
            return
            
        # Verify cursor hasn't moved since request
        if self._request_pos and self.text_widget.index(customtkinter.INSERT) != self._request_pos:
            return

        try:
            # Insert text
            self.text_widget.insert(customtkinter.INSERT, text)
            
            logger.info(f"Showing ghost text: '{text[:20]}...'")
            
            # Apply ghost tag
            start_index = f"{customtkinter.INSERT}-{len(text)}c"
            end_index = customtkinter.INSERT
            self.text_widget.tag_add("ghost", start_index, end_index)
            self.text_widget.tag_raise("ghost")
            
            self.active = True
            
            # Position cursor back to start
            self.text_widget.mark_set(customtkinter.INSERT, start_index)
        except Exception as e:
            logger.error(f"Error showing ghost text: {e}")

    def clear(self):
        """Remove ghost text."""
        if not self.active:
            return
            
        logger.info("Clearing ghost text")
        try:
            self.text_widget.delete("ghost.first", "ghost.last")
            self.active = False
        except tkinter.TclError:
            self.active = False

    def accept(self):
        """Accept ghost text (convert to real text)."""
        if not self.active:
            return
            
        logger.info("Accepting ghost text")
        try:
            text = self.text_widget.get("ghost.first", "ghost.last")
            self.text_widget.tag_remove("ghost", "ghost.first", "ghost.last")
            self.active = False
            
            # Move cursor to end
            self.text_widget.mark_set(customtkinter.INSERT, f"{customtkinter.INSERT}+{len(text)}c")
            self.text_widget.see(customtkinter.INSERT)
        except tkinter.TclError:
            self.active = False
