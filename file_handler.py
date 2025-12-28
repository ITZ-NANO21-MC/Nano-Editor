"""File operations handler for NanoEditor."""
import os
import shlex
import tkinter as tk
from tkinter import filedialog, messagebox

class FileHandler:
    """Mixin or helper for File operations in the main App."""
    
    def open_file(self, file_path=None) -> None:
        if not file_path:
            file_path = filedialog.askopenfilename()
        
        if file_path and os.path.exists(file_path):
            try:
                # Check if it's already open
                for i, tab in enumerate(self.tab_manager.tabs):
                    if tab.file_path == file_path:
                         self.tab_manager.switch_tab(i)
                         return

                with open(file_path, "r") as f:
                    content = f.read()
                
                tab_index = self.tab_manager.new_tab(file_path)
                tab = self.tab_manager.tabs[tab_index]
                tab.content = content
                self.tab_manager.switch_tab(tab_index)
                
                self.current_file = file_path
                self.status_bar.set_file_path(file_path)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self) -> None:
        tab = self.tab_manager.get_current_tab()
        if not tab: return
        
        if tab.file_path:
            try:
                content = self.tab_manager.text_area.get("1.0", tk.END + "-1c")
                with open(tab.file_path, "w") as f:
                    f.write(content)
                tab.content = content # Keep in sync
                self.feedback.show_success(f"Saved {os.path.basename(tab.file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self) -> None:
        tab = self.tab_manager.get_current_tab()
        if not tab: return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".py")
        if file_path:
            try:
                content = self.tab_manager.text_area.get("1.0", tk.END + "-1c")
                with open(file_path, "w") as f:
                    f.write(content)
                tab.file_path = file_path
                tab.content = content # Keep in sync
                self.tab_manager.update_tab_title()
                self.feedback.show_success(f"Saved as {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def open_file_at_line(self, file_path, line_num=1) -> None:
        """Opens a file and scrolls to a specific line."""
        self.open_file(file_path)
        # Give some time for the tab to switch and text to load
        self.after(100, lambda: self._goto_line(line_num))

    def _goto_line(self, line_num) -> None:
        if hasattr(self, 'tab_manager'):
            self.tab_manager.text_area.see(f"{line_num}.0")
            self.tab_manager.text_area.mark_set("insert", f"{line_num}.0")
            self.tab_manager.text_area.tag_add("highlight_line", f"{line_num}.0", f"{line_num}.end")
            self.after(2000, lambda: self.tab_manager.text_area.tag_remove("highlight_line", "1.0", "end"))

    def run_current_file(self) -> None:
        tab = self.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            messagebox.showwarning("Run", "Please save the file first")
            return
            
        file_path = tab.file_path
        ext = os.path.splitext(file_path)[1].lower()
        
        command = ""
        if ext == ".py":
            command = f"python3 {shlex.quote(file_path)}"
        elif ext == ".js":
            command = f"node {shlex.quote(file_path)}"
        elif ext in [".sh", ".bash"]:
            command = f"bash {shlex.quote(file_path)}"
        
        if command:
            if hasattr(self, 'terminal_panel'):
                self.terminal_panel.run_command(command)
                if not self.terminal_panel.winfo_viewable():
                    self.toggle_terminal()
        else:
            messagebox.showinfo("Run", f"No run command configured for {ext} files")
