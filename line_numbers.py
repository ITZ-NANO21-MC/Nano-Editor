import customtkinter
import tkinter


class LineNumbers(customtkinter.CTkCanvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.configure(width=40)
        self.bind("<MouseWheel>", self.on_scroll)

    def on_scroll(self, event):
        if not self.text_widget:
            return
        
        try:
            delta = getattr(event, 'delta', 0)
            if delta != 0:
                scroll_amount = -1 * int(delta / 120)
                self.text_widget.yview_scroll(scroll_amount, "units")
                self.redraw()
        except (tkinter.TclError, AttributeError, ZeroDivisionError):
            pass

    def redraw(self, *args):
        if not self.text_widget:
            return
        
        try:
            self.delete("all")
            self.text_widget.update_idletasks()
            
            i = self.text_widget.index("@0,0")
            max_iterations = 1000  # Prevent infinite loop
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                dline = self.text_widget.dlineinfo(i)
                if dline is None:
                    break
                
                try:
                    y = dline[1]
                    linenum = str(i).split(".")[0]
                    self.create_text(38, y, anchor="ne", text=linenum, fill="gray")
                    i = self.text_widget.index(f"{i}+1line")
                except (IndexError, ValueError, tkinter.TclError):
                    break
                    
        except (tkinter.TclError, AttributeError):
            pass
