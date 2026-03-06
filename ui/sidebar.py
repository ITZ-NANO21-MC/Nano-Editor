"""VS Code style sidebar with activity bar."""
import customtkinter as ctk
import tkinter as tk
from tkfontawesome import icon_to_image
from pygments.styles import get_all_styles


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
            ("brain", "agent", "Nano-Agent (Ctrl+Shift+Z)"),
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
        
        icon_names = ["copy", "search", "code-branch", "play", "robot", "brain", "boxes", "user-circle", "cog"]
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
        elif view == "agent":
            self.app.show_agent()
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


class SettingsWindowBase(ctk.CTkToplevel):
    """Base class for settings dialogs."""
    def __init__(self, master, title, width=400, height=450):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.after(10, self.lift)
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        x = master.winfo_screenwidth() // 2 - width // 2
        y = master.winfo_screenheight() // 2 - height // 2
        self.geometry(f"+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkLabel(self, text=title, font=("Segoe UI", 16, "bold"))
        header.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Close button
        btn = ctk.CTkButton(self, text="Cerrar", command=self.destroy, width=100)
        btn.grid(row=2, column=0, pady=(0, 20))


class AppearanceSettingsWindow(SettingsWindowBase):
    """Appearance settings dialog."""
    def __init__(self, master, app):
        super().__init__(master, "Configuración de Apariencia")
        self.app = app
        
        # Theme
        ctk.CTkLabel(self.content_frame, text="Tema del Editor", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 5))
        theme_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            theme_frame, text="Claro", width=100,
            command=lambda: app.set_theme("light")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            theme_frame, text="Oscuro", width=100,
            command=lambda: app.set_theme("dark")
        ).pack(side="left", padx=5)
        
        # Font size
        ctk.CTkLabel(self.content_frame, text="Tamaño de Fuente", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(20, 5))
        self.font_size_var = tk.IntVar(value=app.settings_panel.font_size_var.get() if hasattr(app, 'settings_panel') else 13)
        self.font_slider = ctk.CTkSlider(
            self.content_frame, from_=8, to=30,
            variable=self.font_size_var,
            command=self.update_font
        )
        self.font_slider.pack(fill="x", pady=5)
        
        # Syntax Highlighting
        ctk.CTkLabel(self.content_frame, text="Resaltado de Sintaxis", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(20, 5))
        
        styles = list(get_all_styles())
        styles.sort()
        styles = styles[:15]
        
        if "monokai" not in styles:
            styles.append("monokai")
            styles.sort()
        
        self.style_var = ctk.StringVar(value=app.settings_panel.style_var.get() if hasattr(app, 'settings_panel') else "monokai")
        self.style_menu = ctk.CTkComboBox(
            self.content_frame, values=styles,
            variable=self.style_var,
            command=self.update_style,
            state="readonly"
        )
        self.style_menu.pack(fill="x", pady=5)

    def update_font(self, value):
        self.app.update_font_size(int(value))
        if hasattr(self.app, 'settings_panel'):
            self.app.settings_panel.font_size_var.set(int(value))

    def update_style(self, choice):
        self.app.set_syntax_theme(choice)
        if hasattr(self.app, 'settings_panel'):
            self.app.settings_panel.style_var.set(choice)


