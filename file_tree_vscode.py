"""VS Code style file explorer."""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os
from typing import Optional


class VSCodeFileTree(ctk.CTkFrame):
    def __init__(self, master, app=None):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        self.app = app
        
        # Header
        header = ctk.CTkFrame(self, height=35, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header, text="EXPLORER", 
            font=("Segoe UI", 11, "bold"),
            text_color=("#383838", "#CCCCCC")
        )
        title.pack(side="left", padx=10, pady=8)
        
        # Buttons
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=5)
        
        for icon in ["⋯"]:
            ctk.CTkButton(
                btn_frame, text=icon, width=25, height=25,
                fg_color="transparent", hover_color=("#D0D0D0", "#3E3E3E"),
                font=("Segoe UI", 14), corner_radius=3
            ).pack(side="left", padx=2)
        
        # Project name
        self.project_frame = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self.project_frame.pack(fill="x", padx=5, pady=5)
        self.project_frame.pack_propagate(False)
        
        self.project_btn = ctk.CTkButton(
            self.project_frame, text="", anchor="w",
            fg_color="transparent", hover_color=("#E0E0E0", "#2A2D2E"),
            font=("Segoe UI", 11), corner_radius=0, height=30,
            text_color=("#333333", "#CCCCCC"),
            command=self.toggle_project
        )
        self.project_btn.pack(fill="x")
        
        # Tree container
        tree_container = ctk.CTkFrame(self, fg_color="transparent")
        tree_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(tree_container)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview with VS Code style
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.update_tree_theme()
        
        self.tree = ttk.Treeview(
            tree_container,
            style="VSCode.Treeview",
            show="tree",
            selectmode="browse",
            yscrollcommand=scrollbar.set
        )
        self.tree.pack(fill="both", expand=True, side="left")
        scrollbar.configure(command=self.tree.yview)
        
        # Icons mapping
        self.icons = {
            "folder": "📁",
            "folder_open": "📂",
            "file": "📄",
            ".py": "🐍",
            ".js": "📜",
            ".html": "🌐",
            ".css": "🎨",
            ".json": "📋",
            ".md": "📝",
            ".txt": "📄",
            ".sh": "⚙️",
            ".yml": "⚙️",
            ".yaml": "⚙️"
        }
        
        self.expanded = True
        self.current_path = None
        
        # Bindings
        self.tree.bind("<<TreeviewOpen>>", self.on_open)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self.on_click)
        
        # Load default path
        try:
            default_path = os.getcwd()
            self.load_directory(default_path)
        except (OSError, PermissionError):
            pass
    
    def update_tree_theme(self) -> None:
        """Update tree colors based on theme."""
        mode = ctk.get_appearance_mode()
        
        if mode == "Light":
            self.style.configure(
                "VSCode.Treeview",
                background="#FFFFFF",
                foreground="#333333",
                fieldbackground="#FFFFFF",
                borderwidth=0,
                font=("Segoe UI", 10),
                rowheight=22
            )
            self.style.configure(
                "VSCode.Treeview.Heading",
                background="#F3F3F3",
                foreground="#333333",
                borderwidth=0
            )
            self.style.map(
                "VSCode.Treeview",
                background=[("selected", "#CCE8FF")],
                foreground=[("selected", "#000000")]
            )
        else:
            self.style.configure(
                "VSCode.Treeview",
                background="#252526",
                foreground="#CCCCCC",
                fieldbackground="#252526",
                borderwidth=0,
                font=("Segoe UI", 10),
                rowheight=22
            )
            self.style.configure(
                "VSCode.Treeview.Heading",
                background="#2D2D2D",
                foreground="#CCCCCC",
                borderwidth=0
            )
            self.style.map(
                "VSCode.Treeview",
                background=[("selected", "#094771")],
                foreground=[("selected", "#FFFFFF")]
            )
    
    def toggle_project(self) -> None:
        """Toggle project tree visibility."""
        if self.expanded:
            for item in self.tree.get_children():
                self.tree.item(item, open=False)
            self.project_btn.configure(text=f"▶ {os.path.basename(self.current_path)}")
            self.expanded = False
        else:
            for item in self.tree.get_children():
                self.tree.item(item, open=True)
            self.project_btn.configure(text=f"▼ {os.path.basename(self.current_path)}")
            self.expanded = True
    
    def load_directory(self, path: str) -> None:
        """Load directory into tree."""
        if not os.path.isdir(path):
            return
        
        self.current_path = path
        self.tree.delete(*self.tree.get_children())
        
        project_name = os.path.basename(path) or path
        self.project_btn.configure(text=f"▼ {project_name}")
        
        self._populate_tree("", path)
    
    def _populate_tree(self, parent: str, path: str) -> None:
        """Populate tree with files and folders."""
        try:
            items = sorted(os.listdir(path))
            
            # Separate folders and files
            folders = [i for i in items if os.path.isdir(os.path.join(path, i)) and not i.startswith(".")]
            files = [i for i in items if os.path.isfile(os.path.join(path, i)) and not i.startswith(".")]
            
            # Add folders first
            for item in folders:
                item_path = os.path.join(path, item)
                icon = self.icons["folder"]
                node = self.tree.insert(
                    parent, "end",
                    text=f"  {icon} {item}",
                    values=[item_path, "folder"],
                    open=False
                )
                # Add dummy child for lazy loading
                self.tree.insert(node, "end", text="")
            
            # Add files
            for item in files:
                item_path = os.path.join(path, item)
                ext = os.path.splitext(item)[1]
                icon = self.icons.get(ext, self.icons["file"])
                self.tree.insert(
                    parent, "end",
                    text=f"  {icon} {item}",
                    values=[item_path, "file"]
                )
        except (PermissionError, OSError):
            pass
    
    def on_open(self, event: tk.Event) -> None:
        """Handle folder expansion."""
        try:
            item = self.tree.focus()
            values = self.tree.item(item, "values")
            
            if not values or values[1] != "folder":
                return
            
            path = values[0]
            
            # Check if already loaded
            children = self.tree.get_children(item)
            if len(children) == 1 and not self.tree.item(children[0], "text"):
                # Remove dummy and load real content
                self.tree.delete(children[0])
                self._populate_tree(item, path)
                
                # Update icon
                text = self.tree.item(item, "text")
                new_text = text.replace(self.icons["folder"], self.icons["folder_open"])
                self.tree.item(item, text=new_text)
        except (tk.TclError, IndexError, KeyError):
            pass
    
    def on_click(self, event: tk.Event) -> None:
        """Handle folder collapse."""
        try:
            item = self.tree.identify("item", event.x, event.y)
            if item:
                values = self.tree.item(item, "values")
                if values and values[1] == "folder":
                    if self.tree.item(item, "open"):
                        # Update icon to closed
                        text = self.tree.item(item, "text")
                        new_text = text.replace(self.icons["folder_open"], self.icons["folder"])
                        self.tree.item(item, text=new_text)
        except (tk.TclError, IndexError, KeyError):
            pass
    
    def on_double_click(self, event: tk.Event) -> None:
        """Handle file double-click."""
        try:
            print("[DEBUG] Double-click detected")
            item = self.tree.focus()
            print(f"[DEBUG] Item: {item}")
            values = self.tree.item(item, "values")
            print(f"[DEBUG] Values: {values}")
            
            if not values:
                print("[DEBUG] No values found")
                return
            
            path = values[0]
            file_type = values[1]
            print(f"[DEBUG] Path: {path}, Type: {file_type}")
            
            if file_type == "file" and os.path.isfile(path):
                print(f"[DEBUG] Opening file: {path}")
                print(f"[DEBUG] App exists: {self.app is not None}")
                print(f"[DEBUG] Has open_file: {hasattr(self.app, 'open_file') if self.app else False}")
                if self.app and hasattr(self.app, "open_file"):
                    print(f"[DEBUG] Calling app.open_file({path})")
                    self.app.open_file(path)
                    print("[DEBUG] File opened successfully")
                else:
                    print("[DEBUG] ERROR: App or open_file not available")
            else:
                print(f"[DEBUG] Not a file or doesn't exist")
        except (tk.TclError, IndexError, AttributeError, OSError) as e:
            print(f"[DEBUG] ERROR in on_double_click: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh(self) -> None:
        """Refresh current directory."""
        if self.current_path:
            self.load_directory(self.current_path)


# Sections at bottom
class VSCodeSections(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        
        sections = [
            ("▶ OUTLINE", None),
            ("▶ TIMELINE", None)
        ]
        
        for text, cmd in sections:
            btn = ctk.CTkButton(
                self, text=text, anchor="w",
                fg_color="transparent", hover_color=("#E0E0E0", "#2A2D2E"),
                font=("Segoe UI", 10), corner_radius=0, height=30,
                text_color=("#333333", "#CCCCCC"),
                command=cmd
            )
            btn.pack(fill="x", padx=10, pady=2)
