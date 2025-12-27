"""Popup window for AI completion suggestions."""
import customtkinter as ctk
import tkinter as tk
from typing import List, Callable
from ai_completion import CompletionSuggestion


class AICompletionPopup:
    """Popup window showing AI code completion suggestions."""
    
    def __init__(self, 
                 master: ctk.CTk, 
                 text_widget: ctk.CTkTextbox,
                 on_select: Callable[[str], None]):
        
        self.master = master
        self.text_widget = text_widget
        self.on_select = on_select
        
        # Create popup window
        self.popup = tk.Toplevel(master)
        self.popup.wm_overrideredirect(True)
        self.popup.configure(
            bg="#2B2B2B",
            relief="solid",
            borderwidth=1
        )
        
        # Listbox for suggestions
        self.listbox = tk.Listbox(
            self.popup,
            bg="#2B2B2B",
            fg="#CCCCCC",
            selectbackground="#3B8ED0",
            selectforeground="#FFFFFF",
            font=("monospace", 11),
            height=8,
            width=50,
            borderwidth=0,
            highlightthickness=0
        )
        
        self.listbox.pack(fill="both", expand=True)
        
        # Bind events
        self.listbox.bind("<<ListboxSelect>>", lambda event: self._on_select(event))
        self.listbox.bind("<Return>", lambda event: self._on_enter(event))
        self.listbox.bind("<Escape>", lambda event: self._hide(event))
        self.listbox.bind("<Tab>", lambda event: self._on_tab(event))
        
        # Current suggestions
        self.suggestions: List[CompletionSuggestion] = []
        self.selected_index = 0
        
        # Hide initially
        self._hide()
    
    def show(self, suggestions: List[CompletionSuggestion], x: int, y: int):
        """Show popup with suggestions at given coordinates."""
        if not suggestions:
            self._hide()
            return
        
        self.suggestions = suggestions
        self.listbox.delete(0, tk.END)
        
        # Add suggestions to listbox
        for i, suggestion in enumerate(suggestions):
            # Create display text with confidence indicator
            confidence_bar = "█" * int(suggestion.confidence * 5)
            display_text = f"{confidence_bar} {suggestion.text[:50]}"
            
            if len(suggestion.text) > 50:
                display_text += "..."
            
            self.listbox.insert(i, display_text)
        
        # Select first item
        self.listbox.selection_set(0)
        self.selected_index = 0
        
        # Position popup
        self.popup.update_idletasks()
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        
        # Adjust position if near screen edges
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        if x + popup_width > screen_width:
            x = screen_width - popup_width - 10
        
        if y + popup_height > screen_height:
            y = y - popup_height - 30
        
        self.popup.wm_geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        self.popup.deiconify()
        self.listbox.focus_set()
    
    def _hide(self, event=None):
        """Hide the popup."""
        self.popup.withdraw()
    
    def _on_select(self, event):
        """Handle selection change."""
        selection = self.listbox.curselection()
        if selection:
            self.selected_index = selection[0]
    
    def _on_enter(self, event):
        """Handle Enter key - insert selected suggestion."""
        self._insert_selected()
        return "break"
    
    def _on_tab(self, event):
        """Handle Tab key - insert selected suggestion."""
        self._insert_selected()
        return "break"
    
    def _insert_selected(self):
        """Insert selected suggestion into text widget."""
        if self.selected_index < len(self.suggestions):
            suggestion = self.suggestions[self.selected_index]
            self.on_select(suggestion.text)
            self._hide()
    
    def move_selection(self, direction: int):
        """Move selection up or down."""
        new_index = self.selected_index + direction
        
        if 0 <= new_index < len(self.suggestions):
            self.selected_index = new_index
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(new_index)
            self.listbox.see(new_index)
    
    def is_visible(self) -> bool:
        """Check if popup is visible."""
        return self.popup.winfo_viewable()
