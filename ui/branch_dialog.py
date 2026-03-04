import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from logger import logger

class BranchDialog(ctk.CTkToplevel):
    """Dialog for managing Git branches."""
    def __init__(self, master, git_manager, on_branch_changed=None):
        super().__init__(master)
        
        self.git_manager = git_manager
        self.on_branch_changed = on_branch_changed
        
        self.title("Branch Manager")
        self.geometry("400x500")
        self.minsize(300, 400)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        ctk.CTkLabel(
            self, text="Git Branches", font=("Segoe UI", 16, "bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Branch List (Scrollable)
        self.branch_scroll = ctk.CTkScrollableFrame(self)
        self.branch_scroll.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Create Branch Section
        create_frame = ctk.CTkFrame(self, fg_color="transparent")
        create_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        create_frame.grid_columnconfigure(0, weight=1)
        
        self.new_branch_var = ctk.StringVar()
        self.new_branch_entry = ctk.CTkEntry(
            create_frame, placeholder_text="New branch name...", 
            textvariable=self.new_branch_var
        )
        self.new_branch_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.new_branch_entry.bind("<Return>", lambda e: self._create_branch())
        
        ctk.CTkButton(
            create_frame, text="Create", width=80,
            command=self._create_branch
        ).grid(row=0, column=1)
        
        # Initial load
        self.refresh_branches()

    def refresh_branches(self):
        """Reload the branch list."""
        for widget in self.branch_scroll.winfo_children():
            widget.destroy()
            
        branches = self.git_manager.get_branches()
        current_branch = self.git_manager.get_current_branch()
        
        if not branches:
            ctk.CTkLabel(
                self.branch_scroll, text="No branches found or not a git repo.", 
                text_color="gray"
            ).pack(pady=20)
            return
            
        for branch in branches:
            row = ctk.CTkFrame(self.branch_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            is_current = branch == current_branch
            
            # Branch name
            label_kwargs = {
                "text": f"★ {branch}" if is_current else f"  {branch}",
                "font": ("Segoe UI", 12, "bold" if is_current else "normal"),
                "anchor": "w"
            }
            if is_current:
                label_kwargs["text_color"] = "#00CC44"
            name_label = ctk.CTkLabel(row, **label_kwargs)
            name_label.pack(side="left", fill="x", expand=True, padx=5)
            
            # Action buttons
            if not is_current:
                # Checkout
                ctk.CTkButton(
                    row, text="Checkout", width=60, height=24,
                    command=lambda b=branch: self._checkout(b)
                ).pack(side="right", padx=2)
                
                # Merge
                ctk.CTkButton(
                    row, text="Merge", width=60, height=24,
                    fg_color="#D97706", hover_color="#B45309",
                    command=lambda b=branch: self._merge(b)
                ).pack(side="right", padx=2)
                
                # Delete
                ctk.CTkButton(
                    row, text="🗑", width=30, height=24,
                    fg_color="#DC2626", hover_color="#991B1B",
                    command=lambda b=branch: self._delete(b)
                ).pack(side="right", padx=2)

    def _create_branch(self):
        name = self.new_branch_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Branch name cannot be empty.", parent=self)
            return
            
        if self.git_manager.create_branch(name):
            self.new_branch_var.set("")
            self.refresh_branches()
            # Optionally checkout the new branch immediately
            self._checkout(name)
        else:
            messagebox.showerror("Error", f"Failed to create branch '{name}'.", parent=self)

    def _checkout(self, branch_name):
        if self.git_manager.checkout_branch(branch_name):
            self.refresh_branches()
            if self.on_branch_changed:
                self.on_branch_changed()
        else:
            messagebox.showerror("Error", f"Failed to checkout '{branch_name}'. Ensure you have no uncommitted changes.", parent=self)

    def _merge(self, branch_name):
        if messagebox.askyesno("Confirm Merge", f"Merge '{branch_name}' into current branch?", parent=self):
            success, msg = self.git_manager.merge_branch(branch_name)
            if success:
                messagebox.showinfo("Merge", "Merge completed successfully.", parent=self)
            else:
                messagebox.showerror("Merge Conflict/Error", msg, parent=self)
                self.destroy() # Close dialog to let user resolve conflicts
                
            if self.on_branch_changed:
                 self.on_branch_changed()

    def _delete(self, branch_name):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{branch_name}'?", parent=self):
            if self.git_manager.delete_branch(branch_name):
                self.refresh_branches()
            else:
                # Ask if they want to force delete
                if messagebox.askyesno("Delete Failed", f"Branch '{branch_name}' is not fully merged. Force delete?", parent=self):
                    if self.git_manager.delete_branch(branch_name, force=True):
                        self.refresh_branches()
                    else:
                        messagebox.showerror("Error", f"Failed to force delete branch '{branch_name}'.", parent=self)
