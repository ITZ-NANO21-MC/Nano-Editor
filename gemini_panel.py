import customtkinter
import tkinter
import threading
import datetime
import re
from typing import Callable, Optional
from ai_utils import process_ai_code_output, clean_ai_json_response
from tkfontawesome import icon_to_image
from syntax_highlighter import SyntaxHighlighter


class CodeBlockFrame(customtkinter.CTkFrame):
    """A container for code blocks with copy/insert actions."""
    def __init__(self, master, code: str = "", language: str = "python", app=None):
        theme = customtkinter.get_appearance_mode()
        bg_color = ("#F0F0F0", "#1E1E1E")
        header_color = ("#E5E5E5", "#2D2D2D")
        
        super().__init__(master, fg_color=bg_color, corner_radius=6)
        self.code = code
        self.app = app
        self.language = language
        
        # Header
        self.header = customtkinter.CTkFrame(self, fg_color=header_color, height=30, corner_radius=6)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        self.lang_label = customtkinter.CTkLabel(
            self.header, text=language.upper() or "CODE",
            font=("Segoe UI", 10, "bold"),
            text_color=("#666666", "#999999")
        )
        self.lang_label.pack(side="left", padx=10)
        
        # Buttons
        self.btn_frame = customtkinter.CTkFrame(self.header, fg_color="transparent")
        self.btn_frame.pack(side="right", padx=5)
        
        self.copy_btn = customtkinter.CTkButton(
            self.btn_frame, text="📋 Copy", width=50, height=22,
            font=("Segoe UI", 10),
            fg_color="#007ACC", hover_color="#005A9E",
            command=self.copy_code
        )
        self.copy_btn.pack(side="left", padx=2)
        
        self.insert_btn = customtkinter.CTkButton(
            self.btn_frame, text="➕ Insert", width=50, height=22,
            font=("Segoe UI", 10),
            fg_color="#007ACC", hover_color="#005A9E",
            command=self.insert_code
        )
        self.insert_btn.pack(side="left", padx=2)
        
        # Text box
        self.text_box = customtkinter.CTkTextbox(
            self, font=("monospace", 12),
            height=150,
            fg_color="transparent",
            text_color=("#333333", "#E0E0E0"),
            border_width=0
        )
        self.text_box.pack(fill="both", expand=True, padx=5, pady=5)
        
        if code:
            self.text_box.insert("1.0", code)
            
        self.highlighter = SyntaxHighlighter(self.text_box, style="monokai" if theme == "Dark" else "friendly")

    def append_text(self, text: str):
        self.text_box.insert("end", text)
        self.text_box.see("end")
        
    def finalize(self):
        """Called when code block is complete."""
        text = self.text_box.get("1.0", "end-1c")
        # Clean any surrounding markdown or quotes that might have slipped in
        cleaned_text = process_ai_code_output(f"```{self.language}\n{text}\n```")
        if not cleaned_text or cleaned_text.strip() == "":
             cleaned_text = text.strip()
             
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", cleaned_text)
        self.code = cleaned_text
        self.highlighter.highlight(f"temp.{self.language or 'py'}")
        self.text_box.configure(state="disabled")

    def copy_code(self):
        code = self.text_box.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(code)
        if self.app and hasattr(self.app, 'feedback'):
            self.app.feedback.show_success("Code copied")

    def insert_code(self):
        code = self.text_box.get("1.0", "end-1c")
        if self.app and hasattr(self.app, 'tab_manager'):
            text_area = self.app.tab_manager.text_area
            text_area.insert(customtkinter.INSERT, code)
            if self.app and hasattr(self.app, 'feedback'):
                self.app.feedback.show_success("Inserted into editor")