class PanelsSettingsWindow(SettingsWindowBase):
    """Panels visibility settings dialog."""
    def __init__(self, master, app):
        super().__init__(master, "Configuración de Paneles", height=300)
        self.app = app
        
        ctk.CTkLabel(self.content_frame, text="Visibilidad de Paneles", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.show_terminal_var = app.settings_panel.show_terminal_var
        self.show_ai_var = app.settings_panel.show_ai_var
        
        ctk.CTkCheckBox(
            self.content_frame, text="Mostrar Terminal",
            variable=self.show_terminal_var,
            command=self.update_panels
        ).pack(anchor="w", pady=10)
        
        ctk.CTkCheckBox(
            self.content_frame, text="Mostrar Panel IA",
            variable=self.show_ai_var,
            command=self.update_panels
        ).pack(anchor="w", pady=10)

    def update_panels(self):
        self.app.settings_panel.update_panels()


class AIModelSettingsWindow(SettingsWindowBase):
    """AI provider and model settings dialog with API key management."""
    
    # Map provider display names to their .env key names
    PROVIDER_KEY_MAP = {
        "Gemini": "GEMINI_API_KEY",
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY",
        "DeepSeek": "DEEPSEEK_API_KEY",
        "Groq": "GROQ_API_KEY",
        "Ollama": "OLLAMA_API_BASE"
    }
    
    def __init__(self, master, app):
        super().__init__(master, "Configuración de IA", height=520)
        self.app = app
        self.providers = app.settings_panel.providers
        
        from config import config
        self.config = config
        
        # --- Provider ---
        ctk.CTkLabel(self.content_frame, text="Proveedor de IA", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.provider_var = app.settings_panel.provider_var
        self.provider_menu = ctk.CTkComboBox(
            self.content_frame, values=list(self.providers.keys()),
            variable=self.provider_var,
            command=self.on_provider_changed,
            state="readonly"
        )
        self.provider_menu.pack(fill="x", pady=5)

        # --- Model ---
        ctk.CTkLabel(self.content_frame, text="Modelo de IA", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15, 5))
        
        self.ai_model_var = app.settings_panel.ai_model_var
        self.ai_model_menu = ctk.CTkComboBox(
            self.content_frame, values=self.providers.get(self.provider_var.get(), []),
            variable=self.ai_model_var,
            command=self.update_ai_model,
            state="readonly"
        )
        self.ai_model_menu.pack(fill="x", pady=5)

        # --- API Key Section ---
        self.api_key_label = ctk.CTkLabel(self.content_frame, text="API Key", font=("Segoe UI", 12, "bold"))
        self.api_key_label.pack(anchor="w", pady=(15, 5))
        
        self.api_key_var = ctk.StringVar()
        self.api_key_entry = ctk.CTkEntry(
            self.content_frame, textvariable=self.api_key_var,
            placeholder_text="Ingresa tu API Key...",
            show="•", height=32, font=("Consolas", 11)
        )
        self.api_key_entry.pack(fill="x", pady=5)
        
        # Show/Hide toggle + Save button
        key_actions = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        key_actions.pack(fill="x", pady=5)
        
        self.show_key_var = tk.BooleanVar(value=False)
        self.show_key_check = ctk.CTkCheckBox(
            key_actions, text="Mostrar", variable=self.show_key_var,
            command=self._toggle_key_visibility, width=80
        )
        self.show_key_check.pack(side="left")
        
        self.save_key_btn = ctk.CTkButton(
            key_actions, text="💾 Guardar API Key", width=140,
            command=self._save_api_key
        )
        self.save_key_btn.pack(side="right")
        
        # Status indicator
        self.key_status_label = ctk.CTkLabel(
            self.content_frame, text="", font=("Segoe UI", 10)
        )
        self.key_status_label.pack(anchor="w", pady=(2, 0))
        
        # Load initial state
        self._load_api_key_for_provider(self.provider_var.get())

    def on_provider_changed(self, provider):
        """Handle provider change: update models and API key field."""
        self.app.settings_panel.update_provider_models(provider)
        models = self.providers.get(provider, [])
        self.ai_model_menu.configure(values=models)
        self._load_api_key_for_provider(provider)

    def _load_api_key_for_provider(self, provider):
        """Load the stored API key for the given provider into the entry."""
        env_key = self.PROVIDER_KEY_MAP.get(provider, "")
        
        if provider == "Ollama":
            self.api_key_label.configure(text="Ollama API Base URL")
            self.api_key_entry.configure(placeholder_text="http://localhost:11434", show="")
        else:
            self.api_key_label.configure(text=f"API Key ({provider})")
            self.api_key_entry.configure(placeholder_text="Ingresa tu API Key...")
            if not self.show_key_var.get():
                self.api_key_entry.configure(show="•")
            else:
                self.api_key_entry.configure(show="")
        
        stored_value = self.config.get(env_key, "") if env_key else ""
        self.api_key_var.set(stored_value or "")
        
        # Update status
        if stored_value:
            self.key_status_label.configure(text=f"✅ {env_key} configurada", text_color="#00CC44")
        else:
            self.key_status_label.configure(text=f"⚠️ {env_key} no configurada", text_color="#FFCC00")

    def _toggle_key_visibility(self):
        provider = self.provider_var.get()
        if provider == "Ollama":
            self.api_key_entry.configure(show="")
        elif self.show_key_var.get():
            self.api_key_entry.configure(show="")
        else:
            self.api_key_entry.configure(show="•")

    def _save_api_key(self):
        """Save the API key for the current provider to .env."""
        provider = self.provider_var.get()
        env_key = self.PROVIDER_KEY_MAP.get(provider, "")
        value = self.api_key_var.get().strip()
        
        if not env_key:
            return
            
        if not value:
            from tkinter import messagebox
            messagebox.showwarning("API Key", f"Ingresa una API Key para {provider}.", parent=self)
            return
        
        self.config.set(env_key, value)
        if self.config.save():
            self.key_status_label.configure(text=f"✅ {env_key} guardada correctamente", text_color="#00CC44")
            if hasattr(self.app, 'feedback'):
                self.app.feedback.show_success(f"API Key de {provider} guardada")
        else:
            self.key_status_label.configure(text=f"❌ Error al guardar {env_key}", text_color="#FF5555")

    def update_ai_model(self, choice):
        self.app.settings_panel.update_ai_model(choice)


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
        
        # Variables persist here to maintain state
        self.show_terminal_var = tk.BooleanVar(value=True)
        self.show_ai_var = tk.BooleanVar(value=True)
        self.font_size_var = tk.IntVar(value=13)
        self.style_var = ctk.StringVar(value="monokai")
        
        self.providers = {
            "Gemini": ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"],
            "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "Anthropic": ["claude-3-5-sonnet", "claude-3-5-haiku", "claude-3-opus", "claude-3-sonnet"],
            "DeepSeek": ["deepseek-chat", "deepseek-coder"],
            "Groq": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            "Ollama": ["llama3", "mistral", "codellama"]
        }
        
        from config import config
        current_full_model = config.get('AI_MODEL', 'gemini/gemini-2.0-flash')
        
        if '/' in current_full_model:
            curr_provider_key, curr_model_name = current_full_model.split('/', 1)
            provider_map = {k.lower(): k for k in self.providers.keys()}
            current_provider = provider_map.get(curr_provider_key.lower(), "Gemini")
        else:
            current_provider = "Gemini"
            curr_model_name = current_full_model

        self.provider_var = ctk.StringVar(value=current_provider)
        self.ai_model_var = ctk.StringVar(value=curr_model_name)

        # Settings Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        categories = [
            ("Apariencia", self.open_appearance),
            ("Paneles", self.open_panels),
            ("Configuración de IA", self.open_ai)
        ]
        
        for name, cmd in categories:
            btn = ctk.CTkButton(
                btn_frame, text=name, command=cmd,
                height=40, font=("Segoe UI", 12),
                anchor="w", fg_color=("#E0E0E0", "#333333"),
                text_color=("#333333", "#FFFFFF"),
                hover_color=("#D0D0D0", "#404040")
            )
            btn.pack(fill="x", pady=5)

    def open_appearance(self):
        AppearanceSettingsWindow(self.app, self.app).grab_set()

    def open_panels(self):
        PanelsSettingsWindow(self.app, self.app).grab_set()

    def open_ai(self):
        AIModelSettingsWindow(self.app, self.app).grab_set()

    def update_provider_models(self, provider):
        models = self.providers.get(provider, [])
        if models:
            self.ai_model_var.set(models[0])
            self.update_ai_model(models[0])

    def update_ai_model(self, choice):
        from config import config
        provider = self.provider_var.get()
        prefix = provider.lower()
        
        if prefix == "openai":
             full_model = f"{prefix}/{choice}"
        elif prefix == "gemini":
             if not choice.startswith("gemini/"):
                full_model = f"{prefix}/{choice}"
             else:
                full_model = choice
        else:
             full_model = f"{prefix}/{choice}"

        config.set('AI_MODEL', full_model)
        if config.save():
            if hasattr(self.app, 'feedback'):
                self.app.feedback.show_success(f"Modelo actualizado: {choice}")
        else:
            if hasattr(self.app, 'feedback'):
                self.app.feedback.show_error("Error al guardar .env")

    def update_panels(self):
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
