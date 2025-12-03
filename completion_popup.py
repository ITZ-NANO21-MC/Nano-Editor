import customtkinter
import tkinter


class CompletionPopup(customtkinter.CTkToplevel):
    def __init__(self, master, text_widget, completions, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.completions = completions
        self.overrideredirect(True)  # Remove window decorations

        # Use hardcoded, generally acceptable colors for compatibility
        bg_color = "gray20" if customtkinter.get_appearance_mode() == "Dark" else "gray90"
        fg_color = "white" if customtkinter.get_appearance_mode() == "Dark" else "black"
        select_bg_color = "#3B8ED0"  # A common blue for selection
        select_fg_color = "white"

        self.listbox = tkinter.Listbox(self,
                                       bg=bg_color,
                                       fg=fg_color,
                                       selectbackground=select_bg_color,
                                       selectforeground=select_fg_color,
                                       highlightthickness=0,
                                       borderwidth=0)
        self.listbox.pack(fill="both", expand=True)

        for comp in self.completions:
            self.listbox.insert("end", comp.name)

        self.listbox.bind("<Return>", self.handle_key_event)
        self.listbox.bind("<Up>", self.handle_key_event)
        self.listbox.bind("<Down>", self.handle_key_event)
        self.listbox.bind("<Escape>", self.handle_key_event)

        self.transient(master)  # Make it appear on top of the main window
        self.withdraw()  # Hide it initially

    def show(self):
        if not self.completions:
            return

        # Get cursor position
        bbox = self.text_widget.bbox(customtkinter.INSERT)
        if not bbox:
            return

        x = self.text_widget.winfo_rootx() + bbox[0]
        y = self.text_widget.winfo_rooty() + bbox[1] + bbox[3]  # bbox[3] is height

        self.geometry(f"+{x}+{y}")
        self.deiconify()  # Show the window
        self.listbox.focus_set()
        self.listbox.selection_set(0)  # Select first item

    def hide(self, event=None):  # Hide the window
        self.withdraw()  # Hide the window

    def select_completion(self):
        if not self.listbox.curselection():
            return

        try:
            selected_index = self.listbox.curselection()[0]
            
            if selected_index >= len(self.completions):
                return
            
            selected_completion = self.completions[selected_index].name
            
            cursor_index = self.text_widget.index(customtkinter.INSERT)
            line, col = map(int, cursor_index.split('.'))
            
            word_start = self.text_widget.index(f"{line}.{col} wordstart")
            word_end = self.text_widget.index(customtkinter.INSERT)
            
            self.text_widget.delete(word_start, word_end)
            self.text_widget.insert(customtkinter.INSERT, selected_completion)
            self.hide()
            self.text_widget.focus_set()
        except (IndexError, ValueError, AttributeError, tkinter.TclError) as e:
            # Silently fail if widget is destroyed or in invalid state
            self.hide()

    def _move_selection(self, direction):
        """Move listbox selection up (-1) or down (1)."""
        self.listbox.selection_clear(0, "end")
        current_selection = self.listbox.curselection()
        list_size = self.listbox.size()
        
        if not list_size:
            return
        
        if current_selection:
            current_index = current_selection[0]
            new_index = current_index + direction
            new_index = max(0, min(list_size - 1, new_index))
        else:
            new_index = 0 if direction > 0 else list_size - 1
        
        self.listbox.selection_set(new_index)
        self.listbox.see(new_index)
    
    def handle_key_event(self, event):
        key_actions = {
            "Up": lambda: self._move_selection(-1),
            "Down": lambda: self._move_selection(1),
            "Return": self.select_completion,
            "Escape": self.hide
        }
        
        action = key_actions.get(event.keysym)
        if action:
            action()
        
        return "break"
