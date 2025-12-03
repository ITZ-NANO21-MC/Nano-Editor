import customtkinter
import tkinter
from tkinter import filedialog, messagebox
from text_area import CodeEditor
from line_numbers import LineNumbers
from file_tree import FileTree
from gemini_panel import GeminiPanel
from gemini_client import GeminiClient
from status_bar import StatusBar
from find_replace import FindReplaceWindow
from ai_assistant import AIAssistant
from ai_menu import create_ai_menu, AIActionDialog, AIResultDialog
from ai_file_operations import AIFileOperations
import os


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("NanoEditor")
        self.geometry("1200x768")
        self.current_file = None

        # set grid layout 3 rows, 3 columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self.file_tree = FileTree(self)
        self.file_tree.grid(row=0, column=0, sticky="ns")

        self.line_numbers = LineNumbers(self, text_widget=None)
        self.line_numbers.grid(row=0, column=1, sticky="ns")
        
        self.text_area = CodeEditor(self)
        self.text_area.grid(row=0, column=2, sticky="nsew")

        self.line_numbers.text_widget = self.text_area
        self.text_area.set_line_numbers(self.line_numbers)

        self.gemini_client = GeminiClient()
        self.gemini_panel = GeminiPanel(self, self.gemini_client)
        self.gemini_panel.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky="ew")

        self.ai_assistant = AIAssistant()
        self.ai_file_ops = AIFileOperations(os.path.dirname(self.current_file) if self.current_file else os.getcwd())
        
        self.create_menu()
        self.update_status_bar()

        self.text_area.bind("<KeyRelease>", self.update_status_bar)
        self.text_area.bind("<Button-1>", self.update_status_bar)

    def create_menu(self):
        self.menu_bar = tkinter.Menu(self)
        self.config(menu=self.menu_bar)

        menu_structure = {
            "File": [
                ("Open", self.open_file),
                ("Save", self.save_file),
                "separator",
                ("Exit", self.quit)
            ],
            "Edit": [
                ("Find and Replace", self.open_find_replace_window),
                "separator",
                ("Autocomplete", self.text_area.get_completions)
            ],
            "Theme": [
                ("Light", lambda: self.set_theme("light")),
                ("Dark", lambda: self.set_theme("dark"))
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

    def open_find_replace_window(self):
        find_window = FindReplaceWindow(self, self.text_area)
        find_window.grab_set()

    def set_theme(self, theme):
        customtkinter.set_appearance_mode(theme)

    def open_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename()
        
        if file_path:
            try:
                self.current_file = file_path
                self.text_area.file_path = file_path
                with open(file_path, "r", encoding="utf-8") as f:
                    self.text_area.delete("1.0", "end")
                    self.text_area.insert("1.0", f.read())
                self.title(f"NanoEditor - {self.current_file}")
                self.status_bar.set_file_path(self.current_file)
                self.text_area.on_text_changed()
                self.text_area.highlight_text()
                self.update_status_bar()
            except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
                tkinter.messagebox.showerror("Error", f"Cannot open file: {e}")
                self.current_file = None

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get("1.0", "end-1c"))
            except (PermissionError, OSError) as e:
                tkinter.messagebox.showerror("Error", f"Cannot save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename()
        if file_path:
            try:
                self.current_file = file_path
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get("1.0", "end-1c"))
                self.title(f"NanoEditor - {self.current_file}")
                self.status_bar.set_file_path(self.current_file)
            except (PermissionError, OSError) as e:
                tkinter.messagebox.showerror("Error", f"Cannot save file: {e}")
                self.current_file = None

    def update_status_bar(self, event=None):
        cursor_pos = self.text_area.index(customtkinter.INSERT)
        line, col = cursor_pos.split('.')
        self.status_bar.set_line_col(line, int(col) + 1)
    
    def _get_selected_text(self):
        try:
            return self.text_area.get("sel.first", "sel.last")
        except tkinter.TclError:
            return self.text_area.get("1.0", "end-1c")
    
    def _insert_text_at_cursor(self, text):
        try:
            self.text_area.insert(customtkinter.INSERT, text)
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
        if not self.current_file:
            return "Python"
        ext_map = {".py": "Python", ".js": "JavaScript", ".java": "Java", ".cpp": "C++", ".go": "Go"}
        ext = os.path.splitext(self.current_file)[1]
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
        if not self.current_file:
            messagebox.showwarning("No File", "Open a file first")
            return
        
        def on_instruction(instruction):
            self.status_bar.set_file_path("AI: Modifying file...")
            self.ai_file_ops.modify_file(
                self.current_file, instruction,
                lambda result: self._handle_file_modification(result)
            )
        
        dialog = AIActionDialog(
            self, "Modify File",
            "Describe what changes to make:",
            on_instruction
        )
        dialog.grab_set()
    
    def ai_add_function(self):
        if not self.current_file:
            messagebox.showwarning("No File", "Open a file first")
            return
        
        def on_description(description):
            self.status_bar.set_file_path("AI: Adding function...")
            self.ai_file_ops.add_function_to_file(
                self.current_file, description,
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
        if "✅" in result and self.current_file:
            self.open_file(self.current_file)


if __name__ == "__main__":
    app = App()
    app.mainloop()