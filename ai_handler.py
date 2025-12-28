import os
from tkinter import messagebox
from ai_menu import AIActionDialog, AIResultDialog
from ai_utils import process_ai_code_output

class AIHandler:
    """Mixin or helper for AI Assistant actions in the main App."""
    
    def ai_explain_code(self) -> None:
        if not hasattr(self, 'tab_manager'): return
        code = self._get_selected_text()
        if not code or not code.strip():
            messagebox.showwarning("No Code", "Select code to explain")
            return
        
        if len(code) > 50000:
            messagebox.showwarning("Code Too Long", "Selected code is too long (max 50K chars)")
            return
        
        context = self._get_project_context()
        self.status_bar.set_file_path("AI: Explaining...")
        progress = self.feedback.show_progress("AI analyzing code...")
        self.ai_assistant.explain_code(
            code,
            lambda r: self._handle_ai_result("Explanation", r, False, progress),
            project_context=context
        )

    def ai_generate_code(self) -> None:
        context = self._get_project_context()
        def on_desc(desc: str) -> None:
            lang = self._detect_language()
            self.status_bar.set_file_path("AI: Generating...")
            self.ai_assistant.generate_code(
                desc, lang,
                lambda r: self._show_ai_result("Generated", r),
                project_context=context
            )
        AIActionDialog(self, "Generate Code", "Describe code:", on_desc).grab_set()

    def ai_refactor_code(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to refactor")
            return
        context = self._get_project_context()
        self.status_bar.set_file_path("AI: Refactoring...")
        self.ai_assistant.refactor_code(
            code,
            lambda r: self._show_ai_result("Refactored", r),
            project_context=context
        )

    def ai_fix_errors(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to fix")
            return
        context = self._get_project_context()
        def on_err(err: str) -> None:
            self.status_bar.set_file_path("AI: Fixing...")
            self.ai_assistant.fix_errors(
                code, err,
                lambda r: self._show_ai_result("Fixed", r),
                project_context=context
            )
        AIActionDialog(self, "Fix Errors", "Error message:", on_err).grab_set()

    def ai_optimize_code(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to optimize")
            return
        context = self._get_project_context()
        self.status_bar.set_file_path("AI: Optimizing...")
        self.ai_assistant.optimize_code(
            code,
            lambda r: self._show_ai_result("Optimizations", r, False),
            project_context=context
        )

    def ai_generate_docstring(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select function/class")
            return
        context = self._get_project_context()
        self.status_bar.set_file_path("AI: Documenting...")
        self.ai_assistant.generate_docstring(
            code,
            lambda r: self._show_ai_result("Docstring", r),
            project_context=context
        )

    def ai_translate_code(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to translate")
            return
        context = self._get_project_context()
        def on_lang(lang: str) -> None:
            from_lang = self._detect_language()
            self.status_bar.set_file_path(f"AI: Translating to {lang}...")
            self.ai_assistant.translate_code(
                code, from_lang, lang,
                lambda r: self._show_ai_result("Translated", r),
                project_context=context
            )
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

    def ai_create_project(self) -> None:
        """Create a complete project structure from description."""
        def on_description(description: str) -> None:
            self.status_bar.set_file_path("AI: Creating project structure...")
            self.ai_file_ops.create_project_structure(
                description,
                lambda result: messagebox.showinfo("AI Project Creation", result)
            )
        AIActionDialog(
            self, "Create Project",
            "Describe the project you want to create (e.g., 'A simple Flask app with REST API'):",
            on_description
        ).grab_set()

    def _show_ai_result(self, title: str, result: str, allow_insert: bool = True) -> None:
        self.status_bar.set_file_path(f"AI: {title} Complete")
        AIResultDialog(
            self, title, result,
            self._insert_text_at_cursor if allow_insert else None
        ).grab_set()

    def _handle_ai_result(self, title: str, result: str, allow_insert: bool, progress) -> None:
        if progress: progress.stop()
        self.feedback.show_success("AI completed")
        processed_result = process_ai_code_output(result)
        self._show_ai_result(title, processed_result, allow_insert)

    def _handle_file_modification(self, result: str) -> None:
        messagebox.showinfo("AI File Modification", result)
        tab = self.tab_manager.get_current_tab()
        if "✅" in result and tab and tab.file_path:
            self.open_file(tab.file_path)
