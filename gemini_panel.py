import customtkinter
import tkinter


class GeminiPanel(customtkinter.CTkFrame):
    def __init__(self, master, gemini_client, **kwargs):
        super().__init__(master, **kwargs)
        self.gemini_client = gemini_client
        self.is_processing = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.output_text = customtkinter.CTkTextbox(self, font=("monospace", 14))
        self.output_text.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.input_entry = customtkinter.CTkEntry(self, placeholder_text="Ask Gemini...")
        self.input_entry.grid(row=1, column=0, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self.send_query())

        self.send_button = customtkinter.CTkButton(self, text="Send", command=self.send_query)
        self.send_button.grid(row=1, column=1, sticky="ew")

    def send_query(self):
        query = self.input_entry.get().strip()
        
        if not query:
            return
        
        if self.is_processing:
            return
        
        try:
            self.is_processing = True
            self.send_button.configure(state="disabled", text="Sending...")
            self.input_entry.configure(state="disabled")
            
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", f"You: {query}\n\n")
            self.output_text.insert("end", "Gemini: Thinking...\n")
            
            self.input_entry.delete(0, "end")
            
            self.gemini_client.run_gemini(query, self.display_response)
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
            content = self.output_text.get("1.0", "end")
            lines = content.split("\n")
            
            if "Thinking..." in content:
                self.output_text.delete("1.0", "end")
                new_content = "\n".join([line for line in lines if "Thinking..." not in line])
                self.output_text.insert("1.0", new_content)
            
            self.output_text.insert("end", f"Gemini: {response}\n")
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
