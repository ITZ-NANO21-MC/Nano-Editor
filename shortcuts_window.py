import customtkinter as ctk

class ShortcutsWindow(ctk.CTkToplevel):
    """Custom scrollable window for shortcuts."""
    def __init__(self, master):
        super().__init__(master)
        self.title("Atajos de Teclado")
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
        header = ctk.CTkLabel(self, text="Atajos de Teclado", font=("Segoe UI", 16, "bold"))
        header.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Scrollable Text area
        self.text_box = ctk.CTkTextbox(self, font=("Segoe UI", 13), wrap="word")
        self.text_box.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        shortcuts = """Comandos del Editor:
        
Ctrl+N - Nueva Pestaña
Ctrl+O - Abrir Archivo
Ctrl+S - Guardar Archivo
Ctrl+W - Cerrar Pestaña
Ctrl+F - Buscar y Reemplazar
Ctrl+Shift+F - Búsqueda en Proyecto
F12 / Ctrl+Click - Ir a Definición
Ctrl+` - Alternar Terminal
Ctrl+, - Configuración

Edición:
Ctrl+A - Seleccionar Todo
Ctrl+C - Copiar
Ctrl+X - Cortar
Ctrl+V - Pegar

Asistente de IA:
Ctrl+Shift+Space - Sugerencia (Ghost Text)
Tab / Enter - Aceptar Sugerencia
Esc - Limpiar Sugerencia

Vistas (Ctrl+Shift+...):
E - Explorador
G - Git / Fuente
D - Depuración
A - Asistente IA
X - Extensiones"""

        self.text_box.insert("1.0", shortcuts)
        self.text_box.configure(state="disabled") # Read only

        # Close button
        btn = ctk.CTkButton(self, text="Cerrar", command=self.destroy, width=100)
        btn.grid(row=2, column=0, pady=(0, 20))
