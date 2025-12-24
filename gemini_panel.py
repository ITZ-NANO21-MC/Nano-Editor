import customtkinter
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

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.output_text = customtkinter.CTkTextbox(self, font=("monospace", 14), state="disabled", wrap="word")
        self.output_text.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Configure tags for chat roles
        gemini_color = "#D3D3D3" if customtkinter.get_appearance_mode() == "Dark" else "#333333"
        self.output_text.tag_config("user", foreground="#4A9EFF")
        self.output_text.tag_config("gemini", foreground=gemini_color)
        self.output_text.tag_config("error", foreground="#FF5555")

        # Input Frame
        input_frame = customtkinter.CTkFrame(self)
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = customtkinter.CTkEntry(input_frame, placeholder_text="Ask Gemini...")
        self.input_entry.grid(row=0, column=0, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self.send_query())

        self.send_button = customtkinter.CTkButton(input_frame, text="Send", command=self.send_query, width=70)
        self.send_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.context_checkbox = customtkinter.CTkCheckBox(self, text="Include Project Context", font=("Segoe UI", 12))
        self.context_checkbox.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 5))

    def send_query(self):
        query = self.input_entry.get().strip()
        if not query or self.is_processing:
            return

        self.is_processing = True
        self.send_button.configure(state="disabled", text="...")
        self.input_entry.delete(0, "end")
        self.input_entry.configure(state="disabled")

        # Append user message to chat history
        self._append_message(f"You: {query}\n\n", "user")

        # Prepare query (with context if needed)
        final_query = query
        if self.context_checkbox.get():
            project_context = self.context_provider()
            final_query = f"{project_context}\n\nBased on the context above, answer the following question:\n\n{query}"

        # Start background thread for streaming response
        thread = threading.Thread(target=self._stream_worker, args=(final_query,), daemon=True)
        thread.start()

    def _stream_worker(self, query: str):
        """Worker function to be run in a separate thread to handle streaming."""
        try:
            # Add Gemini's prefix
            self.after(0, self._append_message, "Gemini: ", "gemini")
            
            # Process stream
            full_response = ""
            for chunk in self.gemini_client.run_gemini_stream(query):
                full_response += chunk
                self.after(0, self._append_chunk, chunk)

            # Clean up the response (e.g., remove markdown) and add final newline
            # This part is optional if real-time processing is perfect
            self.after(0, self._append_message, "\n\n", "gemini")

        except Exception as e:
            self.after(0, self._append_message, f"\nAn error occurred: {e}\n\n", "error")
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

    def _append_message(self, text: str, tag: str):
        """Safely appends a full message with a specific tag."""
        if not self.winfo_exists():
            return
        try:
            self.output_text.configure(state="normal")
            start_index = self.output_text.index("end-1c")
            self.output_text.insert("end", text)
            end_index = self.output_text.index("end-1c")
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
            self.input_entry.focus_set()
        except tkinter.TclError:
            pass
