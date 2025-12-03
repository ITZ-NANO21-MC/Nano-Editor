"""Project-wide search functionality."""
import customtkinter
import tkinter
import os
from pathlib import Path
import threading


class ProjectSearchWindow(customtkinter.CTkToplevel):
    """Window for searching text across project files."""
    
    def __init__(self, master, workspace_path, open_file_callback):
        super().__init__(master)
        self.workspace_path = Path(workspace_path)
        self.open_file_callback = open_file_callback
        self.search_thread = None
        
        self.title("Search in Project")
        self.geometry("700x500")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Search input
        search_frame = customtkinter.CTkFrame(self)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = customtkinter.CTkEntry(
            search_frame,
            placeholder_text="Search text..."
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_entry.bind("<Return>", lambda e: self.start_search())
        
        self.search_btn = customtkinter.CTkButton(
            search_frame, text="Search", width=80,
            command=self.start_search
        )
        self.search_btn.grid(row=0, column=1)
        
        # Options
        options_frame = customtkinter.CTkFrame(search_frame)
        options_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        self.case_sensitive = customtkinter.CTkCheckBox(
            options_frame, text="Case sensitive"
        )
        self.case_sensitive.pack(side="left", padx=5)
        
        self.whole_word = customtkinter.CTkCheckBox(
            options_frame, text="Whole word"
        )
        self.whole_word.pack(side="left", padx=5)
        
        # Results
        results_frame = customtkinter.CTkFrame(self)
        results_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        self.results_text = customtkinter.CTkTextbox(
            results_frame, font=("monospace", 11)
        )
        self.results_text.grid(row=0, column=0, sticky="nsew")
        self.results_text.bind("<Double-Button-1>", self.on_result_click)
        
        # Status
        self.status_label = customtkinter.CTkLabel(
            self, text="Enter search term and press Search"
        )
        self.status_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))
    
    def start_search(self):
        """Start search in background thread."""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        self.search_btn.configure(state="disabled", text="Searching...")
        self.results_text.delete("1.0", "end")
        self.status_label.configure(text="Searching...")
        
        def search_thread():
            results = self.search_in_files(query)
            self.after(0, lambda: self.display_results(results, query))
        
        self.search_thread = threading.Thread(target=search_thread, daemon=True)
        self.search_thread.start()
    
    def search_in_files(self, query):
        """Search for query in all project files."""
        results = []
        case_sensitive = self.case_sensitive.get()
        whole_word = self.whole_word.get()
        
        search_query = query if case_sensitive else query.lower()
        
        # File extensions to search
        extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', 
                     '.rb', '.php', '.html', '.css', '.txt', '.md', '.json', '.xml'}
        
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', 'venv', 'env'}]
                
                for file in files:
                    if Path(file).suffix in extensions:
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                for line_num, line in enumerate(f, 1):
                                    search_line = line if case_sensitive else line.lower()
                                    
                                    if whole_word:
                                        import re
                                        pattern = r'\b' + re.escape(search_query) + r'\b'
                                        if re.search(pattern, search_line):
                                            results.append((file_path, line_num, line.rstrip()))
                                    else:
                                        if search_query in search_line:
                                            results.append((file_path, line_num, line.rstrip()))
                        except Exception:
                            continue
        except Exception:
            pass
        
        return results
    
    def display_results(self, results, query):
        """Display search results."""
        self.search_btn.configure(state="normal", text="Search")
        
        if not results:
            self.results_text.insert("1.0", f"No results found for '{query}'")
            self.status_label.configure(text="No results found")
            return
        
        self.status_label.configure(text=f"Found {len(results)} results")
        
        for file_path, line_num, line in results:
            rel_path = file_path.relative_to(self.workspace_path)
            self.results_text.insert("end", f"{rel_path}:{line_num}\n", "file")
            self.results_text.insert("end", f"  {line}\n\n")
        
        # Configure tag for clickable file paths
        self.results_text.tag_config("file", foreground="#4A9EFF", underline=True)
    
    def on_result_click(self, event):
        """Handle click on search result."""
        try:
            index = self.results_text.index(f"@{event.x},{event.y}")
            line_start = self.results_text.index(f"{index} linestart")
            line_end = self.results_text.index(f"{index} lineend")
            line_text = self.results_text.get(line_start, line_end)
            
            if ":" in line_text and not line_text.startswith(" "):
                parts = line_text.split(":")
                if len(parts) >= 2:
                    file_path = self.workspace_path / parts[0]
                    line_num = int(parts[1])
                    
                    if file_path.exists():
                        self.open_file_callback(str(file_path), line_num)
                        self.destroy()
        except Exception:
            pass
