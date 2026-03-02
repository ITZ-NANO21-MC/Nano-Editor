import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from core.refactoring.renamer import Renamer

class RenameDialog(ctk.CTkToplevel):
    """Dialog for previewing and applying symbol renames."""
    def __init__(self, master, editor_view, current_word, code, line, column, file_path):
        super().__init__(master)
        self.title("Rename Symbol")
        self.geometry("500x450")
        self.minsize(400, 300)
        self.after(10, self.lift)
        self.grab_set()

        self.editor_view = editor_view
        self.code = code
        self.line = line
        self.column = column
        self.file_path = file_path
        
        try:
            self.renamer = Renamer()
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))
            self.destroy()
            return
            
        self._build_ui(current_word)

    def _build_ui(self, current_word):
        # Input Frame
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(input_frame, text=f"Rename '{current_word}' to:", font=("Segoe UI", 12)).pack(anchor="w")
        
        self.new_name_var = tk.StringVar(value=current_word)
        self.entry = ctk.CTkEntry(input_frame, textvariable=self.new_name_var, font=("monospace", 12))
        self.entry.pack(fill="x", pady=(5, 0))
        self.entry.select_range(0, tk.END)
        self.entry.focus_set()
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(btn_frame, text="Preview", width=80, command=self._on_preview).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Apply", width=80, fg_color="#007ACC", command=self._on_apply).pack(side="left")
        ctk.CTkButton(btn_frame, text="Cancel", width=80, fg_color="transparent", border_width=1, command=self.destroy).pack(side="right")
        
        # Preview Area
        ctk.CTkLabel(self, text="Preview Changes:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10)
        self.preview_text = ctk.CTkTextbox(self, font=("monospace", 11), state="disabled", wrap="none")
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _on_preview(self):
        new_name = self.new_name_var.get().strip()
        if not new_name:
            return
            
        result = self.renamer.compute_rename(self.code, self.line, self.column, new_name, self.file_path)
        
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        
        if not result or result.files_affected == 0:
            self.preview_text.insert("end", "No changes found or rename not possible.")
            self.preview_text.configure(state="disabled")
            return
            
        summary = f"Files affected: {result.files_affected}, Replacements: {result.total_replacements}\n\n"
        self.preview_text.insert("end", summary)
        
        for fpath, changes in result.changes.items():
            fname = fpath.split('/')[-1]
            self.preview_text.insert("end", f"── {fname} ──\n")
            for ln, old_c, new_c in changes:
                self.preview_text.insert("end", f" Line {ln}:\n")
                self.preview_text.insert("end", f" - {old_c}\n")
                self.preview_text.insert("end", f" + {new_c}\n\n")
                
        self.preview_text.configure(state="disabled")

    def _on_apply(self):
        new_name = self.new_name_var.get().strip()
        if not new_name:
            return
            
        new_code = self.renamer.apply_rename(self.code, self.line, self.column, new_name, self.file_path)
        if new_code is not None:
            # We only handle single-file updates here based on apply_rename logic
            text_area = self.editor_view.tab_manager.text_area
            # Save scroll position
            yview = text_area.yview()
            text_area.delete("1.0", "end")
            text_area.insert("1.0", new_code)
            text_area.yview_moveto(yview[0])
            if hasattr(self.editor_view.app, 'feedback'):
                self.editor_view.app.feedback.show_success("Renamed successfully")
        else:
            messagebox.showerror("Error", "Rename failed.")
            
        self.destroy()
