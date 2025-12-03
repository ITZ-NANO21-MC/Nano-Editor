"""VS Code style sidebar with activity bar."""
import customtkinter as ctk


class VSCodeSidebar(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, width=48, fg_color=("#E5E5E5", "#333333"), corner_radius=0)
        self.pack_propagate(False)
        self.app = app
        self.current_view = "explorer"
        
        # Activity buttons
        self.buttons = {}
        
        activities = [
            ("📁", "explorer", "Explorer (Ctrl+Shift+E)"),
            ("🔍", "search", "Search (Ctrl+Shift+F)"),
            ("🔀", "source", "Source Control (Ctrl+Shift+G)"),
            ("▶", "run", "Run and Debug (Ctrl+Shift+D)"),
            ("🤖", "ai", "AI Assistant (Ctrl+Shift+A)"),
            ("⚙", "extensions", "Extensions (Ctrl+Shift+X)"),
        ]
        
        # Top buttons
        for icon, view, tooltip in activities:
            btn = ctk.CTkButton(
                self, text=icon, width=48, height=48,
                fg_color="transparent",
                hover_color=("#D0D0D0", "#2A2A2A"),
                text_color=("#333333", "#CCCCCC"),
                corner_radius=0,
                font=("Segoe UI", 20),
                command=lambda v=view: self.switch_view(v)
            )
            btn.pack(side="top")
            self.buttons[view] = btn
            
            # Tooltip (simplified)
            self._create_tooltip(btn, tooltip)
        
        # Spacer
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(side="top", expand=True, fill="both")
        
        # Bottom buttons
        bottom_activities = [
            ("👤", "account", "Account"),
            ("⚙️", "settings", "Settings (Ctrl+,)"),
        ]
        
        for icon, view, tooltip in bottom_activities:
            btn = ctk.CTkButton(
                self, text=icon, width=48, height=48,
                fg_color="transparent",
                hover_color=("#D0D0D0", "#2A2A2A"),
                text_color=("#333333", "#CCCCCC"),
                corner_radius=0,
                font=("Segoe UI", 18),
                command=lambda v=view: self.switch_view(v)
            )
            btn.pack(side="bottom")
            self.buttons[view] = btn
            self._create_tooltip(btn, tooltip)
        
        # Set initial active
        self.set_active("explorer")
    
    def _create_tooltip(self, widget, text):
        """Simple tooltip on hover."""
        def on_enter(e):
            widget.configure(text_color=("#000000", "#FFFFFF"))
        
        def on_leave(e):
            widget.configure(text_color=("#333333", "#CCCCCC"))
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def switch_view(self, view):
        """Switch between different views."""
        self.current_view = view
        self.set_active(view)
        
        # Handle view switching
        if view == "explorer":
            self.app.show_explorer()
        elif view == "search":
            self.app.show_search()
        elif view == "source":
            self.app.show_source_control()
        elif view == "run":
            self.app.show_run_debug()
        elif view == "ai":
            self.app.show_ai_assistant()
        elif view == "extensions":
            self.app.show_extensions()
        elif view == "settings":
            self.app.show_settings()
        elif view == "account":
            self.app.show_account()
    
    def set_active(self, view):
        """Set active button highlight."""
        for v, btn in self.buttons.items():
            if v == view:
                btn.configure(
                    fg_color=("#FFFFFF", "#1E1E1E"),
                    border_width=2,
                    border_color=("#007ACC", "#007ACC"),
                    text_color=("#007ACC", "#FFFFFF")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    border_width=0,
                    text_color=("#333333", "#CCCCCC")
                )


