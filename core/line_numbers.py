import customtkinter
import tkinter


class LineNumbers(customtkinter.CTkCanvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.configure(width=50)
        self.font = kwargs.get("font", ("monospace", 14))
        self.text_color = "gray"
        self.breakpoint_manager = None
        self._current_file = None
        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<Button-1>", self._on_gutter_click)
    
    def set_breakpoint_manager(self, bp_manager, file_path=None):
        """Connect a BreakpointManager and optionally set current file."""
        self.breakpoint_manager = bp_manager
        self._current_file = file_path
    
    def set_current_file(self, file_path):
        """Update the current file path for breakpoint tracking."""
        self._current_file = file_path
        self.redraw()

    def _on_gutter_click(self, event):
        """Toggle breakpoint when clicking on the line number gutter."""
        if not self.breakpoint_manager or not self._current_file:
            return
        
        try:
            # Determine which line was clicked based on y coordinate
            # Use the text widget's coordinate system
            index = self.text_widget.index(f"@0,{event.y}")
            line = int(index.split('.')[0])
            self.breakpoint_manager.toggle_breakpoint(self._current_file, line)
            self.redraw()
        except (tkinter.TclError, ValueError):
            pass

    def yview_moveto(self, fraction):
        """Redraw line numbers at the specified vertical position."""
        try:
            self.redraw()
        except Exception:
            pass

    def yview(self, *args):
        """Handle scroll and redraw."""
        try:
            if args:
                if hasattr(super(), 'yview'):
                    super().yview(*args)
            self.redraw()
        except (tkinter.TclError, AttributeError):
            pass

    def sync_with_text_widget(self):
        """Sync position with text widget's current view."""
        try:
            if self.text_widget:
                self.redraw()
        except Exception:
            pass
    
    def redraw(self, *args):
        """Redraw line numbers and breakpoint indicators."""
        if not self.text_widget:
            return
            
        self.delete("all")
        try:
            first_dline = self.text_widget.dlineinfo("@0,0")
            if not first_dline:
                return
            
            line_height = first_dline[3]
            visible_height = self.text_widget.winfo_height()
            
            if line_height > 0:
                lines_visible = int(visible_height / line_height) + 2
            else:
                lines_visible = 20

            first_index = self.text_widget.index("@0,0")
            first_line = int(first_index.split('.')[0])
            
            start_line = max(1, first_line - 2)
            end_line = first_line + lines_visible + 2

            # Get breakpoints for current file
            bp_lines = set()
            if self.breakpoint_manager and self._current_file:
                bp_lines = set(self.breakpoint_manager.get_breakpoints(self._current_file))
            
            for line_num in range(start_line, end_line + 1):
                dline = self.text_widget.dlineinfo(f"{line_num}.0")
                if dline:
                    y = dline[1] + line_height / 2
                    
                    # Draw breakpoint dot if active
                    if line_num in bp_lines:
                        self.create_oval(
                            3, y - 5, 13, y + 5,
                            fill="#E51400", outline="#E51400",
                            tags=f"bp_{line_num}"
                        )
                    
                    # Draw line number (shifted right to make room for dots)
                    self.create_text(
                        46, y,
                        anchor="ne",
                        text=str(line_num),
                        fill=self.text_color,
                        font=self.font,
                        tags=f"line_{line_num}"
                    )
        except (tkinter.TclError, ValueError, ZeroDivisionError):
            pass

