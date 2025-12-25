import customtkinter
import tkinter
import threading
from typing import Callable
from ai_utils import process_ai_code_output


class GeminiPanel(customtkinter.CTkFrame):
    def __init__(self, master, gemini_client, context_provider: Callable[[], str], **kwargs):
        super().__init__(master, **kwargs)
        self.gemini_client = gemini_client
        self.context_provider = context_provider
        self.is_processing = False
        self.chat_history = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create output text widget (read-only chat area)
        self.output_text = customtkinter.CTkTextbox(
            self, 
            font=("Segoe UI", 12),  # Fuente base del widget
            state="disabled", 
            wrap="word",
            fg_color=("#FFFFFF", "#1E1E1E"),
            text_color=("#000000", "#E0E0E0")
        )
        self.output_text.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Configure tags for chat roles - SOLO COLOR, NO FONT
        mode = customtkinter.get_appearance_mode()
        
        # Define colors based on theme
        if mode == "Dark":
            user_color = "#4A9EFF"    # Blue for user messages
            gemini_color = "#D3D3D3"  # Light gray for Gemini responses
            error_color = "#FF5555"   # Red for errors
        else:
            user_color = "#0066CC"    # Darker blue for light theme
            gemini_color = "#333333"  # Dark gray for Gemini responses
            error_color = "#CC0000"   # Darker red for errors
        
        # Configure text tags - SOLO foreground, NO font
        self.output_text.tag_config("user", foreground=user_color)
        self.output_text.tag_config("gemini", foreground=gemini_color)
        self.output_text.tag_config("error", foreground=error_color)
        self.output_text.tag_config("system", foreground="#888888")

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
            text="Include Project Context", 
            font=("Segoe UI", 12),
            checkbox_width=18,
            checkbox_height=18
        )
        self.context_checkbox.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))

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

        # Start background thread for streaming response
        thread = threading.Thread(target=self._stream_worker, args=(final_query,), daemon=True)
        thread.start()

    def _stream_worker(self, query: str):
        """Worker function to be run in a separate thread to handle streaming."""
        try:
            # Store response for history
            full_response = ""
            
            # Add Gemini's prefix
            self.after(0, self._append_message, "Gemini: ", "gemini")
            
            # Process stream
            for chunk in self.gemini_client.run_gemini_stream(query):
                if chunk:
                    full_response += chunk
                    self.after(0, self._append_chunk, chunk)

            # Store in history
            self.chat_history.append({"role": "gemini", "content": full_response})
            
            # Add final newlines for separation
            self.after(0, self._append_message, "\n\n", "gemini")

        except Exception as e:
            error_msg = f"\n❌ Error: {str(e)}\n\n"
            self.after(0, self._append_message, error_msg, "error")
            self.chat_history.append({"role": "error", "content": str(e)})
        finally:
            # Reset UI on the main thread
            self.after(0, self._reset_ui)

    def _append_chunk(self, chunk: str):
        """Safely appends a chunk of text to the output from the main thread."""
        if not self.winfo_exists():
            return
        try:
            self.output_text.configure(state="normal")
            self.output_text.insert("end", chunk)
            self.output_text.see("end")
            self.output_text.configure(state="disabled")
        except tkinter.TclError:
            pass

    def _append_message(self, text: str, tag: str = None):
        """Safely appends a full message with a specific tag."""
        if not self.winfo_exists():
            return
        try:
            self.output_text.configure(state="normal")
            start_index = self.output_text.index("end-1c")
            self.output_text.insert("end", text)
            end_index = self.output_text.index("end-1c")
            
            if tag:
                self.output_text.tag_add(tag, start_index, end_index)
                
            self.output_text.see("end")
            self.output_text.configure(state="disabled")
        except tkinter.TclError:
            pass

    def _reset_ui(self):
        """Resets the UI to its initial state after a query is complete."""
        try:
            self.is_processing = False
            self.send_button.configure(state="normal", text="Send")
            self.input_entry.configure(state="normal")
            self.context_checkbox.configure(state="normal")
            self.input_entry.focus_set()
        except tkinter.TclError:
            pass

    def clear_chat(self):
        """Clear the chat history and display."""
        try:
            self.output_text.configure(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.configure(state="disabled")
            
            # Clear history
            self.chat_history = []
            
            # Add welcome message back
            self._append_message("🤖 Gemini AI Assistant\nType your questions about code, debugging, or programming concepts.\n\n", "system")
            
        except tkinter.TclError:
            pass

    def get_chat_history(self):
        """Return the chat history for context."""
        return self.chat_history.copy()

    def update_theme(self):
        """Update colors when theme changes."""
        mode = customtkinter.get_appearance_mode()
        
        if mode == "Dark":
            user_color = "#4A9EFF"
            gemini_color = "#D3D3D3"
            error_color = "#FF5555"
        else:
            user_color = "#0066CC"
            gemini_color = "#333333"
            error_color = "#CC0000"
        
        # Update text widget colors
        self.output_text.configure(
            fg_color=("#FFFFFF", "#1E1E1E"),
            text_color=("#000000", "#E0E0E0")
        )
        
        # Update tags (solo colores)
        self.output_text.tag_config("user", foreground=user_color)
        self.output_text.tag_config("gemini", foreground=gemini_color)
        self.output_text.tag_config("error", foreground=error_color)
