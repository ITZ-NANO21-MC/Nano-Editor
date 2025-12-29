"""NanoEditor v3.0 - Modern, clean and lightweight GUI."""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from tab_manager import TabManager
from file_tree_vscode import VSCodeFileTree, VSCodeSections
from sidebar_vscode import VSCodeSidebar, SearchPanel, SourceControlPanel, RunDebugPanel, ExtensionsPanel, SettingsPanel
from ai_panel_vscode import AIAssistantPanel
from gemini_panel import GeminiPanel
from gemini_client import GeminiClient
from terminal_panel import TerminalPanel
from status_bar import StatusBar
from find_replace import FindReplaceWindow
from ai_assistant import AIAssistant
from ai_menu import AIActionDialog, AIResultDialog
from ai_file_operations import AIFileOperations
from project_context import ProjectContext
from project_search import ProjectSearchWindow
from goto_definition import GotoDefinition, setup_goto_definition_bindings
from ai_utils import process_ai_code_output
from ai_handler import AIHandler
from file_handler import FileHandler
from menu_bar import ModernMenuBar
import os
import shlex
import shutil
from typing import Optional, Callable
from logger import logger
from visual_feedback import VisualFeedback


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


class App(ctk.CTk, AIHandler, FileHandler):
    def __init__(self):
        super().__init__()
        
        logger.info("Starting NanoEditor v3.0")
        self.title("NanoEditor v3.0")
        self.geometry("1400x900")
        self.current_file = None
        self.file_tree_visible = True
        self.feedback = None  # Initialized after main frame
        
        # Set default theme to dark
        ctk.set_appearance_mode("dark")
        
        # Main container
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True)
        
        # Menu bar
        self.menu_bar = ModernMenuBar(main, self)
        self.menu_bar.pack(fill="x", side="top")
        
        # Content area
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True)
        
        # ============================================================
        # CONFIGURACIÓN DE GRID CORREGIDA (enteros en lugar de floats)
        # ============================================================
        content.grid_rowconfigure(0, weight=70)   # Editor: 70%
        content.grid_rowconfigure(1, weight=15)   # Terminal: 15%
        content.grid_rowconfigure(2, weight=15)   # Gemini panel: 15%
        
        content.grid_columnconfigure(0, weight=0, minsize=48)  # Sidebar
        content.grid_columnconfigure(1, weight=0, minsize=250) # Panel
        content.grid_columnconfigure(2, weight=1)              # Editor
        # ============================================================
        
        # Activity bar (sidebar)
        self.sidebar = VSCodeSidebar(content, self)
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="ns")
        
        # Panel container (for explorer, search, etc.)
        self.panel_container = ctk.CTkFrame(content, fg_color="transparent")
        self.panel_container.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.panel_container.grid_rowconfigure(0, weight=1)
        self.panel_container.grid_rowconfigure(1, weight=0)
        
        # Create all panels
        self.explorer_panel = ctk.CTkFrame(self.panel_container, fg_color="transparent")
        self.explorer_panel.grid_rowconfigure(0, weight=1)
        self.explorer_panel.grid_rowconfigure(1, weight=0)
        
        self.file_tree = VSCodeFileTree(self.explorer_panel, self)
        self.file_tree.grid(row=0, column=0, sticky="nsew")
        
        self.sections = VSCodeSections(self.explorer_panel, self)
        self.sections.grid(row=1, column=0, sticky="ew")
        
        self.search_panel = SearchPanel(self.panel_container, self)
        self.source_panel = SourceControlPanel(self.panel_container)
        self.run_panel = RunDebugPanel(self.panel_container, self)
        self.ai_panel = AIAssistantPanel(self.panel_container, self)
        self.extensions_panel = ExtensionsPanel(self.panel_container)
        self.settings_panel = SettingsPanel(self.panel_container, self)
        
        # Show explorer by default
        self.current_panel = self.explorer_panel
        self.explorer_panel.grid(row=0, column=0, rowspan=3, sticky="nsew")
        
        # Tab manager
        self.tab_manager = TabManager(content)
        self.tab_manager.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        # Terminal
        self.terminal_panel = TerminalPanel(content)
        self.terminal_panel.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        self.terminal = self.terminal_panel # Alias
        
        # Gemini panel
        self.gemini_client = GeminiClient()
        self.gemini_panel = GeminiPanel(
            content,
            self.gemini_client,
            context_provider=self._get_project_context,
            app=self
        )
        self.gemini_panel.grid(row=2, column=2, sticky="nsew", padx=5, pady=5)
        
        # Status bar
        self.status_bar = StatusBar(main)
        self.status_bar.pack(fill="x", side="bottom")
        
        # Visual feedback
        self.feedback = VisualFeedback(self)
        
        # AI components
        self.ai_assistant = AIAssistant()
        self.ai_file_ops = AIFileOperations(os.getcwd())
        
        # Goto definition
        self.goto_def = GotoDefinition(
            self.tab_manager.text_area,
            self.open_file_at_line
        )
        setup_goto_definition_bindings(
            self.tab_manager.text_area,
            self.handle_goto_definition
        )
        
        self.update_status_bar()
        
        # Bindings
        self.tab_manager.text_area.bind("<KeyRelease>", self.update_status_bar)
        self.tab_manager.text_area.bind("<Button-1>", self.update_status_bar)
        
        # Shortcuts
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-n>", lambda e: self.tab_manager.new_tab())
        self.bind("<Control-w>", lambda e: self.tab_manager.close_tab(self.tab_manager.current_tab_index))
        self.bind("<Control-f>", lambda e: self.open_find_replace_window())
        self.bind("<Control-Shift-F>", lambda e: self.show_search())
        self.bind("<Control-Shift-E>", lambda e: self.show_explorer())
        self.bind("<Control-Shift-G>", lambda e: self.show_source_control())
        self.bind("<Control-Shift-D>", lambda e: self.show_run_debug())
        self.bind("<Control-Shift-A>", lambda e: self.show_ai_assistant())
        self.bind("<Control-Shift-X>", lambda e: self.show_extensions())
        self.bind("<Control-comma>", lambda e: self.show_settings())

        # Bind editing shortcuts directly to text_area to prevent bubbling
        self.tab_manager.text_area.bind("<Control-a>", lambda e: self.select_all())
        self.tab_manager.text_area.bind("<Control-c>", self.copy_text)
        self.tab_manager.text_area.bind("<Control-x>", self.cut_text)
        self.tab_manager.text_area.bind("<Control-v>", self.paste_text)

    def toggle_file_tree(self):
        if self.file_tree_visible:
            self.panel_container.grid_remove()
            self.file_tree_visible = False
        else:
            self.panel_container.grid()
            self.file_tree_visible = True
    
    def show_explorer(self):
        """Show explorer panel."""
        self._hide_all_panels()
        self.explorer_panel.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.current_panel = self.explorer_panel
        if not self.file_tree_visible:
            self.panel_container.grid()
            self.file_tree_visible = True
    
    def show_search(self):
        """Show search panel."""
        self._hide_all_panels()
        self.search_panel.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.current_panel = self.search_panel
        if not self.file_tree_visible:
            self.panel_container.grid()
            self.file_tree_visible = True
    
    def show_source_control(self):
        """Show source control panel."""
        self._hide_all_panels()
        self.source_panel.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.current_panel = self.source_panel
        if not self.file_tree_visible:
            self.panel_container.grid()
            self.file_tree_visible = True
    
    def show_run_debug(self):
        """Show run and debug panel."""
        self._hide_all_panels()
        self.run_panel.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.current_panel = self.run_panel
        if not self.file_tree_visible:
            self.panel_container.grid()
            self.file_tree_visible = True
    
    def show_ai_assistant(self):
        """Show AI assistant panel."""
        self._hide_all_panels()
        self.ai_panel.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.current_panel = self.ai_panel
        if not self.file_tree_visible:
            self.panel_container.grid()
            self.file_tree_visible = True
    
    def show_extensions(self):
        """Show extensions panel."""
        self._hide_all_panels()
        self.extensions_panel.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.current_panel = self.extensions_panel
        if not self.file_tree_visible:
            self.panel_container.grid()
            self.file_tree_visible = True
    
    def show_settings(self):
        """Show settings panel."""
        self._hide_all_panels()
        self.settings_panel.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.current_panel = self.settings_panel
        if not self.file_tree_visible:
            self.panel_container.grid()
            self.file_tree_visible = True
    
    def show_account(self):
        """Show account info."""
        messagebox.showinfo("Account", "NanoEditor v3.0\nAccount management coming soon...")
    
    def _hide_all_panels(self):
        """Hide all side panels."""
        for panel in [self.explorer_panel, self.search_panel, self.source_panel, 
                      self.run_panel, self.ai_panel, self.extensions_panel, self.settings_panel]:
            panel.grid_remove()

    def toggle_terminal(self):
        if self.terminal.winfo_viewable():
            self.terminal.grid_remove()
        else:
            self.terminal.grid()

    def toggle_gemini(self):
        if self.gemini_panel.winfo_viewable():
            self.gemini_panel.grid_remove()
        else:
            self.gemini_panel.grid()

    def open_find_replace_window(self):
        FindReplaceWindow(self, self.tab_manager.text_area).grab_set()

    def set_theme(self, theme):
        ctk.set_appearance_mode(theme)
        # Update file tree theme
        if hasattr(self, 'file_tree'):
            self.file_tree.update_tree_theme()

    def set_syntax_theme(self, theme):
        """Update syntax highlighting theme."""
        print(f"[DEBUG] App: Setting syntax theme to: {theme}")
        self.tab_manager.text_area.set_syntax_theme(theme)

    def update_font_size(self, size):
        """
        Updates the font size of the editor text area and synchronizes line numbers.
        
        Args:
            size (int): The new font size in pixels.
        """
        self.tab_manager.text_area.configure(font=("monospace", size))
        if self.tab_manager.line_numbers:
            self.tab_manager.line_numbers.redraw()

    def save_file(self):
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            self.save_file_as()
            return
        
        # Validate file path
        if not isinstance(tab.file_path, str) or not tab.file_path.strip():
            messagebox.showerror("Error", "Invalid file path")
            return
        
        try:
            content = self.tab_manager.text_area.get("1.0", "end-1c")
            
            # Create backup before saving
            if os.path.exists(tab.file_path):
                backup_path = tab.file_path + ".bak"
                try:
                    shutil.copy2(tab.file_path, backup_path)
                except (OSError, IOError, PermissionError):
                    pass  # Backup is optional
            
            with open(tab.file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            tab.modified = False
            tab.content = content
            self.tab_manager.update_tab_title()
            self.status_bar.set_file_path(f"Saved: {tab.file_path}")
            logger.info(f"Saved: {tab.file_path}")
            self.feedback.show_success("File saved")
        except PermissionError:
            logger.error(f"Permission denied: {tab.file_path}")
            self.feedback.show_error("Permission denied")
            messagebox.showerror("Error", f"Permission denied: {tab.file_path}")
        except OSError as e:
            logger.error(f"Cannot save: {e}")
            messagebox.showerror("Error", f"Cannot save file: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            messagebox.showerror("Error", f"Unexpected error: {e}")

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename()
        if file_path:
            tab = self.tab_manager.get_current_tab()
            if tab:
                tab.file_path = file_path
                self.save_file()

    def update_status_bar(self, event: Optional[tk.Event] = None) -> None:
        try:
            cursor_pos = self.tab_manager.text_area.index(ctk.INSERT)
            line, col = cursor_pos.split('.')
            self.status_bar.set_line_col(line, int(col) + 1)
        except (tk.TclError, ValueError, AttributeError):
            pass

    def run_current_file(self) -> None:
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            messagebox.showwarning("No File", "Save file first")
            return
        
        # Validate file path
        if not os.path.isfile(tab.file_path):
            logger.error(f"File not found: {tab.file_path}")
            messagebox.showerror("Error", "File does not exist")
            return
        
        self.save_file()
        ext = os.path.splitext(tab.file_path)[1]
        
        # Sanitized commands using list format (prevents injection)
        commands = {
            ".py": ["python3", tab.file_path],
            ".js": ["node", tab.file_path],
            ".sh": ["bash", tab.file_path]
        }
        
        cmd_list = commands.get(ext)
        if cmd_list:
            # Convert list to shell command string safely
            cmd = " ".join(shlex.quote(arg) for arg in cmd_list)
            logger.info(f"Running: {tab.file_path}")
            self.feedback.show_info("Running file...")
            self.terminal.run_command(cmd)
        else:
            logger.warning(f"No runner for: {ext}")
            messagebox.showinfo("Run", f"No runner for {ext}")

    def show_about(self):
        AboutWindow(self)

    def show_shortcuts(self):
        ShortcutsWindow(self)

    def _get_project_context(self) -> str:
        """Gathers and returns the project context string."""
        project_root = os.getcwd()  # Or determine from file_tree
        context_builder = ProjectContext(self.tab_manager, self.file_tree, project_root)
        return context_builder.gather_context_for_ai()

    def _get_selected_text(self) -> str:
        """Get selected text or all text if nothing is selected."""
        try:
             # Check if there's a selection
            if self.tab_manager.text_area.tag_ranges("sel"):
                return self.tab_manager.text_area.get("sel.first", "sel.last")
            else:
                # Get current line if cursor is on it
                cursor_pos = self.tab_manager.text_area.index(ctk.INSERT)
                line_num = cursor_pos.split('.')[0]
                return self.tab_manager.text_area.get(f"{line_num}.0", f"{line_num}.end")
        except (tk.TclError, AttributeError, ValueError):
            # Fallback to entire content
            try:
                return self.tab_manager.text_area.get("1.0", "end-1c")
            except (tk.TclError, AttributeError):
                return ""

    def has_text_selected(self):
        """Check if there's any text selected in the editor."""
        try:
            # Targeted check on internal textbox
            text_widget = self.tab_manager.text_area
            if hasattr(text_widget, "_textbox"):
                text_widget = text_widget._textbox
            
            if text_widget.tag_ranges("sel"):
                return True
            return False
        except Exception:
            return False

    def select_all(self, event=None):
        """Select all text in the current editor."""
        try:
            text_widget = self.tab_manager.text_area
            if hasattr(text_widget, "_textbox"):
                text_widget = text_widget._textbox
            
            text_widget.tag_add("sel", "1.0", "end")
            text_widget.focus_set()
            return "break"
        except Exception as e:
            logger.error(f"Error selecting all text: {e}")
            return "break"

    def copy_text(self, event=None):
        """Copy selected text to clipboard."""
        try:
            text_area = self.tab_manager.text_area
            # Use internal textbox if available
            text_widget = text_area._textbox if hasattr(text_area, "_textbox") else text_area

            if self.has_text_selected():
                try:
                    selected_text = text_widget.get("sel.first", "sel.last")
                    if selected_text:
                        self.clipboard_clear()
                        self.clipboard_append(selected_text)
                        self.feedback.show_success("Text copied")
                        return "break"
                except tk.TclError:
                    pass
            
            self.feedback.show_warning("No text selected")
        except Exception as e:
            logger.error(f"Error copying text: {e}")
            self.feedback.show_error("Failed to copy")
        return "break"

    def cut_text(self, event=None):
        """Cut selected text to clipboard."""
        try:
            text_area = self.tab_manager.text_area
            # Use internal textbox if available
            text_widget = text_area._textbox if hasattr(text_area, "_textbox") else text_area

            if self.has_text_selected():
                try:
                    selected_text = text_widget.get("sel.first", "sel.last")
                    if selected_text:
                        self.clipboard_clear()
                        self.clipboard_append(selected_text)
                        
                        # Use internal widget delete to be precise
                        text_widget.delete("sel.first", "sel.last")
                        
                        self.feedback.show_success("Text cut")
                        return "break"
                except tk.TclError:
                    pass

            self.feedback.show_warning("No text selected")
        except Exception as e:
            logger.error(f"Error cutting text: {e}")
            self.feedback.show_error("Failed to cut")
        return "break"

    def paste_text(self, event=None):
        """Paste text from clipboard."""
        try:
            text_area = self.tab_manager.text_area
            # Use internal textbox if available
            text_widget = text_area._textbox if hasattr(text_area, "_textbox") else text_area

            try:
                clipboard_text = self.clipboard_get()
            except tk.TclError:
                clipboard_text = ""

            if not clipboard_text:
                self.feedback.show_warning("Clipboard is empty")
                return "break"

            if self.has_text_selected():
                try:
                    insert_pos = text_widget.index("sel.first")
                    text_widget.delete("sel.first", "sel.last")
                    text_widget.insert(insert_pos, clipboard_text)
                except tk.TclError:
                    text_widget.insert(ctk.INSERT, clipboard_text)
            else:
                text_widget.insert(ctk.INSERT, clipboard_text)

            # Ensure visibility
            text_widget.see(ctk.INSERT)
            self.feedback.show_success("Text pasted")
            return "break"

        except Exception as e:
            logger.error(f"Error pasting text: {e}")
            self.feedback.show_error("Failed to paste")
        return "break"

    def open_project_search(self, search_options=None):
        """
        Opens the project-wide search window.
        
        Args:
            search_options (dict, optional): Initial search configuration containing 
                'query', 'case_sensitive', 'whole_word', and 'use_regex'.
        """
        tab = self.tab_manager.get_current_tab()
        if tab and tab.file_path:
            workspace = os.path.dirname(tab.file_path)
        else:
            workspace = os.getcwd()
        ProjectSearchWindow(self, workspace, self.open_file_at_line, search_options).grab_set()

    def open_file_at_line(self, file_path, line_num=1):
        self.open_file(file_path)
        try:
            self.tab_manager.text_area.mark_set(ctk.INSERT, f"{line_num}.0")
            self.tab_manager.text_area.see(f"{line_num}.0")
            self.tab_manager.text_area.tag_remove("highlight", "1.0", "end")
            self.tab_manager.text_area.tag_add("highlight", f"{line_num}.0", f"{line_num}.end")
            self.tab_manager.text_area.tag_config("highlight", background="#3B8ED0")
            self.tab_manager.text_area.after(1500, lambda: self.tab_manager.text_area.tag_remove("highlight", "1.0", "end"))
        except (tkinter.TclError, AttributeError):
            pass

    def handle_goto_definition(self):
        if not self.goto_def.goto_definition():
            self.status_bar.set_file_path("No definition found")

    def find_references(self):
        references = self.goto_def.find_symbol_references()
        if references:
            result = f"Found {len(references)} references:\n\n"
            for ref in references:
                result += f"{ref.module_path}:{ref.line} - {ref.name}\n"
            messagebox.showinfo("References", result)
        else:
            messagebox.showinfo("References", "No references found")

    def _detect_language(self) -> str:
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            return "Python"
        ext_map = {".py": "Python", ".js": "JavaScript", ".java": "Java", ".cpp": "C++", ".go": "Go"}
        ext = os.path.splitext(tab.file_path)[1]
        return ext_map.get(ext, "Python")

    def _insert_text_at_cursor(self, text: str) -> None:
        try:
            self.tab_manager.text_area.insert(ctk.INSERT, text)
        except tkinter.TclError:
            pass



if __name__ == "__main__":
    app = App()
    app.mainloop()
