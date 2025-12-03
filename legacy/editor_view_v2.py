"""NanoEditor with tabs and integrated terminal."""
import customtkinter
import tkinter
from tkinter import filedialog, messagebox
from tab_manager import TabManager
from file_tree import FileTree
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


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("NanoEditor v2.0")
        self.geometry("1400x900")
        self.current_file = None

        # Grid layout
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # File tree
        self.file_tree = FileTree(self)
        self.file_tree.grid(row=0, column=0, rowspan=3, sticky="ns")

        # Tab manager with editor
        self.tab_manager = TabManager(self)
        self.tab_manager.grid(row=0, column=1, sticky="nsew")

        # Terminal panel
        self.terminal = TerminalPanel(self)
        self.terminal.grid(row=1, column=1, sticky="nsew")

        # Gemini panel
        self.gemini_client = GeminiClient()
        self.gemini_panel = GeminiPanel(self, self.gemini_client)
        self.gemini_panel.grid(row=2, column=1, sticky="nsew")

        # Status bar
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky="ew")

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

        self.create_menu()
        self.update_status_bar()

        # Bind events
        self.tab_manager.text_area.bind("<KeyRelease>", self.update_status_bar)
        self.tab_manager.text_area.bind("<Button-1>", self.update_status_bar)

    def create_menu(self):
        self.menu_bar = tkinter.Menu(self)
        self.config(menu=self.menu_bar)

        menu_structure = {
            "File": [
                ("New Tab", lambda: self.tab_manager.new_tab()),
                ("Open", self.open_file),
                ("Save", self.save_file),
                ("Save As", self.save_file_as),
                "separator",
                ("Close Tab", lambda: self.tab_manager.close_tab(self.tab_manager.current_tab_index)),
                "separator",
                ("Exit", self.quit)
            ],
            "Edit": [
                ("Find and Replace", self.open_find_replace_window),
                ("Search in Project...", self.open_project_search),
                "separator",
                ("Goto Definition (F12)", self.handle_goto_definition),
                ("Find References", self.find_references),
                "separator",
                ("Autocomplete", self.tab_manager.text_area.get_completions)
            ],
            "View": [
                ("Toggle Terminal", self.toggle_terminal),
                ("Toggle Gemini Panel", self.toggle_gemini),
                "separator",
                ("Light Theme", lambda: self.set_theme("light")),
                ("Dark Theme", lambda: self.set_theme("dark"))
            ],
            "AI Assistant": [
                ("Explain Code", self.ai_explain_code),
                ("Generate Code...", self.ai_generate_code),
                "separator",
                ("Refactor Code", self.ai_refactor_code),
                ("Fix Errors...", self.ai_fix_errors),
                ("Optimize Code", self.ai_optimize_code),
                "separator",
                ("Generate Docstring", self.ai_generate_docstring),
                ("Translate Code...", self.ai_translate_code),
                "separator",
                ("Create File...", self.ai_create_file),
                ("Modify Current File...", self.ai_modify_current_file),
                ("Add Function...", self.ai_add_function)
            ]
        }

        for menu_label, items in menu_structure.items():
            menu = tkinter.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label=menu_label, menu=menu)

            for item in items:
                if item == "separator":
                    menu.add_separator()
                else:
                    label, command = item
                    menu.add_command(label=label, command=command)

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
        find_window = FindReplaceWindow(self, self.tab_manager.text_area)
        find_window.grab_set()

    def set_theme(self, theme):
        customtkinter.set_appearance_mode(theme)

    def open_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename()

        if file_path:
            try:
                # Create new tab or use current
                tab_index = self.tab_manager.new_tab(file_path)
                tab = self.tab_manager.tabs[tab_index]

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tab.file_path = file_path
                tab.content = content
                self.tab_manager.switch_tab(tab_index)

                self.current_file = file_path
                self.title(f"NanoEditor v2.0 - {file_path}")
                self.status_bar.set_file_path(file_path)
                self.terminal.set_working_directory(os.path.dirname(file_path))

            except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
                messagebox.showerror("Error", f"Cannot open file: {e}")

    def save_file(self):
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            self.save_file_as()
            return

        try:
            content = self.tab_manager.text_area.get("1.0", "end-1c")
            with open(tab.file_path, "w", encoding="utf-8") as f:
                f.write(content)
            tab.modified = False
            tab.content = content
            self.tab_manager.update_tab_title()
        except (PermissionError, OSError) as e:
            messagebox.showerror("Error", f"Cannot save file: {e}")

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename()
        if file_path:
            tab = self.tab_manager.get_current_tab()
            if tab:
                tab.file_path = file_path
                self.save_file()

    def update_status_bar(self, event=None):
        try:
            cursor_pos = self.tab_manager.text_area.index(customtkinter.INSERT)
            line, col = cursor_pos.split('.')
            self.status_bar.set_line_col(line, int(col) + 1)
        except:
            pass

    def _get_selected_text(self):
        try:
            return self.tab_manager.text_area.get("sel.first", "sel.last")
        except tkinter.TclError:
            return self.tab_manager.text_area.get("1.0", "end-1c")

    def _insert_text_at_cursor(self, text):
        try:
            self.tab_manager.text_area.insert(customtkinter.INSERT, text)
        except tkinter.TclError:
            pass

    def _show_ai_result(self, title, result, allow_insert=True):
        insert_callback = self._insert_text_at_cursor if allow_insert else None
        dialog = AIResultDialog(self, title, result, insert_callback)
        dialog.grab_set()

    def ai_explain_code(self):
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "No code to explain")
            return
        self.status_bar.set_file_path("AI: Explaining...")
        self.ai_assistant.explain_code(code, lambda r: self._show_ai_result("Explanation", r, False))

    def ai_generate_code(self):
        def on_desc(desc):
            lang = self._detect_language()
            self.status_bar.set_file_path("AI: Generating...")
            self.ai_assistant.generate_code(desc, lang, lambda r: self._show_ai_result("Generated", r))
        AIActionDialog(self, "Generate Code", "Describe code:", on_desc).grab_set()

    def ai_refactor_code(self):
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to refactor")
            return
        self.status_bar.set_file_path("AI: Refactoring...")
        self.ai_assistant.refactor_code(code, lambda r: self._show_ai_result("Refactored", r))

    def ai_fix_errors(self):
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to fix")
            return
        def on_err(err):
            self.status_bar.set_file_path("AI: Fixing...")
            self.ai_assistant.fix_errors(code, err, lambda r: self._show_ai_result("Fixed", r))
        AIActionDialog(self, "Fix Errors", "Error message:", on_err).grab_set()

    def ai_optimize_code(self):
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to optimize")
            return
        self.status_bar.set_file_path("AI: Optimizing...")
        self.ai_assistant.optimize_code(code, lambda r: self._show_ai_result("Optimizations", r, False))

    def ai_generate_docstring(self):
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select function/class")
            return
        self.status_bar.set_file_path("AI: Documenting...")
        self.ai_assistant.generate_docstring(code, lambda r: self._show_ai_result("Docstring", r))

    def ai_translate_code(self):
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to translate")
            return
        def on_lang(lang):
            from_lang = self._detect_language()
            self.status_bar.set_file_path(f"AI: Translating to {lang}...")
            self.ai_assistant.translate_code(code, from_lang, lang, lambda r: self._show_ai_result("Translated", r))
        AIActionDialog(self, "Translate", "Target language:", on_lang).grab_set()

    def _detect_language(self):
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            return "Python"
        ext_map = {".py": "Python", ".js": "JavaScript", ".java": "Java", ".cpp": "C++", ".go": "Go"}
        ext = os.path.splitext(tab.file_path)[1]
        return ext_map.get(ext, "Python")

    def ai_create_file(self):
        def on_input(text):
            lines = text.strip().split('\n', 1)
            filename = lines[0].strip()
            description = lines[1].strip() if len(lines) > 1 else lines[0]

            self.status_bar.set_file_path(f"AI: Creating {filename}...")
            self.ai_file_ops.create_file_from_description(
                description, filename,
                lambda result: messagebox.showinfo("AI File Creation", result)
            )

        dialog = AIActionDialog(
            self, "Create File",
            "Line 1: filename.py\nLine 2: Description of what the file should do",
            on_input
        )
        dialog.grab_set()

    def ai_modify_current_file(self):
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            messagebox.showwarning("No File", "Open a file first")
            return

        def on_instruction(instruction):
            self.status_bar.set_file_path("AI: Modifying file...")
            self.ai_file_ops.modify_file(
                tab.file_path, instruction,
                lambda result: self._handle_file_modification(result)
            )

        dialog = AIActionDialog(
            self, "Modify File",
            "Describe what changes to make:",
            on_instruction
        )
        dialog.grab_set()

    def ai_add_function(self):
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            messagebox.showwarning("No File", "Open a file first")
            return

        def on_description(description):
            self.status_bar.set_file_path("AI: Adding function...")
            self.ai_file_ops.add_function_to_file(
                tab.file_path, description,
                lambda result: self._handle_file_modification(result)
            )

        dialog = AIActionDialog(
            self, "Add Function",
            "Describe the function to add:",
            on_description
        )
        dialog.grab_set()

    def _handle_file_modification(self, result):
        messagebox.showinfo("AI File Modification", result)
        tab = self.tab_manager.get_current_tab()
        if "✅" in result and tab and tab.file_path:
            self.open_file(tab.file_path)
    
    def open_project_search(self):
        """Open project-wide search window."""
        workspace = os.path.dirname(self.tab_manager.get_current_tab().file_path) if self.tab_manager.get_current_tab() and self.tab_manager.get_current_tab().file_path else os.getcwd()
        search_window = ProjectSearchWindow(self, workspace, self.open_file_at_line)
        search_window.grab_set()
    
    def open_file_at_line(self, file_path, line_num=1):
        """Open file and jump to specific line."""
        self.open_file(file_path)
        try:
            self.tab_manager.text_area.mark_set(customtkinter.INSERT, f"{line_num}.0")
            self.tab_manager.text_area.see(f"{line_num}.0")
            
            # Highlight line
            self.tab_manager.text_area.tag_remove("highlight", "1.0", "end")
            self.tab_manager.text_area.tag_add("highlight", f"{line_num}.0", f"{line_num}.end")
            self.tab_manager.text_area.tag_config("highlight", background="#3B8ED0")
            self.tab_manager.text_area.after(1500, lambda: self.tab_manager.text_area.tag_remove("highlight", "1.0", "end"))
        except Exception:
            pass
    
    def handle_goto_definition(self):
        """Handle goto definition request."""
        if not self.goto_def.goto_definition():
            self.status_bar.set_file_path("No definition found")
    
    def find_references(self):
        """Find all references to symbol under cursor."""
        references = self.goto_def.find_symbol_references()
        if references:
            result = f"Found {len(references)} references:\n\n"
            for ref in references:
                result += f"{ref.module_path}:{ref.line} - {ref.name}\n"
            messagebox.showinfo("References", result)
        else:
            messagebox.showinfo("References", "No references found")


if __name__ == "__main__":
    app = App()
    app.mainloop()