class SearchPanel(ctk.CTkFrame):
    """Search panel for project-wide search."""
    def __init__(self, master, app):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        self.app = app
        
        # Header
        header = ctk.CTkFrame(self, height=35, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="SEARCH",
            font=("Segoe UI", 11, "bold"),
            text_color=("#383838", "#CCCCCC")
        ).pack(side="left", padx=10, pady=8)
        
        # Search input
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Search",
            height=30, font=("Segoe UI", 11)
        )
        self.search_entry.pack(fill="x", pady=5)
        
        self.replace_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Replace",
            height=30, font=("Segoe UI", 11)
        )
        self.replace_entry.pack(fill="x", pady=5)
        
        # Options
        options = ctk.CTkFrame(self, fg_color="transparent")
        options.pack(fill="x", padx=10)
        
        ctk.CTkCheckBox(options, text="Match Case", font=("Segoe UI", 10)).pack(anchor="w")
        ctk.CTkCheckBox(options, text="Match Whole Word", font=("Segoe UI", 10)).pack(anchor="w")
        ctk.CTkCheckBox(options, text="Use Regular Expression", font=("Segoe UI", 10)).pack(anchor="w")
        
        # Search button
        ctk.CTkButton(
            self, text="Search in Files",
            command=lambda: app.open_project_search(),
            height=32, font=("Segoe UI", 11)
        ).pack(fill="x", padx=10, pady=10)


class SourceControlPanel(ctk.CTkFrame):
    """Source control panel."""
    def __init__(self, master):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        
        header = ctk.CTkFrame(self, height=35, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="SOURCE CONTROL",
            font=("Segoe UI", 11, "bold"),
            text_color=("#383838", "#CCCCCC")
        ).pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(
            self, text="Git integration coming soon...",
            font=("Segoe UI", 10),
            text_color=("#666666", "#999999")
        ).pack(pady=20)


class RunDebugPanel(ctk.CTkFrame):
    """Run and debug panel."""
    def __init__(self, master, app):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        self.app = app
        
        header = ctk.CTkFrame(self, height=35, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="RUN AND DEBUG",
            font=("Segoe UI", 11, "bold"),
            text_color=("#383838", "#CCCCCC")
        ).pack(side="left", padx=10, pady=8)
        
        # Run button
        ctk.CTkButton(
            self, text="▶ Run Current File",
            command=app.run_current_file,
            height=35, font=("Segoe UI", 11),
            fg_color=("#007ACC", "#007ACC")
        ).pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            self, text="Debugging features coming soon...",
            font=("Segoe UI", 10),
            text_color=("#666666", "#999999")
        ).pack(pady=10)


class ExtensionsPanel(ctk.CTkFrame):
    """Extensions panel."""
    def __init__(self, master):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        
        header = ctk.CTkFrame(self, height=35, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="EXTENSIONS",
            font=("Segoe UI", 11, "bold"),
            text_color=("#383838", "#CCCCCC")
        ).pack(side="left", padx=10, pady=8)
        
        # Search extensions
        ctk.CTkEntry(
            self, placeholder_text="Search Extensions",
            height=30, font=("Segoe UI", 11)
        ).pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            self, text="Extension marketplace coming soon...",
            font=("Segoe UI", 10),
            text_color=("#666666", "#999999")
        ).pack(pady=10)


class SettingsPanel(ctk.CTkFrame):
    """Settings panel."""
    def __init__(self, master, app):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        self.app = app
        
        header = ctk.CTkFrame(self, height=35, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="SETTINGS",
            font=("Segoe UI", 11, "bold"),
            text_color=("#383838", "#CCCCCC")
        ).pack(side="left", padx=10, pady=8)
        
        # Settings options
        settings_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Theme
        ctk.CTkLabel(settings_frame, text="Theme", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 5))
        theme_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            theme_frame, text="Light", width=100,
            command=lambda: app.set_theme("light")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            theme_frame, text="Dark", width=100,
            command=lambda: app.set_theme("dark")
        ).pack(side="left", padx=5)
        
        # Font size
        ctk.CTkLabel(settings_frame, text="Font Size", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 5))
        ctk.CTkSlider(settings_frame, from_=10, to=24).pack(fill="x", pady=5)
        
        # Terminal
        ctk.CTkLabel(settings_frame, text="Panels", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 5))
        ctk.CTkCheckBox(settings_frame, text="Show Terminal").pack(anchor="w", pady=2)
        ctk.CTkCheckBox(settings_frame, text="Show AI Panel").pack(anchor="w", pady=2)
