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
from project_search import ProjectSearchWindow
from goto_definition import GotoDefinition, setup_goto_definition_bindings
import os
import shlex
import shutil
from typing import Optional, Callable
from logger import logger
from visual_feedback import VisualFeedback


class ModernMenuBar(ctk.CTkFrame):
    """Modern horizontal menu bar."""
    def __init__(self, master, app):
        super().__init__(master, height=35, fg_color=("#E5E5E5", "#1E1E1E"))
        self.app = app
        self.pack_propagate(False)
        
        menus = [
            ("File", [
                ("New Tab", lambda: app.tab_manager.new_tab()),
                ("Open", app.open_file),
                ("Save", app.save_file),
                ("Save As", app.save_file_as),
                None,
                ("Close Tab", lambda: app.tab_manager.close_tab(app.tab_manager.current_tab_index)),
                None,
                ("Exit", app.quit)
            ]),
            ("Edit", [
                ("Find & Replace", app.open_find_replace_window),
                ("Search in Project", app.open_project_search),
                None,
                ("Goto Definition", app.handle_goto_definition),
                ("Find References", app.find_references)
            ]),
            ("Selection", [
                ("Select All", lambda: app.tab_manager.text_area.event_generate("<<SelectAll>>")),
                ("Copy", lambda: app.tab_manager.text_area.event_generate("<<Copy>>")),
                ("Cut", lambda: app.tab_manager.text_area.event_generate("<<Cut>>")),
                ("Paste", lambda: app.tab_manager.text_area.event_generate("<<Paste>>"))
            ]),
            ("View", [
                ("Toggle Terminal", app.toggle_terminal),
                ("Toggle AI Panel", app.toggle_gemini),
                ("Toggle File Tree", app.toggle_file_tree),
                None,
                ("Light Theme", lambda: app.set_theme("light")),
                ("Dark Theme", lambda: app.set_theme("dark"))
            ]),
            ("Go", [
                ("Goto Definition (F12)", app.handle_goto_definition),
                ("Find References", app.find_references)
            ]),
            ("Run", [
                ("Run in Terminal", app.run_current_file),
                ("Clear Terminal", lambda: app.terminal.clear_terminal())
            ]),
            ("Terminal", [
                ("Show Terminal", lambda: app.terminal.grid()),
                ("Hide Terminal", lambda: app.terminal.grid_remove()),
                ("Clear", lambda: app.terminal.clear_terminal())
            ]),
            ("AI Assistant", [
                ("Explain Code", app.ai_explain_code),
                ("Generate Code...", app.ai_generate_code),
                None,
                ("Refactor Code", app.ai_refactor_code),
                ("Fix Errors...", app.ai_fix_errors),
                ("Optimize Code", app.ai_optimize_code),
                None,
                ("Generate Docstring", app.ai_generate_docstring),
                ("Translate Code...", app.ai_translate_code),
                None,
                ("Create File...", app.ai_create_file),
                ("Modify Current File...", app.ai_modify_current_file),
                ("Add Function...", app.ai_add_function)
            ]),
            ("Help", [
                ("About", app.show_about),
                ("Shortcuts", app.show_shortcuts)
            ])
        ]
        
        for label, items in menus:
            btn = ctk.CTkButton(
                self, text=label, width=60, height=28,
                fg_color="transparent", hover_color=("#D0D0D0", "#2D2D2D"),
                text_color=("#333333", "#CCCCCC"),
                corner_radius=4, font=("Segoe UI", 12),
                command=lambda i=items: self.show_dropdown(i)
            )
            btn.pack(side="left", padx=2, pady=3)


    def show_dropdown(self, items):
        """Show dropdown menu."""
        menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 10))
        for item in items:
            if item is None:
                menu.add_separator()
            else:
                label, command = item
                menu.add_command(label=label, command=command)
        try:
            menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + 35)
        finally:
            menu.grab_release()


