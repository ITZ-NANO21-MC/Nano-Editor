import customtkinter as ctk
import os

class ReferencesWindow(ctk.CTkToplevel):
    """Custom window for symbol references."""
    def __init__(self, master, references):
        super().__init__(master)
        self.title("Referencias de Símbolo")
        self.geometry("600x450")
        self.after(10, self.lift) # Focus
        
        # Center window
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (600 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (450 // 2)
        self.geometry(f"+{x}+{y}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        count = len(references)
        header_text = f"Se encontraron {count} referencias" if count > 1 else "Se encontró 1 referencia"
        header = ctk.CTkLabel(self, text=header_text, font=("Segoe UI", 16, "bold"))
        header.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Scrollable list
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        
        for ref in references:
            # Handle potential None module_path (current file)
            if ref.module_path:
                filename = os.path.basename(str(ref.module_path))
                full_path = str(ref.module_path)
            else:
                filename = "Current File"
                # Try to get current file path from app if possible, or leave as None
                # If None, opened file logic needs to handle it (or we just jump to line in current tab)
                full_path = None
            
            # Format: filename:line - content
            display_text = f"{filename}:{ref.line} - {ref.name}"
            
            ref_btn = ctk.CTkButton(
                self.scroll_frame,
                text=display_text,
                command=lambda p=full_path, l=ref.line: self._on_click(p, l),
                anchor="w",
                font=("Segoe UI", 12),
                fg_color="transparent",
                text_color=("#333333", "#CCCCCC"),
                hover_color=("#E0E0E0", "#3D3D3D")
            )
            ref_btn.pack(fill="x", pady=2)

        # Footer / Close button
        btn = ctk.CTkButton(self, text="Cerrar", command=self.destroy, width=100)
        btn.grid(row=2, column=0, pady=(10, 20))

    def _on_click(self, file_path, line):
        """Handle clicking a reference."""
        if file_path:
            self.master.open_file_at_line(file_path, line)
        else:
            # If no file path, it's the current file, just jump
            self.master.goto_def.jump_to_line(line)
            
        # We don't necessarily want to close the window, 
        # but let's close it to focus on the code.
        self.destroy()
