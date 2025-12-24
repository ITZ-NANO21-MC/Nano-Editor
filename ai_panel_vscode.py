"""AI Assistant panel for VS Code style sidebar."""
import customtkinter as ctk


class AIAssistantPanel(ctk.CTkFrame):
    """AI Assistant panel with all AI features."""
    def __init__(self, master, app):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        self.app = app
        
        # Header (NO debe ser parte del área desplazable)
        self.header = ctk.CTkFrame(self, height=35, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        ctk.CTkLabel(
            self.header, text="AI ASSISTANT",
            font=("Segoe UI", 11, "bold"),
            text_color=("#383838", "#CCCCCC")
        ).pack(side="left", padx=10, pady=8)
        
        # Scrollable content - AHORA DENTRO DE OTRO CONTENEDOR
        self.scroll_container = ctk.CTkFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True)
        
        self.content = ctk.CTkScrollableFrame(
            self.scroll_container, 
            fg_color="transparent",
            scrollbar_button_color=("#CCCCCC", "#3E3E3E"),
            scrollbar_button_hover_color=("#BBBBBB", "#4E4E4E")
        )
        self.content.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Code Analysis Section
        self._create_section(self.content, "CODE ANALYSIS", [
            ("Explain Code", "Get explanation of selected code", app.ai_explain_code),
            ("Optimize Code", "Optimize selected code", app.ai_optimize_code),
            ("Find References", "Find symbol references", app.find_references),
        ])
        
        # Code Generation Section
        self._create_section(self.content, "CODE GENERATION", [
            ("Generate Code", "Generate code from description", app.ai_generate_code),
            ("Generate Docstring", "Add documentation", app.ai_generate_docstring),
            ("Translate Code", "Translate to another language", app.ai_translate_code),
        ])
        
        # Code Modification Section
        self._create_section(self.content, "CODE MODIFICATION", [
            ("Refactor Code", "Improve code structure", app.ai_refactor_code),
            ("Fix Errors", "Fix code errors", app.ai_fix_errors),
        ])
        
        # File Operations Section
        self._create_section(self.content, "FILE OPERATIONS", [
            ("Create File", "Create new file with AI", app.ai_create_file),
            ("Modify File", "Modify current file", app.ai_modify_current_file),
            ("Add Function", "Add function to file", app.ai_add_function),
        ])
        
        # Quick Actions
        ctk.CTkLabel(
            self.content, text="QUICK ACTIONS",
            font=("Segoe UI", 10, "bold"),
            text_color=("#666666", "#999999"),
            anchor="w"
        ).pack(fill="x", pady=(15, 5))
        
        quick_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        quick_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            quick_frame, text="💡 Explain",
            command=app.ai_explain_code,
            height=28, font=("Segoe UI", 10),
            fg_color=("#007ACC", "#007ACC"),
            hover_color=("#005A9E", "#005A9E")
        ).pack(side="left", padx=2, expand=True, fill="x")
        
        ctk.CTkButton(
            quick_frame, text="🔧 Fix",
            command=app.ai_fix_errors,
            height=28, font=("Segoe UI", 10),
            fg_color=("#007ACC", "#007ACC"),
            hover_color=("#005A9E", "#005A9E")
        ).pack(side="left", padx=2, expand=True, fill="x")
        
        # Info
        info = ctk.CTkLabel(
            self.content,
            text="💡 Select code in editor to use AI features",
            font=("Segoe UI", 9),
            text_color=("#666666", "#999999"),
            wraplength=220,
            justify="left"
        )
        info.pack(fill="x", pady=(20, 10))
        
        # SOLUCIÓN: Configurar correctamente el mousewheel
        self._setup_mousewheel_scrolling()

    def _setup_mousewheel_scrolling(self):
        """Setup proper mousewheel scrolling for the panel."""
        # Enlazar eventos al header para que también desplace
        self.header.bind("<MouseWheel>", self._forward_to_scrollable)
        self.header.bind("<Button-4>", self._forward_to_scrollable)
        self.header.bind("<Button-5>", self._forward_to_scrollable)
        
        # Enlazar eventos a todos los widgets dentro del contenido
        self._bind_mousewheel_to_widgets(self.content)

    def _bind_mousewheel_to_widgets(self, widget):
        """Recursively bind mousewheel events to all child widgets."""
        # Enlazar el widget actual
        widget.bind("<MouseWheel>", self._forward_to_scrollable)
        widget.bind("<Button-4>", self._forward_to_scrollable)
        widget.bind("<Button-5>", self._forward_to_scrollable)
        
        # Recursivamente enlazar a todos los hijos
        for child in widget.winfo_children():
            # No enlazar a CTkScrollableFrame de nuevo (para evitar bucle)
            if not isinstance(child, ctk.CTkScrollableFrame):
                self._bind_mousewheel_to_widgets(child)

    def _forward_to_scrollable(self, event):
        """Forward mousewheel event to the scrollable frame."""
        canvas = self.content._parent_canvas
        if not canvas:
            return "break"
        
        delta = 0
        if event.num == 4:  # Linux scroll up
            delta = -1
        elif event.num == 5:  # Linux scroll down
            delta = 1
        elif hasattr(event, 'delta'):  # Windows/Mac
            delta = -1 if event.delta > 0 else 1
        
        if delta != 0:
            canvas.yview_scroll(delta, "units")
        
        return "break"

    def _create_section(self, parent, title, items):
        """Create a section with title and buttons."""
        # Section title
        ctk.CTkLabel(
            parent, text=title,
            font=("Segoe UI", 10, "bold"),
            text_color=("#666666", "#999999"),
            anchor="w"
        ).pack(fill="x", pady=(15, 5))
        
        # Section items
        for label, description, command in items:
            btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
            btn_frame.pack(fill="x", pady=2)
            
            btn = ctk.CTkButton(
                btn_frame, text=label,
                command=command,
                anchor="w",
                height=32,
                font=("Segoe UI", 10),
                fg_color="transparent",
                hover_color=("#E0E0E0", "#2A2D2E"),
                border_width=1,
                border_color=("#CCCCCC", "#3E3E3E"),
                text_color=("#333333", "#CCCCCC")
            )
            btn.pack(fill="x")
            
            # Description tooltip
            desc_label = ctk.CTkLabel(
                btn_frame, text=description,
                font=("Segoe UI", 8),
                text_color=("#999999", "#666666"),
                anchor="w"
            )
            desc_label.pack(fill="x", padx=5)
