import customtkinter
import customtkinter
import tkinter
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

        self.output_text = customtkinter.CTkTextbox(self, font=("monospace", 14), state="disabled")
        self.output_text.grid(row=0, column=0, columnspan=2, sticky="nsew")

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
        
        if not query:
            return
        
        if self.is_processing:
            return
        
        try:
            self.is_processing = True
            self.send_button.configure(state="disabled", text="Sending...")
            self.input_entry.delete(0, "end")
            self.input_entry.configure(state="disabled")
            
            final_query = query
            self.output_text.configure(state="normal")
            # Check if context should be included
            if self.context_checkbox.get():
                self.output_text.insert("1.0", "Gathering project context...\n")
                project_context = self.context_provider()
                final_query = f"{project_context}\n\nBased on the context above, answer the following question:\n\n{query}"
            
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", f"You: {query}\n\n")
            self.output_text.insert("end", "Gemini: Thinking...\n")
            self.output_text.configure(state="disabled")
            
            self.gemini_client.run_gemini(final_query, self.display_response)
        except tkinter.TclError:
            self._reset_ui()

    def display_response(self, response):
        try:
            if not self.winfo_exists():
                return
            
            self.after(0, self._update_response, response)
        except Exception:
            pass
    
    def _update_response(self, response):
        try:
            self.output_text.configure(state="normal")
            content = self.output_text.get("1.0", "end")
            lines = content.split("\n")
            
            if "Thinking..." in content:
                self.output_text.delete("1.0", "end")
                new_content = "\n".join([line for line in lines if "Thinking..." not in line])
                self.output_text.insert("1.0", new_content)
            
            processed_response = process_ai_code_output(response)
            self.output_text.insert("end", f"Gemini: {processed_response}\n")
            self.output_text.configure(state="disabled")
        except tkinter.TclError:
            pass
        finally:
            self._reset_ui()
    
    def _reset_ui(self):
        try:
            self.is_processing = False
            self.send_button.configure(state="normal", text="Send")
            self.input_entry.configure(state="normal")
            self.input_entry.focus_set()
        except tkinter.TclError:
            pass
