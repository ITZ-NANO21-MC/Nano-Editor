import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import re

class ConflictResolver(ctk.CTkToplevel):
    """A visual tool to resolve git merge conflicts."""
    def __init__(self, master, app, filepath, git_manager):
        super().__init__(master)
        
        self.app = app
        self.filepath = filepath
        self.git_manager = git_manager
        
        # We need to ensure we have a valid absolute path
        if not os.path.isabs(self.filepath):
            self.filepath = os.path.join(self.git_manager.repo_path, self.filepath)
            
        self.filename = os.path.basename(self.filepath)
        
        self.title(f"Resolve Conflicts - {self.filename}")
        self.geometry("900x700")
        self.minsize(600, 400)
        
        # State
        self.original_content = ""
        self.conflicts = [] # List of {"start": i, "mid": j, "end": k} indicating line indices
        self.current_conflict_idx = 0
        
        self._setup_ui()
        self._load_file()
        
    def _setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header toolbar
        toolbar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            toolbar, text="Loading...", font=("Segoe UI", 12, "bold")
        )
        self.status_label.pack(side="left", padx=10)
        
        # Action Buttons
        actions_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        actions_frame.pack(side="right")
        
        self.prev_btn = ctk.CTkButton(
            actions_frame, text="▲ Prev", width=60, command=self._prev_conflict, state="disabled"
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(
            actions_frame, text="▼ Next", width=60, command=self._next_conflict, state="disabled"
        )
        self.next_btn.pack(side="left", padx=5)
        
        self.resolve_btn = ctk.CTkButton(
            actions_frame, text="Mark as Resolved", fg_color="#00CC44", hover_color="#00AA33",
            command=self._mark_resolved
        )
        self.resolve_btn.pack(side="left", padx=(15, 5))
        
        # Text editor
        editor_frame = ctk.CTkFrame(self)
        editor_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)
        
        self.text_widget = tk.Text(
            editor_frame, 
            bg="#1E1E1E", fg="#D4D4D4", insertbackground="white",
            font=("Consolas", 12), undo=True, wrap="none"
        )
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scroll = tk.Scrollbar(editor_frame, orient="vertical", command=self.text_widget.yview)
        h_scroll = tk.Scrollbar(editor_frame, orient="horizontal", command=self.text_widget.xview)
        self.text_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        # Setup tags for highlighting conflicts
        self.text_widget.tag_configure("conflict_current_marker", bg="#3A3A3A", fg="#569CD6")
        self.text_widget.tag_configure("conflict_current_content", bg="#203423") # Dark green
        self.text_widget.tag_configure("conflict_separator", bg="#3A3A3A", fg="#569CD6")
        self.text_widget.tag_configure("conflict_incoming_content", bg="#2D2140") # Dark purple/blue
        self.text_widget.tag_configure("conflict_incoming_marker", bg="#3A3A3A", fg="#569CD6")
        
        # Bindings
        self.text_widget.bind("<KeyRelease>", self._on_text_modified)
        
    def _load_file(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.original_content = content
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", content)
            
            self._parse_conflicts()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}", parent=self)
            self.destroy()

    def _parse_conflicts(self):
        """Find conflict markers and highlight them."""
        # Clear existing tags
        for tag in self.text_widget.tag_names():
            if tag.startswith("conflict_"):
                 self.text_widget.tag_remove(tag, "1.0", "end")
                 
        self.conflicts = []
        
        # Patterns for Git conflict markers
        # <<<<<<< HEAD (or other name)
        # =======
        # >>>>>>> branch_name
        
        start_pattern = r"^<<<<<<<"
        mid_pattern = r"^======="
        end_pattern = r"^>>>>>>>"
        
        lines = self.text_widget.get("1.0", "end-1c").split("\n")
        
        in_conflict = False
        current_conflict = {}
        
        for i, line in enumerate(lines):
            line_idx = i + 1
            if re.match(start_pattern, line):
                in_conflict = True
                current_conflict = {"start": line_idx}
            elif in_conflict and re.match(mid_pattern, line):
                current_conflict["mid"] = line_idx
            elif in_conflict and re.match(end_pattern, line):
                current_conflict["end"] = line_idx
                self.conflicts.append(current_conflict)
                in_conflict = False
                current_conflict = {}
                
        self._highlight_conflicts()
        self._update_navigation()

    def _highlight_conflicts(self):
        for idx, conflict in enumerate(self.conflicts):
            start_line = conflict.get("start")
            mid_line = conflict.get("mid")
            end_line = conflict.get("end")
            
            if not (start_line and mid_line and end_line): continue
            
            # Highlight markers
            self.text_widget.tag_add("conflict_current_marker", f"{start_line}.0", f"{start_line}.end")
            self.text_widget.tag_add("conflict_separator", f"{mid_line}.0", f"{mid_line}.end")
            self.text_widget.tag_add("conflict_incoming_marker", f"{end_line}.0", f"{end_line}.end")
            
            # Highlight content
            # Current content (between <<<<<<< and =======)
            if mid_line > start_line + 1:
                self.text_widget.tag_add("conflict_current_content", f"{start_line+1}.0", f"{mid_line}.0")
                
            # Incoming content (between ======= and >>>>>>>)
            if end_line > mid_line + 1:
                self.text_widget.tag_add("conflict_incoming_content", f"{mid_line+1}.0", f"{end_line}.0")

    def _update_navigation(self):
        total = len(self.conflicts)
        if total == 0:
            self.status_label.configure(text="No conflicts found! Ready to resolve.", text_color="#00CC44")
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
        else:
            self.status_label.configure(text=f"Conflict {self.current_conflict_idx + 1} of {total}", text_color="#FFCC00")
            self.prev_btn.configure(state="normal" if self.current_conflict_idx > 0 else "disabled")
            self.next_btn.configure(state="normal" if self.current_conflict_idx < total - 1 else "disabled")
            
            # Jump to current conflict
            conflict = self.conflicts[self.current_conflict_idx]
            if "start" in conflict:
                self.text_widget.see(f"{conflict['start']}.0")
                
            # Add action overlay for the current conflict (Buttons above the start marker)
            self._add_action_buttons(conflict)
            
    def _add_action_buttons(self, conflict):
        # Remove any existing action buttons
        if hasattr(self, 'action_window'):
            self.text_widget.delete(self.action_window)
            
        start_line = conflict.get("start")
        if not start_line: return
        
        action_frame = tk.Frame(self.text_widget, bg="#333333")
        
        # Accept Current
        atk = tk.Button(
            action_frame, text="Accept Current", bg="#203423", fg="white", relief="flat",
            command=lambda: self._accept_change(conflict, "current")
        )
        atk.pack(side="left", padx=2, pady=2)
        
        # Accept Incoming
        atk_inc = tk.Button(
            action_frame, text="Accept Incoming", bg="#2D2140", fg="white", relief="flat",
            command=lambda: self._accept_change(conflict, "incoming")
        )
        atk_inc.pack(side="left", padx=2, pady=2)
        
        # Accept Both
        atk_both = tk.Button(
            action_frame, text="Accept Both", bg="#4A4A4A", fg="white", relief="flat",
            command=lambda: self._accept_change(conflict, "both")
        )
        atk_both.pack(side="left", padx=2, pady=2)

        # Insert frame as a window in the text widget right before the <<<<<<< marker
        self.text_widget.insert(f"{start_line}.0", "\n")
        self.action_window = self.text_widget.window_create(f"{start_line}.0", window=action_frame)
        
    def _accept_change(self, conflict, mode):
        start_line = conflict["start"]
        mid_line = conflict["mid"]
        end_line = conflict["end"]
        
        # Get content
        current_content = self.text_widget.get(f"{start_line+1}.0", f"{mid_line}.0")
        incoming_content = self.text_widget.get(f"{mid_line+1}.0", f"{end_line}.0")
        
        # The indices have shifted down by 1 because we added the action_window line
        # but the text widget handles window deletion when we delete the range
        real_start = f"{start_line-1}.0" if hasattr(self, 'action_window') else f"{start_line}.0"
        
        # Ensure we delete exactly up to the end of the end_pattern line
        real_end = f"{end_line+1}.0"
        
        # Delete entire conflict block
        self.text_widget.delete(real_start, real_end)
        
        # Insert desired resolution
        insertion_point = real_start
        if mode == "current":
            self.text_widget.insert(insertion_point, current_content)
        elif mode == "incoming":
            self.text_widget.insert(insertion_point, incoming_content)
        elif mode == "both":
            self.text_widget.insert(insertion_point, current_content + incoming_content)
            
        # Reparse
        self._parse_conflicts()

    def _prev_conflict(self):
        if self.current_conflict_idx > 0:
            self.current_conflict_idx -= 1
            self._update_navigation()

    def _next_conflict(self):
        if self.current_conflict_idx < len(self.conflicts) - 1:
            self.current_conflict_idx += 1
            self._update_navigation()

    def _on_text_modified(self, event=None):
        if self.text_widget.edit_modified():
            # Only re-parse if they haven't just used an action button (that calls it anyway)
            # Re-parsing on every keystroke might lose the current action buttons if not careful.
            # For simplicity, we just trigger a delayed re-parse
            self.text_widget.after(500, self._delayed_parse)
            self.text_widget.edit_modified(False)
            
    def _delayed_parse(self):
        # Only re-parse if there are still markers
        content = self.text_widget.get("1.0", "end-1c")
        if "<<<<<<<" in content or "=======" in content or ">>>>>>>" in content:
            self._parse_conflicts()
        else:
             self.conflicts = []
             self._update_navigation()

    def _mark_resolved(self):
        # Check if markers still exist
        content = self.text_widget.get("1.0", "end-1c")
        if "<<<<<<<" in content or "=======" in content or ">>>>>>>" in content:
            if not messagebox.askyesno("Warning", "Conflict markers still exist in the file. Are you sure you want to mark as resolved?", parent=self):
                return
                
        # Save file
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Stage file via GitManager
            if self.git_manager.add_file(self.filepath):
                messagebox.showinfo("Resolved", f"{self.filename} has been marked as resolved and staged for commit.", parent=self)
                # If the app has an open editor for this file, we should instruct it to reload
                # But typically the file tree sends reload events.
                self.destroy()
            else:
                 messagebox.showerror("Error", "Failed to stage the resolved file.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save resolved file: {e}", parent=self)
