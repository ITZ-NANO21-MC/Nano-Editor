"""VS Code style file explorer."""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os
import subprocess
import ast
import re
from typing import Optional
from event_bus import event_bus, Events
from tkfontawesome import icon_to_image


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
        
        # Icon cache
        self.tree_icons = {}
        self._create_tree_icons()
        
        # Buttons
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=5)
        
        # Tree container
        tree_container = ctk.CTkFrame(self, fg_color="transparent")
        tree_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(tree_container)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview style
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
        
        self.expanded = True
        self.current_path = None
        
        # Project Button
        self.project_btn = ctk.CTkButton(
            self, text="", anchor="w",
            fg_color="transparent", hover=False,
            font=("Segoe UI", 11, "bold"),
            command=self.toggle_project,
            height=25,
            corner_radius=0
        )
        self.project_btn.pack(fill="x", before=tree_container)
        
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

    def _create_tree_icons(self):
        """Creates PhotoImages for the treeview."""
        mode = ctk.get_appearance_mode()
        folder_color = "#D4A017" # Golden for folders
        file_color = "#333333" if mode == "Light" else "#CCCCCC"
        python_color = "#3776AB"
        js_color = "#F7DF1E"
        
        self.tree_icons = {
            "folder": icon_to_image("folder", fill=folder_color, scale_to_width=16),
            "folder_open": icon_to_image("folder-open", fill=folder_color, scale_to_width=16),
            "file": icon_to_image("file", fill=file_color, scale_to_width=16),
            ".py": icon_to_image("python", fill=python_color, scale_to_width=16),
            ".js": icon_to_image("js", fill=js_color, scale_to_width=16),
            ".html": icon_to_image("html5", fill="#E34F26", scale_to_width=16),
            ".css": icon_to_image("css3-alt", fill="#1572B6", scale_to_width=16),
        }

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
                node = self.tree.insert(
                    parent, "end",
                    text=f" {item}",
                    image=self.tree_icons["folder"],
                    values=[item_path, "folder"],
                    open=False
                )
                # Add dummy child for lazy loading
                self.tree.insert(node, "end", text="")
            
            # Add files
            for item in files:
                item_path = os.path.join(path, item)
                ext = os.path.splitext(item)[1].lower()
                icon = self.tree_icons.get(ext, self.tree_icons["file"])
                self.tree.insert(
                    parent, "end",
                    text=f" {item}",
                    image=icon,
                    values=[item_path, "file"]
                )
        except (PermissionError, OSError):
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
                self.tree.item(item, image=self.tree_icons["folder_open"])
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
                        self.tree.item(item, image=self.tree_icons["folder"])
        except (tk.TclError, IndexError, KeyError):
            pass
    
    def on_double_click(self, event: tk.Event) -> None:
        """Handle file double-click."""
        try:
            item = self.tree.focus()
            values = self.tree.item(item, "values")
            
            if not values:
                return
            
            path = values[0]
            file_type = values[1]
            
            if file_type == "file" and os.path.isfile(path):
                # Request file open via EventBus
                event_bus.emit(Events.FILE_OPEN_REQUEST, path)
        except (tk.TclError, IndexError, AttributeError, OSError) as e:
            from logger import logger
            logger.error(f"Error in on_double_click: {e}")
    
    def refresh(self) -> None:
        """Refresh current directory."""
        if self.current_path:
            self.load_directory(self.current_path)