class App(ctk.CTk):
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
        content.grid_rowconfigure(0, weight=3)
        content.grid_rowconfigure(1, weight=1)
        content.grid_rowconfigure(2, weight=1)
        content.grid_columnconfigure(0, weight=0, minsize=48)  # Sidebar
        content.grid_columnconfigure(1, weight=0, minsize=250)  # Panel
        content.grid_columnconfigure(2, weight=1)  # Editor
        
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
        
        self.sections = VSCodeSections(self.explorer_panel)
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
        self.terminal = TerminalPanel(content)
        self.terminal.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        
        # Gemini panel
        self.gemini_client = GeminiClient()
        self.gemini_panel = GeminiPanel(content, self.gemini_client)
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

    def open_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename()
        
        if not file_path:
            return
        
        # Validate file path
        if not isinstance(file_path, str):
            logger.error("Invalid file path type")
            messagebox.showerror("Error", "Invalid file path")
            return
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            messagebox.showerror("Error", f"File not found: {file_path}")
            return
        
        if not os.path.isfile(file_path):
            logger.error(f"Not a file: {file_path}")
            messagebox.showerror("Error", f"Not a file: {file_path}")
            return
        
        # Check file size (limit to 10MB)
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:
                logger.warning(f"Large file: {file_size // (1024*1024)}MB")
                if not messagebox.askyesno("Large File", f"File is {file_size // (1024*1024)}MB. Open anyway?"):
                    return
        except OSError as e:
            logger.error(f"Cannot check file size: {e}")
            messagebox.showerror("Error", f"Cannot check file size: {e}")
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tab_index = self.tab_manager.new_tab(file_path)
            tab = self.tab_manager.tabs[tab_index]
            
            tab.file_path = file_path
            tab.content = content
            self.tab_manager.switch_tab(tab_index)
            
            self.current_file = file_path
            self.title(f"NanoEditor v3.0 - {os.path.basename(file_path)}")
            self.status_bar.set_file_path(file_path)
            self.terminal.set_working_directory(os.path.dirname(file_path))
            self.file_tree.load_directory(os.path.dirname(file_path))
            logger.info(f"Opened: {file_path}")
            self.feedback.show_success(f"Opened: {os.path.basename(file_path)}")
        except UnicodeDecodeError:
            logger.error(f"Cannot decode: {file_path}")
            self.feedback.show_error("Cannot decode file")
            messagebox.showerror("Error", "Cannot decode file. Binary file or wrong encoding.")
        except PermissionError:
            logger.error(f"Permission denied: {file_path}")
            self.feedback.show_error("Permission denied")
            messagebox.showerror("Error", f"Permission denied: {file_path}")
        except OSError as e:
            logger.error(f"Cannot open file: {e}")
            messagebox.showerror("Error", f"Cannot open file: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            messagebox.showerror("Error", f"Unexpected error: {e}")

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
            self.terminal.execute_command(cmd)
        else:
            logger.warning(f"No runner for: {ext}")
            messagebox.showinfo("Run", f"No runner for {ext}")

    def show_about(self):
        messagebox.showinfo("About", "NanoEditor v3.0\nModern, lightweight code editor\nPowered by Gemini AI")

    def show_shortcuts(self):
        shortcuts = """Keyboard Shortcuts:
        
Ctrl+N - New Tab
Ctrl+O - Open File
Ctrl+S - Save File
Ctrl+W - Close Tab
Ctrl+F - Find & Replace
Ctrl+Shift+F - Search in Project
F12 - Goto Definition
Ctrl+Click - Goto Definition"""
        messagebox.showinfo("Shortcuts", shortcuts)

    def _get_selected_text(self) -> str:
        try:
            return self.tab_manager.text_area.get("sel.first", "sel.last")
        except tk.TclError:
            return self.tab_manager.text_area.get("1.0", "end-1c")

    def _insert_text_at_cursor(self, text: str) -> None:
        try:
            self.tab_manager.text_area.insert(ctk.INSERT, text)
        except tk.TclError:
            pass

    def _show_ai_result(self, title: str, result: str, allow_insert: bool = True) -> None:
        insert_callback = self._insert_text_at_cursor if allow_insert else None
        AIResultDialog(self, title, result, insert_callback).grab_set()
    
    def _handle_ai_result(self, title: str, result: str, allow_insert: bool, progress) -> None:
        progress.stop()
        self.feedback.show_success("AI completed")
        self._show_ai_result(title, result, allow_insert)

    def open_project_search(self):
        tab = self.tab_manager.get_current_tab()
        if tab and tab.file_path:
            workspace = os.path.dirname(tab.file_path)
        else:
            workspace = os.getcwd()
        ProjectSearchWindow(self, workspace, self.open_file_at_line).grab_set()

    def open_file_at_line(self, file_path, line_num=1):
        self.open_file(file_path)
        try:
            self.tab_manager.text_area.mark_set(ctk.INSERT, f"{line_num}.0")
            self.tab_manager.text_area.see(f"{line_num}.0")
            self.tab_manager.text_area.tag_remove("highlight", "1.0", "end")
            self.tab_manager.text_area.tag_add("highlight", f"{line_num}.0", f"{line_num}.end")
            self.tab_manager.text_area.tag_config("highlight", background="#3B8ED0")
            self.tab_manager.text_area.after(1500, lambda: self.tab_manager.text_area.tag_remove("highlight", "1.0", "end"))
        except (tk.TclError, AttributeError):
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
    
    def ai_explain_code(self) -> None:
        code = self._get_selected_text()
        if not code or not code.strip():
            messagebox.showwarning("No Code", "Select code to explain")
            return
        
        # Validate code length
        if len(code) > 50000:
            messagebox.showwarning("Code Too Long", "Selected code is too long (max 50K chars)")
            return
        
        self.status_bar.set_file_path("AI: Explaining...")
        progress = self.feedback.show_progress("AI analyzing code...")
        self.ai_assistant.explain_code(code, lambda r: self._handle_ai_result("Explanation", r, False, progress))
    
    def ai_generate_code(self) -> None:
        def on_desc(desc: str) -> None:
            lang = self._detect_language()
            self.status_bar.set_file_path("AI: Generating...")
            self.ai_assistant.generate_code(desc, lang, lambda r: self._show_ai_result("Generated", r))
        AIActionDialog(self, "Generate Code", "Describe code:", on_desc).grab_set()
    
    def ai_refactor_code(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to refactor")
            return
        self.status_bar.set_file_path("AI: Refactoring...")
        self.ai_assistant.refactor_code(code, lambda r: self._show_ai_result("Refactored", r))
    
    def ai_fix_errors(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to fix")
            return
        def on_err(err: str) -> None:
            self.status_bar.set_file_path("AI: Fixing...")
            self.ai_assistant.fix_errors(code, err, lambda r: self._show_ai_result("Fixed", r))
        AIActionDialog(self, "Fix Errors", "Error message:", on_err).grab_set()
    
    def ai_optimize_code(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to optimize")
            return
        self.status_bar.set_file_path("AI: Optimizing...")
        self.ai_assistant.optimize_code(code, lambda r: self._show_ai_result("Optimizations", r, False))
    
    def ai_generate_docstring(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select function/class")
            return
        self.status_bar.set_file_path("AI: Documenting...")
        self.ai_assistant.generate_docstring(code, lambda r: self._show_ai_result("Docstring", r))
    
    def ai_translate_code(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to translate")
            return
        def on_lang(lang: str) -> None:
            from_lang = self._detect_language()
            self.status_bar.set_file_path(f"AI: Translating to {lang}...")
            self.ai_assistant.translate_code(code, from_lang, lang, lambda r: self._show_ai_result("Translated", r))
        AIActionDialog(self, "Translate", "Target language:", on_lang).grab_set()
    
    def ai_create_file(self) -> None:
        def on_input(text: str) -> None:
            lines = text.strip().split('\n', 1)
            filename = lines[0].strip()
            description = lines[1].strip() if len(lines) > 1 else lines[0]
            self.status_bar.set_file_path(f"AI: Creating {filename}...")
            self.ai_file_ops.create_file_from_description(
                description, filename,
                lambda result: messagebox.showinfo("AI File Creation", result)
            )
        AIActionDialog(
            self, "Create File",
            "Line 1: filename.py\nLine 2: Description of what the file should do",
            on_input
        ).grab_set()
    
    def ai_modify_current_file(self) -> None:
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            messagebox.showwarning("No File", "Open a file first")
            return
        def on_instruction(instruction: str) -> None:
            self.status_bar.set_file_path("AI: Modifying file...")
            self.ai_file_ops.modify_file(
                tab.file_path, instruction,
                lambda result: self._handle_file_modification(result)
            )
        AIActionDialog(
            self, "Modify File",
            "Describe what changes to make:",
            on_instruction
        ).grab_set()
    
    def ai_add_function(self) -> None:
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            messagebox.showwarning("No File", "Open a file first")
            return
        def on_description(description: str) -> None:
            self.status_bar.set_file_path("AI: Adding function...")
            self.ai_file_ops.add_function_to_file(
                tab.file_path, description,
                lambda result: self._handle_file_modification(result)
            )
        AIActionDialog(
            self, "Add Function",
            "Describe the function to add:",
            on_description
        ).grab_set()
    
    def _handle_file_modification(self, result: str) -> None:
        messagebox.showinfo("AI File Modification", result)
        tab = self.tab_manager.get_current_tab()
        if "✅" in result and tab and tab.file_path:
            self.open_file(tab.file_path)


if __name__ == "__main__":
    app = App()
    app.mainloop()
