import customtkinter
import tkinter


class LineNumbers(customtkinter.CTkCanvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.configure(width=40)
        self.font = kwargs.get("font", ("monospace", 14))
        self.text_color = "gray"
        self.bind("<Configure>", lambda e: self.redraw())
    
    def yview_moveto(self, fraction):
        """Redraw line numbers at the specified vertical position."""
        try:
            # Force redraw to align with text widget's new position
            self.redraw()
        except Exception:
            pass

    def yview(self, *args):
        """Handle scroll and redraw."""
        try:
            if args:
                # If we're using a real scrollable canvas (rare for line numbers)
                if hasattr(super(), 'yview'):
                    super().yview(*args)
            self.redraw()
        except (tkinter.TclError, AttributeError):
            pass

    def sync_with_text_widget(self):
        """Sync position with text widget's current view."""
        try:
            # Get text position and force redraw
            if self.text_widget:
                self.redraw()
        except Exception:
            pass
    
    def redraw(self, *args):
        """Redraw line numbers dynamically with visible range calculation."""
        if not self.text_widget:
            return
            
        self.delete("all")
        try:
            # Obtener primera línea visible usando dlineinfo
            first_dline = self.text_widget.dlineinfo("@0,0")
            if not first_dline:
                return
            
            # Calcular cuántas líneas caben en la ventana visible
            line_height = first_dline[3]
            visible_height = self.text_widget.winfo_height()
            
            if line_height > 0:
                lines_visible = int(visible_height / line_height) + 2
            else:
                lines_visible = 20  # Valor por defecto
            
            # Obtener número de línea de la primera visible
            first_index = self.text_widget.index("@0,0")
            first_line = int(first_index.split('.')[0])
            
            # Dibujar desde 2 líneas antes hasta 2 líneas después del área visible
            start_line = max(1, first_line - 2)
            end_line = first_line + lines_visible + 2
            
            for line_num in range(start_line, end_line + 1):
                dline = self.text_widget.dlineinfo(f"{line_num}.0")
                if dline:
                    y = dline[1] + line_height / 2  # Centrar verticalmente
                    self.create_text(
                        38, y,
                        anchor="ne",
                        text=str(line_num),
                        fill=self.text_color,
                        font=self.font,
                        tags=f"line_{line_num}"
                    )
        except (tkinter.TclError, ValueError, ZeroDivisionError):
            pass
