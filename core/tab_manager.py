"""Tab management system for multiple file editing."""
import customtkinter
import tkinter
from core.text_area import CodeEditor
from core.line_numbers import LineNumbers
from typing import Optional
from event_bus import event_bus, Events


class EditorTab:
    """Represents a single editor tab."""
    
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path
        self.content = ""
        self.modified = False
        self.cursor_position = "1.0"
        self.scroll_position = 0.0
    
    def get_title(self) -> str:
        """Get tab title."""
        if self.file_path:
            import os
            name = os.path.basename(self.file_path)
            return f"{'*' if self.modified else ''}{name}"
        return "Untitled*" if self.modified else "Untitled"


class TabManager(customtkinter.CTkFrame):
    """Manages multiple editor tabs."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.tabs = []
        self.current_tab_index = -1
        self.tab_buttons = []
        
        # Tab bar
        self.tab_bar = customtkinter.CTkFrame(self)
        self.tab_bar.pack(side="top", fill="x", padx=2, pady=2)
        
        # New tab button
        self.new_tab_btn = customtkinter.CTkButton(
            self.tab_bar, text="+", width=30,
            command=self.new_tab
        )
        self.new_tab_btn.pack(side="left", padx=2)
        
        # Editor container
        self.editor_container = customtkinter.CTkFrame(self)
        self.editor_container.pack(side="top", fill="both", expand=True)
        
        self.editor_container.grid_rowconfigure(0, weight=1)
        self.editor_container.grid_columnconfigure(0, weight=0)
        self.editor_container.grid_columnconfigure(1, weight=1)
        
        # Line numbers and text area
        self.line_numbers = LineNumbers(self.editor_container, text_widget=None)
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        
        self.text_area = CodeEditor(self.editor_container)
        self.text_area.grid(row=0, column=1, sticky="nsew")
        
        self.line_numbers.text_widget = self.text_area
        self.text_area.set_line_numbers(self.line_numbers)
        
        # Create first tab and switch to it
        first_tab = self.new_tab()
        self.switch_tab(first_tab)
    
    def new_tab(self, file_path: Optional[str] = None) -> int:
        """Create new tab."""
        tab = EditorTab(file_path)
        tab_index = len(self.tabs)
        self.tabs.append(tab)
        
        # Create tab frame
        tab_frame = customtkinter.CTkFrame(self.tab_bar, fg_color="transparent")
        tab_frame.pack(side="left", padx=2)
        
        # Store index in frame for later retrieval
        tab_frame.tab_index = tab_index
        
        # Tab button
        btn = customtkinter.CTkButton(
            tab_frame,
            text=tab.get_title(),
            width=100,
            command=lambda idx=tab_index: self.switch_tab(idx)
        )
        btn.pack(side="left")
        
        # Close button
        close_btn = customtkinter.CTkButton(
            tab_frame,
            text="×",
            width=20,
            command=lambda idx=tab_index: self.close_tab(idx),
            fg_color="transparent",
            hover_color=("gray70", "gray30")
        )
        close_btn.pack(side="left", padx=(2, 0))
        
        self.tab_buttons.append((tab_frame, btn, close_btn))
        
        # Don't auto-switch, let caller decide
        return len(self.tabs) - 1
    
    def switch_tab(self, index: int) -> None:
        """Switch to tab at index."""
        if index < 0 or index >= len(self.tabs):
            return
        
        # Save current tab state (if exists)
        if self.current_tab_index >= 0 and self.current_tab_index < len(self.tabs):
            self._save_current_tab_state()
        
        # Update current index
        self.current_tab_index = index
        
        # Load new tab
        self._load_current_tab()
        
        # Update button states
        self._update_tab_buttons()
        
        # Emit event
        event_bus.emit(Events.TAB_CHANGED, self.tabs[index])
    
    def close_tab(self, index: int) -> None:
        """Close tab at index."""
        if index < 0 or index >= len(self.tabs):
            return
        
        if len(self.tabs) <= 1:
            return  # Keep at least one tab
        
        # Save state of the tab being closed (if it's the current one)
        if index == self.current_tab_index:
            current_tab = self.tabs[index]
            current_tab.content = self.text_area.get("1.0", "end-1c")
            current_tab.cursor_position = self.text_area.index(customtkinter.INSERT)
            try:
                yview = self.text_area.yview()
                current_tab.scroll_position = float(yview[0]) if yview else 0.0
            except (tkinter.TclError, ValueError, IndexError):
                current_tab.scroll_position = 0.0
        
        # Remove the tab
        self.tabs.pop(index)
        tab_frame, btn, close_btn = self.tab_buttons.pop(index)
        tab_frame.destroy()
        
        # Adjust current_tab_index
        if index < self.current_tab_index:
            # Closed tab was before current tab
            self.current_tab_index -= 1
        elif index == self.current_tab_index:
            # Closed tab was the current tab
            if self.current_tab_index >= len(self.tabs):
                self.current_tab_index = len(self.tabs) - 1
        
        # Update tab button indices
        self._update_tab_indices()
        
        # Load current tab if there are tabs left
        if self.tabs:
            self._load_current_tab()
            self._update_tab_buttons()
    
    def get_current_tab(self) -> Optional[EditorTab]:
        """Get current tab."""
        if self.current_tab_index >= 0:
            return self.tabs[self.current_tab_index]
        return None
    
    def update_tab_title(self, index: Optional[int] = None) -> None:
        """Update tab title."""
        if index is None:
            index = self.current_tab_index
        
        if 0 <= index < len(self.tabs):
            tab = self.tabs[index]
            tab_frame, btn, close_btn = self.tab_buttons[index]
            btn.configure(text=tab.get_title())
    
    def _save_current_tab_state(self) -> None:
        """Save current tab state."""
        if self.current_tab_index < 0:
            return
        
        current_tab = self.tabs[self.current_tab_index]
        current_tab.content = self.text_area.get("1.0", "end-1c")
        current_tab.cursor_position = self.text_area.index(customtkinter.INSERT)
        try:
            yview = self.text_area.yview()
            current_tab.scroll_position = float(yview[0]) if yview else 0.0
        except (tkinter.TclError, ValueError, IndexError):
            current_tab.scroll_position = 0.0
    
    def _load_current_tab(self) -> None:
        """Load current tab content."""
        if self.current_tab_index < 0:
            return
        
        tab = self.tabs[self.current_tab_index]
        
        # Clear and load content
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", tab.content)
        
        # Restore cursor and scroll position
        try:
            self.text_area.mark_set(customtkinter.INSERT, tab.cursor_position)
        except (tkinter.TclError, ValueError):
            self.text_area.mark_set(customtkinter.INSERT, "1.0")
        
        try:
            if isinstance(tab.scroll_position, (int, float)):
                self.text_area.yview_moveto(tab.scroll_position)
        except (tkinter.TclError, ValueError):
            pass
        
        # Set file_path for syntax highlighting
        self.text_area.file_path = tab.file_path
        if tab.file_path:
            self.text_area.highlight_text()
    
    def _update_tab_indices(self) -> None:
        """Update tab indices in tab buttons."""
        for i, (tab_frame, btn, close_btn) in enumerate(self.tab_buttons):
            tab_frame.tab_index = i
            btn.configure(command=lambda idx=i: self.switch_tab(idx))
            close_btn.configure(command=lambda idx=i: self.close_tab(idx))
    
    def _update_tab_buttons(self) -> None:
        """Update tab button states."""
        for i, (tab_frame, btn, close_btn) in enumerate(self.tab_buttons):
            if i == self.current_tab_index:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color=("gray85", "gray15"))