# Sections at bottom
class VSCodeSections(ctk.CTkFrame):
    """Bottom sections for Explorer (Outline, Timeline)."""
    def __init__(self, master, app):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        self.app = app
        
        # Icon cache for symbols
        self.symbol_icons = {}
        self._create_symbol_icons()
        
        # Outline Section
        self.outline_btn = ctk.CTkButton(
            self, text="▼ OUTLINE", anchor="w",
            fg_color="transparent", hover_color=("#E0E0E0", "#2A2D2E"),
            font=("Segoe UI", 10, "bold"), corner_radius=0, height=25,
            text_color=("#333333", "#CCCCCC"),
            command=self.toggle_outline
        )
        self.outline_btn.pack(fill="x", padx=0, pady=0)
        
        self.outline_container = ctk.CTkFrame(self, fg_color="transparent")
        self.outline_container.pack(fill="both", expand=True)
        
        self.outline_tree = ttk.Treeview(
            self.outline_container,
            show="tree",
            selectmode="browse",
            style="VSCode.Treeview"
        )
        self.outline_tree.pack(fill="both", expand=True, padx=5, pady=2)
        
        # Timeline Section
        self.timeline_btn = ctk.CTkButton(
            self, text="▼ TIMELINE", anchor="w",
            fg_color="transparent", hover_color=("#E0E0E0", "#2A2D2E"),
            font=("Segoe UI", 10, "bold"), corner_radius=0, height=25,
            text_color=("#333333", "#CCCCCC"),
            command=self.toggle_timeline
        )
        self.timeline_btn.pack(fill="x", padx=0, pady=0)
        
        self.timeline_container = ctk.CTkFrame(self, fg_color="transparent")
        self.timeline_container.pack(fill="both", expand=True)
        
        self.timeline_list = tk.Listbox(
            self.timeline_container,
            bg=("#FFFFFF" if ctk.get_appearance_mode() == "Light" else "#252526"),
            fg=("#333333" if ctk.get_appearance_mode() == "Light" else "#CCCCCC"),
            font=("Segoe UI", 9),
            borderwidth=0,
            highlightthickness=0,
            selectbackground=("#CCE8FF" if ctk.get_appearance_mode() == "Light" else "#094771"),
            selectforeground=("#000000" if ctk.get_appearance_mode() == "Light" else "#FFFFFF")
        )
        self.timeline_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.outline_expanded = True
        self.timeline_expanded = True
        
        # Bindings
        self.outline_tree.bind("<Double-1>", self.on_outline_click)
        
        # Subscribe to tab changes
        event_bus.subscribe(Events.TAB_CHANGED, self.on_tab_changed)

    def _create_symbol_icons(self):
        """Creates PhotoImages for code symbols."""
        mode = ctk.get_appearance_mode()
        color = "#333333" if mode == "Light" else "#CCCCCC"
        
        self.symbol_icons = {
            "class": icon_to_image("cube", fill="#B180D7", scale_to_width=14),
            "function": icon_to_image("terminal", fill="#4A9EFF", scale_to_width=14),
            "method": icon_to_image("bolt", fill="#4A9EFF", scale_to_width=14),
            "variable": icon_to_image("info-circle", fill="#4FC1FF", scale_to_width=14),
            "macro": icon_to_image("hashtag", fill="#CCCCCC", scale_to_width=14),
            "namespace": icon_to_image("archive", fill="#D4A017", scale_to_width=14)
        }
        
    def toggle_outline(self):
        """Toggle outline section visibility."""
        if self.outline_expanded:
            self.outline_btn.configure(text="▶ OUTLINE")
            self.outline_container.pack_forget()
        else:
            self.outline_btn.configure(text="▼ OUTLINE")
            self.outline_container.pack(fill="both", expand=True)
        self.outline_expanded = not self.outline_expanded

    def toggle_timeline(self):
        """Toggle timeline section visibility."""
        if self.timeline_expanded:
            self.timeline_btn.configure(text="▶ TIMELINE")
            self.timeline_container.pack_forget()
        else:
            self.timeline_btn.configure(text="▼ TIMELINE")
            self.timeline_container.pack(fill="both", expand=True)
        self.timeline_expanded = not self.timeline_expanded

    def on_tab_changed(self, tab):
        """Handle tab change by updating both Outline and Timeline."""
        self.update_outline(tab)
        self.update_timeline(tab)

    def update_outline(self, tab):
        """
        Analiza el contenido del archivo según su extensión para generar el esquema.
        Soporta Python (AST), JavaScript, HTML y CSS (Regex).
        """
        self.outline_tree.delete(*self.outline_tree.get_children())
        
        if not tab or not tab.file_path:
            return

        content = self.app.tab_manager.text_area.get("1.0", "end-1c")
        ext = os.path.splitext(tab.file_path)[1].lower()
        
        if ext == ".py":
            self._parse_python(content)
        elif ext in [".js", ".ts"]:
            self._parse_javascript(content)
        elif ext in [".html", ".htm"]:
            self._parse_html(content)
        elif ext == ".css":
            self._parse_css(content)
        elif ext in [".c", ".cpp", ".cc", ".h", ".hpp"]:
            self._parse_cpp(content)

    def _parse_python(self, content):
        """Usa AST para un análisis preciso de Python."""
        try:
            tree = ast.parse(content)
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    class_id = self.outline_tree.insert(
                        "", "end", text=f" {node.name}", 
                        image=self.symbol_icons["class"],
                        values=[node.lineno], open=True
                    )
                    for subnode in node.body:
                        if isinstance(subnode, ast.FunctionDef):
                            self.outline_tree.insert(
                                class_id, "end", text=f" {subnode.name}", 
                                image=self.symbol_icons["method"],
                                values=[subnode.lineno]
                            )
                elif isinstance(node, ast.FunctionDef):
                    self.outline_tree.insert(
                        "", "end", text=f" {node.name}", 
                        image=self.symbol_icons["function"],
                        values=[node.lineno]
                    )
        except SyntaxError: pass

    def _parse_javascript(self, content):
        """Usa Regex para encontrar clases y funciones en JS."""
        patterns = [
            (r'class\s+([a-zA-Z0-9_$]+)', self.symbol_icons["class"]),
            (r'function\s+([a-zA-Z0-9_$]+)', self.symbol_icons["function"]),
            (r'(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*\(.*?\)\s*=>', self.symbol_icons["method"])
        ]
        self._apply_regex_outline(content, patterns)

    def _parse_html(self, content):
        """Usa Regex para encontrar IDs y etiquetas importantes en HTML."""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Elementos con ID
            match_id = re.search(r'<([a-zA-Z0-9]+)\s+[^>]*id=["\']([^"\']+)["\']', line)
            if match_id:
                self.outline_tree.insert(
                    "", "end", text=f" #{match_id.group(2)}", 
                    image=self.symbol_icons["variable"], values=[i]
                )
            # Encabezados
            match_h = re.search(r'<(h[1-6])(?:\s+[^>]*)?>(.*?)</h[1-6]>', line)
            if match_h:
                self.outline_tree.insert(
                    "", "end", text=f" {match_h.group(2)[:20]}", 
                    image=self.symbol_icons["macro"], values=[i]
                )

    def _parse_css(self, content):
        """Usa Regex para encontrar selectores en CSS."""
        pattern = r'([.#a-zA-Z][^{]*)\s*\{'
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            match = re.search(pattern, line)
            if match:
                selector = match.group(1).strip()
                if selector and not selector.startswith("@"):
                    self.outline_tree.insert(
                        "", "end", text=f" {selector[:25]}", 
                        image=self.symbol_icons["variable"], values=[i]
                    )

    def _parse_cpp(self, content):
        """Usa Regex para encontrar símbolos en C/C++."""
        patterns = [
            (r'(?:class|struct)\s+([a-zA-Z0-9_$]+)\s*(?::\s*[^{]*)?\{', self.symbol_icons["class"]),
            (r'namespace\s+([a-zA-Z0-9_$]+)\s*\{', self.symbol_icons["namespace"]),
            (r'^\s*#\s*define\s+([a-zA-Z0-9_$]+)', self.symbol_icons["macro"]),
            (r'(?:[\w:]+\s+)+([\w:]+)\s*\([^)]*\)\s*(?:const)?\s*\{', self.symbol_icons["method"])
        ]
        self._apply_regex_outline(content, patterns)

    def _apply_regex_outline(self, content, patterns):
        """Aplica patrones regex línea por línea para generar el esquema."""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, icon_img in patterns:
                match = re.search(pattern, line)
                if match:
                    self.outline_tree.insert(
                        "", "end", text=f" {match.group(1)}", 
                        image=icon_img, values=[i]
                    )

    def on_outline_click(self, event):
        """Handles double-click on outline items to navigate to the code line."""
        item = self.outline_tree.focus()
        if item:
            values = self.outline_tree.item(item, "values")
            if values:
                line_num = int(values[0])
                self.app.open_file_at_line(self.app.tab_manager.get_current_tab().file_path, line_num)

    def update_timeline(self, tab):
        """
        Updates the timeline list with git history for the current file.
        """
        self.timeline_list.delete(0, tk.END)
        
        if not tab or not tab.file_path:
            self.timeline_list.insert(tk.END, " No file selected")
            return
            
        file_path = tab.file_path
        if not os.path.exists(file_path):
            self.timeline_list.insert(tk.END, " File not saved")
            return

        try:
            dir_path = os.path.dirname(file_path)
            # Format: hash - relative_date : subject
            log_format = "%h - %ar : %s"
            cmd = ["git", "-C", dir_path, "log", "-n", "20", f"--pretty=format:{log_format}", "--", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    self.timeline_list.insert(tk.END, f" {line}")
            else:
                self.timeline_list.insert(tk.END, " No history found")
        except Exception:
            self.timeline_list.insert(tk.END, " History unavailable")
