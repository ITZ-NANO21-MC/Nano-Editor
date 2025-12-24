"""VS Code style sidebar with activity bar."""
import customtkinter as ctk
import tkinter as tk
from tkfontawesome import icon_to_image


class VSCodeSidebar(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, width=48, fg_color=("#E5E5E5", "#333333"), corner_radius=0)
        self.pack_propagate(False)
        self.app = app
        self.current_view = "explorer"
        
        # Icon cache to prevent garbage collection
        self.icons = {}
        self._create_icons()
        
        # Activity buttons
        self.buttons = {}
        
        activities = [
            ("copy", "explorer", "Explorer (Ctrl+Shift+E)"),
            ("search", "search", "Search (Ctrl+Shift+F)"),
            ("code-branch", "source", "Source Control (Ctrl+Shift+G)"),
            ("play", "run", "Run and Debug (Ctrl+Shift+D)"),
            ("robot", "ai", "AI Assistant (Ctrl+Shift+A)"),
            ("boxes", "extensions", "Extensions (Ctrl+Shift+X)"),
        ]
        
        # Top buttons
        for icon_name, view, tooltip in activities:
            btn = ctk.CTkButton(
                self, image=self.icons.get(icon_name), text="", 
                width=48, height=48,
                fg_color="transparent",
                hover_color=("#D0D0D0", "#2A2D2E"),
                corner_radius=0,
                command=lambda v=view: self.switch_view(v)
            )
            btn.pack(side="top")
            self.buttons[view] = btn
            self._create_tooltip(btn, tooltip)
        
        # Spacer
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(side="top", expand=True, fill="both")
        
        # Bottom buttons
        bottom_activities = [
            ("user-circle", "account", "Account"),
            ("cog", "settings", "Settings (Ctrl+,)"),
        ]
        
        for icon_name, view, tooltip in bottom_activities:
            btn = ctk.CTkButton(
                self, image=self.icons.get(icon_name), text="",
                width=48, height=48,
                fg_color="transparent",
                hover_color=("#D0D0D0", "#2A2D2E"),
                corner_radius=0,
                command=lambda v=view: self.switch_view(v)
            )
            btn.pack(side="bottom")
            self.buttons[view] = btn
            self._create_tooltip(btn, tooltip)
        
        self.set_active("explorer")

    def _create_icons(self):
        """Creates FontAwesome icons and stores them in cache."""
        mode = ctk.get_appearance_mode()
        color = "#333333" if mode == "Light" else "#CCCCCC"
        
        icon_names = ["copy", "search", "code-branch", "play", "robot", "boxes", "user-circle", "cog"]
        for name in icon_names:
            # The SvgImage is not compatible with CTkImage, so we pass it directly.
            # This might affect automatic color switching on theme change.
            img = icon_to_image(name, fill=color, scale_to_width=20)
            self.icons[name] = img
    
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
        
        # Options variables
        self.match_case_var = tk.BooleanVar(value=False)
        self.match_word_var = tk.BooleanVar(value=False)
        self.use_regex_var = tk.BooleanVar(value=False)
        
        # Options
        options = ctk.CTkFrame(self, fg_color="transparent")
        options.pack(fill="x", padx=10)
        
        ctk.CTkCheckBox(options, text="Match Case", font=("Segoe UI", 10), variable=self.match_case_var).pack(anchor="w")
        ctk.CTkCheckBox(options, text="Match Whole Word", font=("Segoe UI", 10), variable=self.match_word_var).pack(anchor="w")
        ctk.CTkCheckBox(options, text="Use Regular Expression", font=("Segoe UI", 10), variable=self.use_regex_var).pack(anchor="w")
        
        # Search button
        ctk.CTkButton(
            self, text="Search in Files",
            command=self.perform_sidebar_search,
            height=32, font=("Segoe UI", 11)
        ).pack(fill="x", padx=10, pady=10)

    def perform_sidebar_search(self):
        """
        Gathers search terms and options from the sidebar and opens the global search window.
        
        This method extracts the query from the search entry and the state of the 
        configuration checkboxes (case sensitivity, whole word, regex) to initiate
        a project-wide search.
        """
        query = self.search_entry.get()
        if not query:
            return
            
        options = {
            "query": query,
            "case_sensitive": self.match_case_var.get(),
            "whole_word": self.match_word_var.get(),
            "use_regex": self.use_regex_var.get()
        }
        self.app.open_project_search(options)


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
    """Settings panel for editor configuration."""
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
        
        # Control variables
        self.show_terminal_var = tk.BooleanVar(value=True)
        self.show_ai_var = tk.BooleanVar(value=True)
        self.font_size_var = tk.IntVar(value=13)
        
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
        self.font_slider = ctk.CTkSlider(
            settings_frame, from_=8, to=30,
            variable=self.font_size_var,
            command=self.update_font
        )
        self.font_slider.pack(fill="x", pady=5)
        
        # Panels visibility
        ctk.CTkLabel(settings_frame, text="Panels", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.terminal_cb = ctk.CTkCheckBox(
            settings_frame, text="Show Terminal",
            variable=self.show_terminal_var,
            command=self.update_panels
        )
        self.terminal_cb.pack(anchor="w", pady=2)
        
        self.ai_cb = ctk.CTkCheckBox(
            settings_frame, text="Show AI Panel",
            variable=self.show_ai_var,
            command=self.update_panels
        )
        self.ai_cb.pack(anchor="w", pady=2)

    def update_panels(self):
        """
        Updates the visibility of terminal and AI panels based on checkbox states.
        """
        show_terminal = self.show_terminal_var.get()
        show_ai = self.show_ai_var.get()
        
        if show_terminal:
            self.app.terminal.grid()
        else:
            self.app.terminal.grid_remove()
            
        if show_ai:
            self.app.gemini_panel.grid()
        else:
            self.app.gemini_panel.grid_remove()

    def update_font(self, value):
        """
        Updates the editor font size in real-time.
        
        Args:
            value (float): The new font size from the slider.
        """
        size = int(value)
        self.app.update_font_size(size)
