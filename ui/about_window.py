import customtkinter as ctk

class AboutWindow(ctk.CTkToplevel):
    """Custom scrollable window for About info."""
    def __init__(self, master):
        super().__init__(master)
        self.title("Acerca de NanoEditor")
        self.geometry("450x500")
        self.after(10, self.lift) # Focus
        
        # Center window
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (450 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkLabel(self, text="NanoEditor v3.0", font=("Segoe UI", 18, "bold"))
        header.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Scrollable Text area
        self.text_box = ctk.CTkTextbox(self, font=("Segoe UI", 13), wrap="word")
        self.text_box.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        info = """NanoEditor es un editor de código moderno, ligero y potente, diseñado para la era de la IA.

Características Principales:
• Interfaz moderna basada en VS Code.
• Resaltado de sintaxis optimizado (non-blocking).
• Gestor de pestañas integrado.
• Terminal multi-lenguaje funcional.
• Inteligencia Artificial avanzada (Gemini 1.5).
• Autocompletado inteligente y Ghost Text.
• Explorador de archivos y búsqueda global.
• Soporte para múltiples lenguajes de programación.

Desarrollado con:
• Python 3.12+
• CustomTkinter (GUI)
• Google Gemini SDK
• Pygments (Sintaxis)

Versión: 3.0.0 (Pre-release)
Estado: Refactorizado y Optimizado 🚀"""

        self.text_box.insert("1.0", info)
        self.text_box.configure(state="disabled") # Read only

        # Close button
        btn = ctk.CTkButton(self, text="Cerrar", command=self.destroy, width=100)
        btn.grid(row=2, column=0, pady=(0, 20))