class GeminiPanel(customtkinter.CTkFrame):
    def __init__(self, master, gemini_client, context_provider: Callable[[], str], app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.gemini_client = gemini_client
        self.context_provider = context_provider
        self.is_processing = False
        self.chat_history = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create scrollable messages container
        self.content = customtkinter.CTkScrollableFrame(
            self, 
            fg_color=("#FFFFFF", "#1E1E1E"),
            scrollbar_button_color=("#CCCCCC", "#3E3E3E"),
            scrollbar_button_hover_color=("#BBBBBB", "#4E4E4E")
        )
        self.content.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Keep track of message widgets
        self.message_parts = []
        self.current_part = None
        self.current_mode = "TEXT" # "TEXT" or "CODE"
        self.code_buffer = ""
        self.backtick_count = 0
        


        # Input Frame
        input_frame = customtkinter.CTkFrame(self)
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = customtkinter.CTkEntry(
            input_frame, 
            placeholder_text="Ask Gemini AI...",
            height=35,
            font=("Segoe UI", 12)
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self.send_query())

        self.send_button = customtkinter.CTkButton(
            input_frame, 
            text="Send", 
            command=self.send_query, 
            width=80,
            height=35,
            font=("Segoe UI", 12, "bold")
        )
        self.send_button.grid(row=0, column=1, sticky="ew")

        # Context checkbox with better styling
        self.context_checkbox = customtkinter.CTkCheckBox(
            self, 
            text="Include Context", 
            font=("Segoe UI", 11),
            checkbox_width=16,
            checkbox_height=16
        )
        self.context_checkbox.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))

        # Project Mode checkbox
        self.project_mode_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Project Mode",
            font=("Segoe UI", 11),
            checkbox_width=16,
            checkbox_height=16,
            text_color="#FF9800" # Orange to highlight it
        )
        self.project_mode_checkbox.grid(row=2, column=0, sticky="w", padx=(130, 0), pady=(0, 10))

        # Setup scrolling
        self._setup_mousewheel_scrolling()

        # Add clear chat button
        self.clear_button = customtkinter.CTkButton(
            self,
            text="Clear Chat",
            command=self.clear_chat,
            width=80,
            height=28,
            font=("Segoe UI", 11),
            fg_color="transparent",
            border_width=1,
            border_color=("#CCCCCC", "#555555")
        )
        self.clear_button.grid(row=2, column=1, sticky="e", padx=10, pady=(0, 10))

        # Add initial welcome message
        self._append_message("🤖 Gemini AI Assistant\nType your questions about code, debugging, or programming concepts.\n\n", "system")

    def send_query(self):
        """Send query to Gemini AI with optional project context."""
        query = self.input_entry.get().strip()
        if not query or self.is_processing:
            return

        # Store in history
        self.chat_history.append({"role": "user", "content": query})

        self.is_processing = True
        self.send_button.configure(state="disabled", text="Thinking...")
        self.input_entry.delete(0, "end")
        self.input_entry.configure(state="disabled")
        self.context_checkbox.configure(state="disabled")
        self.project_mode_checkbox.configure(state="disabled")

        # Append user message to chat history
        self._append_message(f"You: {query}\n\n", "user")

        # Prepare query (with context if needed)
        final_query = query
        if self.context_checkbox.get():
            try:
                project_context = self.context_provider()
                final_query = f"{project_context}\n\nBased on the project context above, answer the following question:\n\n{query}"
                self._append_message("📁 Including project context in this query...\n", "system")
            except Exception as e:
                self._append_message(f"⚠️ Failed to load project context: {str(e)}\n", "error")

        if self.project_mode_checkbox.get():
            self._append_message("🏗️ Project Creation Mode ACTIVE...\n", "system")
            project_inst = """
IMPORTANT: You are in PROJECT CREATION MODE.
Instead of a normal conversation, you MUST return a valid JSON structure representing the files for this project.
FORMAT:
{
  "files": [
    {"path": "filename.py", "content": "file content..."},
    {"path": "subdir/file2.py", "content": "..."}
  ]
}
Return ONLY the JSON. No explanations before or after.
"""
            final_query = f"{project_inst}\n\nUSER REQUEST: {query}"
        thread = threading.Thread(target=self._stream_worker, args=(final_query,), daemon=True)
        thread.start()

    def _stream_worker(self, query: str):
        """Worker function to be run in a separate thread to handle streaming."""
        try:
            # Store response for history
            full_response = ""
            
            # Process stream
            self.current_mode = "TEXT"
            self.backtick_count = 0
            self.delimiter_char = '`'
            
            # Start Gemini response with a label
            self.after(0, lambda: self._start_new_part("gemini", text="Gemini: ", bold=True))

            project_mode = self.project_mode_checkbox.get()
            if project_mode:
                self.after(0, lambda: self._append_message("🏗️ Project Creation Mode ACTIVE. Generating structure...\n", "system"))

            for chunk in self.gemini_client.run_gemini_stream(query):
                if chunk:
                    full_response += chunk
                    if not project_mode:
                        self.after(0, self._process_stream_chunk, chunk)

            # Finalize last part
            if not project_mode:
                self.after(0, self._finalize_current_part)

            # Store in history
            self.chat_history.append({"role": "gemini", "content": full_response})
            
            # Add final newlines for separation
            self.after(0, self._append_message, "\n\n", "gemini")

                # If project mode, apply changes
            if self.project_mode_checkbox.get() and self.app:
                def _on_project_done(result, files_data):
                    self.after(0, lambda: self._append_message(f"\n{result}\n", "system"))
                    # Render files in chat if successful
                    if files_data:
                        for file_info in files_data:
                            path = file_info.get('path', 'unknown')
                            content = file_info.get('content', '')
                            lang = self.app.ai_file_ops._detect_language_from_filename(path)
                            
                            self.after(0, lambda p=path, c=content, l=lang: self._render_file_block(p, c, l))

                    # Refresh file tree if possible
                    if self.app and hasattr(self.app, 'file_tree'):
                         self.after(0, self.app.file_tree.refresh)

                # Generate a unique folder name
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                folder_name = f"project_{timestamp}"
                
                self.app.ai_file_ops.apply_project_structure_from_response(
                    full_response, 
                    _on_project_done,
                    folder_name=folder_name
                )

        except Exception as e:
            error_msg = f"\n❌ Error: {str(e)}\n\n"
            self.after(0, self._append_message, error_msg, "error")
            self.chat_history.append({"role": "error", "content": str(e)})
        finally:
            # Reset UI on the main thread
            self.after(0, self._reset_ui)

    def _render_file_block(self, path: str, content: str, lang: str):
        """Render a file as a code block in the chat."""
        self._start_new_part("system", text=f"📄 {path}", bold=True)
        block = CodeBlockFrame(self.content, code=content, language=lang, app=self.app)
        block.pack(fill="x", padx=10, pady=5)
        block.finalize()
        self._bind_mousewheel_to_widgets(block)
        self._scroll_to_bottom()

    def _process_stream_chunk(self, chunk: str):
        """Process chunk and handle text/code transitions."""
        for char in chunk:
            if char in ['`', "'", '´']:
                if self.backtick_count == 0:
                    self.delimiter_char = char
                    self.backtick_count = 1
                elif char == self.delimiter_char:
                    self.backtick_count += 1
                    if self.backtick_count == 3:
                        # Transition
                        self._handle_mode_transition()
                        self.backtick_count = 0
                else:
                    # Mixed delimiters, treat previous as text
                    self._append_to_current_part(self.delimiter_char * self.backtick_count)
                    self.delimiter_char = char
                    self.backtick_count = 1
                continue
            else:
                if self.backtick_count > 0:
                    # Not a transition, append the held delimiters
                    self._append_to_current_part(self.delimiter_char * self.backtick_count)
                    self.backtick_count = 0
                self._append_to_current_part(char)

    def _handle_mode_transition(self):
        """Toggle between TEXT and CODE mode."""
        self._finalize_current_part()
        if self.current_mode == "TEXT":
            self.current_mode = "CODE"
            # We'll default to python and let finalize clean it up
            self.current_part = CodeBlockFrame(self.content, language="python", app=self.app)
            self.current_part.pack(fill="x", padx=10, pady=5)
            self._bind_mousewheel_to_widgets(self.current_part)
        else:
            self.current_mode = "TEXT"
            self._start_new_part("gemini")

    def _start_new_part(self, tag: str, text: str = "", bold: bool = False):
        """Start a new text part."""
        color = ("#333333", "#E0E0E0")
        if tag == "user": color = ("#0066CC", "#4A9EFF")
        elif tag == "system": color = "#888888"
        elif tag == "error": color = "#FF5555"
        
        font = ("Segoe UI", 12)
        if bold: font = ("Segoe UI", 12, "bold")
        
        part = customtkinter.CTkLabel(
            self.content, text=text, 
            font=font, text_color=color,
            wraplength=250, justify="left",
            anchor="w"
        )
        part.pack(fill="x", padx=10, pady=2)
        self._bind_mousewheel_to_widgets(part)
        self.current_part = part
        self.message_parts.append(part)
        self._scroll_to_bottom()

    def _append_to_current_part(self, text: str):
        """Append text to current active part."""
        if not self.current_part:
            self._start_new_part("gemini")
            
        if isinstance(self.current_part, customtkinter.CTkLabel):
            current_text = self.current_part.cget("text")
            self.current_part.configure(text=current_text + text)
        elif isinstance(self.current_part, CodeBlockFrame):
            self.current_part.append_text(text)
        
        self._scroll_to_bottom()

    def _finalize_current_part(self):
        """Finalize the current part (e.g. apply highlighting)."""
        if isinstance(self.current_part, CodeBlockFrame):
            self.current_part.finalize()
        self.current_part = None

    def _scroll_to_bottom(self):
        """Scroll message list to bottom."""
        try:
            self.content._parent_canvas.yview_moveto(1.0)
        except:
            pass

    def _append_message(self, text: str, tag: str = None):
        """Legacy support for initial messages."""
        self._start_new_part(tag or "system", text=text)

    def _append_chunk(self, chunk: str):
        """No longer used, replaced by _process_stream_chunk."""
        pass

    def _reset_ui(self):
        """Resets the UI to its initial state after a query is complete."""
        try:
            self.is_processing = False
            self.send_button.configure(state="normal", text="Send")
            self.input_entry.configure(state="normal")
            self.context_checkbox.configure(state="normal")
            self.project_mode_checkbox.configure(state="normal")
            self.input_entry.focus_set()
        except tkinter.TclError:
            pass

    def clear_chat(self):
        """Clear the chat history and display."""
        try:
            for widget in self.content.winfo_children():
                widget.destroy()
            
            # Clear history
            self.chat_history = []
            
            # Add welcome message back
            self._append_message("🤖 Gemini AI Assistant\nType your questions about code, debugging, or programming concepts.\n\n", "system")
            
        except tkinter.TclError:
            pass

    def get_chat_history(self):
        """Return the chat history for context."""
        return self.chat_history.copy()

    def _setup_mousewheel_scrolling(self):
        """Setup proper mousewheel scrolling for the panel."""
        self._bind_mousewheel_to_widgets(self.content)

    def _bind_mousewheel_to_widgets(self, widget):
        """Recursively bind mousewheel events to all child widgets."""
        widget.bind("<MouseWheel>", self._forward_to_scrollable)
        widget.bind("<Button-4>", self._forward_to_scrollable)
        widget.bind("<Button-5>", self._forward_to_scrollable)
        
        for child in widget.winfo_children():
            if not isinstance(child, customtkinter.CTkScrollableFrame):
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

    def update_theme(self):
        """Update colors when theme changes."""
        # Standard widgets handle theme changes automatically with Tuple colors
        pass
