import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from core.git.git_manager import GitManager
from ui.diff_viewer import DiffViewer
from ui.branch_dialog import BranchDialog
from ui.conflict_resolver import ConflictResolver
from logger import logger

class GitPanel(ctk.CTkFrame):
    """Source control panel with Git integration."""
    def __init__(self, master, app):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        self.app = app
        
        # Determine starting repo path (can be updated later if needed)
        repo_path = os.getcwd()
        if hasattr(app, 'file_tree') and app.file_tree and app.file_tree.current_path:
             repo_path = app.file_tree.current_path
             
        self.git_manager = GitManager(repo_path)
        
        # Header
        header = ctk.CTkFrame(self, height=35, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="SOURCE CONTROL",
            font=("Segoe UI", 11, "bold"),
            text_color=("#383838", "#CCCCCC")
        ).pack(side="left", padx=10, pady=8)

        self.branch_label = ctk.CTkLabel(
            header, text="",
            font=("Segoe UI", 10),
            text_color=("#007ACC", "#3B8ED0"),
            cursor="hand2"
        )
        self.branch_label.pack(side="right", padx=10, pady=8)
        self.branch_label.bind("<Button-1>", lambda e: self.show_branch_manager())

        
        # Top action buttons
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            actions_frame, text="↻ Refresh", width=60, height=24,
            command=self.refresh_status, font=("Segoe UI", 10)
        ).pack(side="left")
        
        # Commit Message
        msg_frame = ctk.CTkFrame(self, fg_color="transparent")
        msg_frame.pack(fill="x", padx=10, pady=5)
        
        self.commit_msg_var = ctk.StringVar()
        self.msg_entry = ctk.CTkEntry(
            msg_frame, placeholder_text="Message (Ctrl+Enter to commit)",
            textvariable=self.commit_msg_var, height=28, font=("Segoe UI", 11)
        )
        self.msg_entry.pack(fill="x", pady=(0, 5))
        self.msg_entry.bind("<Control-Return>", lambda e: self.commit_changes())
        
        ctk.CTkButton(
            msg_frame, text="Commit", height=28,
            command=self.commit_changes, font=("Segoe UI", 11)
        ).pack(fill="x")
        
        # Divider
        ctk.CTkFrame(self, height=1, fg_color=("#D0D0D0", "#3E3E42")).pack(fill="x", pady=5)
        
        # Changes Section Header
        ctk.CTkLabel(
            self, text="CHANGES", font=("Segoe UI", 10, "bold"),
            text_color=("#666666", "#999999")
        ).pack(anchor="w", padx=10)
        
        # Changes List (Scrollable)
        self.changes_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.changes_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Store checkboxes to track selected items if needed later
        # For simplicity, 'add_all' and 'commit' will be used to commit everything modified.
        self.change_items = []
        
        # Initial load
        self.refresh_status()

    def update_repo_path(self, path: str):
        """Update the git manager repository path."""
        self.git_manager.repo_path = path
        self.refresh_status()

    def refresh_status(self):
        """Fetch git status and update the UI."""
        # Clear existing items
        if not hasattr(self, 'changes_scroll'):
            return
            
        for widget in self.changes_scroll.winfo_children():
            widget.destroy()

            
        self.change_items.clear()
        
        # Check if it's a valid repo
        if not self.git_manager.is_git_repo():
            self.branch_label.configure(text="")
            self.repo_warning = ctk.CTkLabel(
                self.changes_scroll, text="Not a git repository.", 
                text_color="#FF5555", font=("Segoe UI", 11)
            )
            self.repo_warning.pack(pady=20)
            return

        # Update branch label
        branch = self.git_manager.get_current_branch()
        self.branch_label.configure(text=f"⎇ {branch}" if branch else "")
            
        # Get status
        status_list = self.git_manager.get_status()
        
        if not status_list:
            ctk.CTkLabel(
                self.changes_scroll, text="No changes.", 
                text_color=("#666666", "#999999"), font=("Segoe UI", 11)
            ).pack(pady=20)
            return
            
        # Render items
        for item in status_list:
            row = ctk.CTkFrame(self.changes_scroll, fg_color="transparent", height=24)
            row.pack(fill="x", pady=1)
            
            is_conflict = "U" in item['status']
            
            # Status badge (M, A, UU, etc)
            if is_conflict:
                status_color = "#FF5555" # Red for conflict
                status_text = "C" # C for Conflict
            else:
                status_color = "#FFCC00" if "M" in item['status'] else ("#00CC44" if "A" in item['status'] else "#999999")
                status_text = item['status'].strip().ljust(2)
                
            badge = ctk.CTkLabel(
                row, text=status_text, 
                width=20, font=("monospace", 10, "bold"), text_color=status_color
            )
            badge.pack(side="left", padx=5)
            
            # File name
            filename = item['file'].split('/')[-1]
            label_kwargs = {
                "text": filename,
                "font": ("Segoe UI", 11, "bold" if is_conflict else "normal"),
                "anchor": "w"
            }
            if is_conflict:
                label_kwargs["text_color"] = "#FF5555"
            label = ctk.CTkLabel(row, **label_kwargs)
            label.pack(side="left", fill="x", expand=True)
            self._add_tooltip(label, item['file'])
            
            # Bind click to show diff or resolver
            if is_conflict:
                label.bind("<Button-1>", lambda e, f=item['file']: self.show_conflict_resolver(f))
            else:
                label.bind("<Button-1>", lambda e, f=item['file']: self.show_diff(f))

            
            # Plus button to add just this file (optional future enhancement)
            add_btn = ctk.CTkButton(
                row, text="+", width=20, height=20, font=("Segoe UI", 12),
                fg_color="transparent", hover_color=("#D0D0D0", "#404040"),
                command=lambda f=item['file']: self._add_single_file(f)
            )
            add_btn.pack(side="right", padx=2)

    def _add_single_file(self, filepath: str):
        if self.git_manager.add_file(filepath):
            if hasattr(self.app, 'feedback'):
                self.app.feedback.show_success(f"Added {filepath}")
            self.refresh_status()

    def commit_changes(self):
        """Add all files and commit."""
        msg = self.commit_msg_var.get().strip()
        if not msg:
            messagebox.showwarning("Commit", "Please enter a commit message.")
            return
            
        if not self.git_manager.is_git_repo():
            messagebox.showerror("Error", "Not a git repository.")
            return
            
        # Add all first
        if not self.git_manager.add_all():
             messagebox.showerror("Error", "Failed to stage files.")
             return
             
        # Commit
        if self.git_manager.commit(msg):
            self.commit_msg_var.set("")
            if hasattr(self.app, 'feedback'):
                self.app.feedback.show_success("Changes committed successfully")
            self.refresh_status()
        else:
            messagebox.showerror("Error", "Failed to commit. Ensure you have changes and git is configured.")

    def show_diff(self, filepath: str):
        """Open the DiffViewer for a file."""
        # Try unstaged diff first, then staged
        diff = self.git_manager.get_diff(filepath)
        if not diff:
            diff = self.git_manager.get_staged_diff(filepath)
            
        viewer = DiffViewer(self.app, filepath, diff)
        # Delay grab_set until the window is fully rendered
        viewer.after(50, lambda: viewer.grab_set() if viewer.winfo_exists() else None)

    def show_branch_manager(self):
        """Open the BranchManager dialog."""
        if not self.git_manager.is_git_repo():
            messagebox.showinfo("Git", "Not a git repository.")
            return
            
        dialog = BranchDialog(self.winfo_toplevel(), self.git_manager, on_branch_changed=self.refresh_status)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

    def show_conflict_resolver(self, filepath: str):
        """Open the ConflictResolver dialog for a file."""
        resolver = ConflictResolver(self.winfo_toplevel(), self.app, filepath, self.git_manager)
        resolver.transient(self.winfo_toplevel())
        
        # We don't grab_set on resolver, it's basically a window.
        # It'll destroy itself when done.
        
        # When resolver closes, refresh git panel
        resolver.bind("<Destroy>", lambda e: self.after(100, self.refresh_status), add="+")


    def _add_tooltip(self, widget, text):
        def enter(event):
            widget.configure(text_color=("#007ACC", "#3B8ED0"))
        def leave(event):
            widget.configure(text_color=("#333333", "#CCCCCC"))
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
