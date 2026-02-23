import os
from tkinter import messagebox
from ai_menu import AIActionDialog, AIResultDialog
from ai.utils import process_ai_code_output, strip_markdown_formatting

class AIHandler:
    """Mixin or helper for AI Assistant actions in the main App."""
    
    def _start_streaming_action(self, title: str, allow_insert: bool = True, readonly: bool = False, post_process=None):
        """Helper to start a streaming AI action and return the callback.
        
        Args:
            title: Title for the dialog and status bar.
            allow_insert: If True, adds an 'Insert' button to paste code into editor.
            readonly: If True, the dialog text is not editable.
            post_process: Optional callable to clean the full text after streaming completes.
        """
        def insert_cb(text):
            # Clean code if it's meant for insertion into editor
            cleaned_text = process_ai_code_output(text) if allow_insert else text
            self._insert_text_at_cursor(cleaned_text)
            
        dialog = AIResultDialog(
            self, f"{title} (Streaming)", "", 
            insert_cb if allow_insert else None,
            readonly=readonly
        )
        dialog.grab_set()
        
        self.status_bar.set_file_path(f"AI: {title}...")
        
        def on_chunk(chunk):
            if chunk is None:
                # Post-process: clean up full text when streaming is done
                if post_process:
                    try:
                        if readonly:
                            dialog.result_text.configure(state="normal")
                        raw_text = dialog.result_text.get("1.0", "end-1c")
                        cleaned = post_process(raw_text)
                        dialog.result_text.delete("1.0", "end")
                        dialog.result_text.insert("1.0", cleaned)
                        if readonly:
                            dialog.result_text.configure(state="disabled")
                    except Exception:
                        pass
                self.status_bar.set_file_path(f"AI: {title} Complete")
                self.feedback.show_success("AI completed")
            else:
                dialog.append_text(chunk)
                
        return on_chunk

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
        on_chunk = self._start_streaming_action("Explaining", allow_insert=False, readonly=True, post_process=strip_markdown_formatting)
        self.ai_assistant.explain_code(code, on_chunk, project_context=context, stream=True)

    def ai_generate_code(self) -> None:
        context = self._get_project_context()
        def on_desc(desc: str) -> None:
            lang = self._detect_language()
            on_chunk = self._start_streaming_action("Generating", allow_insert=True)
            self.ai_assistant.generate_code(
                desc, lang,
                on_chunk,
                project_context=context,
                stream=True
            )
        AIActionDialog(self, "Generate Code", "Describe code:", on_desc).grab_set()

    def ai_refactor_code(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to refactor")
            return
        context = self._get_project_context()
        on_chunk = self._start_streaming_action("Refactoring", allow_insert=True)
        self.ai_assistant.refactor_code(
            code,
            on_chunk,
            project_context=context,
            stream=True
        )

    def ai_fix_errors(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to fix")
            return
        context = self._get_project_context()
        def on_err(err: str) -> None:
            on_chunk = self._start_streaming_action("Fixing", allow_insert=True)
            self.ai_assistant.fix_errors(
                code, err,
                on_chunk,
                project_context=context,
                stream=True
            )
        AIActionDialog(self, "Fix Errors", "Error message:", on_err).grab_set()

    def ai_optimize_code(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to optimize")
            return
        context = self._get_project_context()
        on_chunk = self._start_streaming_action("Optimizing", allow_insert=True, post_process=strip_markdown_formatting)
        self.ai_assistant.optimize_code(
            code,
            on_chunk,
            project_context=context,
            stream=True
        )

    def ai_generate_docstring(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select function/class")
            return
        context = self._get_project_context()
        on_chunk = self._start_streaming_action("Documenting", allow_insert=True)
        self.ai_assistant.generate_docstring(
            code,
            on_chunk,
            project_context=context,
            stream=True
        )

    def ai_translate_code(self) -> None:
        code = self._get_selected_text()
        if not code.strip():
            messagebox.showwarning("No Code", "Select code to translate")
            return
        context = self._get_project_context()
        def on_lang(lang: str) -> None:
            from_lang = self._detect_language()
            on_chunk = self._start_streaming_action(f"Translating to {lang}", allow_insert=True)
            self.ai_assistant.translate_code(
                code, from_lang, lang,
                on_chunk,
                project_context=context,
                stream=True
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
