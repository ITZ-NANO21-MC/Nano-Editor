"""AI Assistant menu and dialog windows."""
import customtkinter
import tkinter
from tkinter import messagebox


class AIActionDialog(customtkinter.CTkToplevel):
    """Dialog for AI actions that require input."""
    
    def __init__(self, master, title: str, prompt: str, callback):
        super().__init__(master)
        self.callback = callback
        self.title(title)
        self.geometry("500x200")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Label
        label = customtkinter.CTkLabel(self, text=prompt)
        label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Input
        self.input_text = customtkinter.CTkTextbox(self, height=80)
        self.input_text.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Buttons
        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        cancel_btn = customtkinter.CTkButton(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right", padx=5)
        
        ok_btn = customtkinter.CTkButton(btn_frame, text="OK", command=self.on_ok)
        ok_btn.pack(side="right", padx=5)
        
        self.input_text.focus_set()
    
    def on_ok(self):
        text = self.input_text.get("1.0", "end-1c").strip()
        if text:
            self.callback(text)
        self.destroy()


class AIResultDialog(customtkinter.CTkToplevel):
    """Dialog to show AI results with options to insert or copy."""
    
    def __init__(self, master, title: str, result: str, insert_callback=None):
        super().__init__(master)
        self.insert_callback = insert_callback
        self.title(title)
        self.geometry("700x500")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Result text
        self.result_text = customtkinter.CTkTextbox(self, font=("monospace", 12))
        self.result_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.result_text.insert("1.0", result)
        
        # Buttons
        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        close_btn = customtkinter.CTkButton(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side="right", padx=5)
        
        copy_btn = customtkinter.CTkButton(btn_frame, text="Copy", command=self.copy_to_clipboard)
        copy_btn.pack(side="right", padx=5)
        
        if insert_callback:
            insert_btn = customtkinter.CTkButton(
                btn_frame, text="Insert", command=self.insert_result
            )
            insert_btn.pack(side="right", padx=5)
    
    def copy_to_clipboard(self):
        text = self.result_text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Result copied to clipboard")
    
    def insert_result(self):
        if self.insert_callback:
            text = self.result_text.get("1.0", "end-1c")
            self.insert_callback(text)
        self.destroy()


def create_ai_menu(menu_bar, ai_actions):
    """Create AI menu with all assistant actions."""
    ai_menu = tkinter.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="AI Assistant", menu=ai_menu)
    
    ai_menu.add_command(label="Explain Code", command=ai_actions["explain"])
    ai_menu.add_command(label="Generate Code...", command=ai_actions["generate"])
    ai_menu.add_separator()
    ai_menu.add_command(label="Refactor Code", command=ai_actions["refactor"])
    ai_menu.add_command(label="Fix Errors...", command=ai_actions["fix"])
    ai_menu.add_command(label="Optimize Code", command=ai_actions["optimize"])
    ai_menu.add_separator()
    ai_menu.add_command(label="Generate Docstring", command=ai_actions["docstring"])
    ai_menu.add_command(label="Translate Code...", command=ai_actions["translate"])
    
    return ai_menu
