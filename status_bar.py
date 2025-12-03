import customtkinter
import tkinter
import os


class StatusBar(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.max_path_length = 80

        self.file_path_label = customtkinter.CTkLabel(self, text="")
        self.file_path_label.pack(side="left", padx=10)

        self.line_col_label = customtkinter.CTkLabel(self, text="Ln 1, Col 1")
        self.line_col_label.pack(side="right", padx=10)

    def set_file_path(self, path):
        if path is None:
            path = ""
        
        try:
            display_path = self._truncate_path(str(path))
            self.file_path_label.configure(text=display_path)
        except tkinter.TclError:
            pass
    
    def _truncate_path(self, path):
        """Truncate long paths for display."""
        if len(path) <= self.max_path_length:
            return path
        
        # Try to show filename and parent directory
        try:
            filename = os.path.basename(path)
            dirname = os.path.dirname(path)
            
            if len(filename) > self.max_path_length - 10:
                return f"...{filename[-(self.max_path_length-3):]}"
            
            available = self.max_path_length - len(filename) - 4
            if len(dirname) > available:
                dirname = dirname[:available]
            
            return f"{dirname}/.../{filename}"
        except Exception:
            return f"...{path[-(self.max_path_length-3):]}"

    def set_line_col(self, line, col):
        try:
            line_num = int(line) if line is not None else 1
            col_num = int(col) if col is not None else 1
            
            line_num = max(1, line_num)
            col_num = max(1, col_num)
            
            self.line_col_label.configure(text=f"Ln {line_num}, Col {col_num}")
        except (ValueError, TypeError):
            self.line_col_label.configure(text="Ln 1, Col 1")
        except tkinter.TclError:
            pass
