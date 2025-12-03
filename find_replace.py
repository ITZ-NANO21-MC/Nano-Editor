import customtkinter


class FindReplaceWindow(customtkinter.CTkToplevel):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget

        self.title("Find and Replace")
        self.geometry("400x150")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        self.find_label = customtkinter.CTkLabel(self, text="Find:")
        self.find_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.find_entry = customtkinter.CTkEntry(self)
        self.find_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        self.replace_label = customtkinter.CTkLabel(self, text="Replace:")
        self.replace_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.replace_entry = customtkinter.CTkEntry(self)
        self.replace_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        self.find_button = customtkinter.CTkButton(self, text="Find", command=self.find)
        self.find_button.grid(row=2, column=0, padx=10, pady=10)

        self.replace_button = customtkinter.CTkButton(self, text="Replace", command=self.replace)
        self.replace_button.grid(row=2, column=1, padx=10, pady=10)

        self.replace_all_button = customtkinter.CTkButton(self, text="Replace All", command=self.replace_all)
        self.replace_all_button.grid(row=2, column=2, padx=10, pady=10)

    def find(self):
        find_text = self.find_entry.get()
        if not find_text:
            return
        
        start_pos = self.text_widget.search(find_text, "1.0", stopindex="end")
        if not start_pos:
            return
        
        end_pos = f"{start_pos}+{len(find_text)}c"
        self.text_widget.tag_remove("sel", "1.0", "end")
        self.text_widget.tag_add("sel", start_pos, end_pos)
        self.text_widget.mark_set("insert", start_pos)
        self.text_widget.see(start_pos)
        self.focus()

    def replace(self):
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        if not find_text or not self.text_widget.tag_ranges("sel"):
            return
        
        start_pos = self.text_widget.index("sel.first")
        end_pos = self.text_widget.index("sel.last")
        self.text_widget.delete(start_pos, end_pos)
        self.text_widget.insert(start_pos, replace_text)
        self.find()

    def replace_all(self):
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        if not find_text:
            return
        
        content = self.text_widget.get("1.0", "end")
        new_content = content.replace(find_text, replace_text)
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", new_content)
