from tkinter import ttk
import os
import tkinter


class FileTree(ttk.Treeview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.heading("#0", text="Project", anchor="w")
        self.bind("<<TreeviewOpen>>", self.on_open)
        self.bind("<Double-1>", self.on_double_click)
        
        try:
            default_path = os.path.expanduser("~")
            if not os.path.isdir(default_path):
                default_path = os.getcwd()
            self.populate_tree(default_path)
        except (OSError, tkinter.TclError):
            pass

    def populate_tree(self, path):
        if not path or not isinstance(path, str):
            return
        
        if not os.path.exists(path):
            return
        
        if not os.path.isdir(path):
            path = os.path.dirname(path)
            if not path or not os.path.isdir(path):
                return
        
        try:
            self.delete(*self.get_children())
            root_node = self.insert("", "end", text=path, values=[path], open=True)
            
            if root_node:
                self.populate_node(root_node, path)
        except (tkinter.TclError, OSError):
            pass

    def populate_node(self, parent, path):
        try:
            items = os.listdir(path)
        except (PermissionError, FileNotFoundError, OSError):
            return
        
        for item in items:
            try:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    node = self.insert(parent, "end", text=item, values=[item_path], open=False)
                    self.insert(node, "end", text="dummy")
                else:
                    self.insert(parent, "end", text=item, values=[item_path])
            except (PermissionError, OSError):
                continue

    def on_open(self, event):
        try:
            node_id = self.focus()
            node = self.item(node_id)
            if not node.get("values"):
                return
            path = node["values"][0]
            if os.path.isdir(path):
                children = self.get_children(node_id)
                if len(children) == 1 and self.item(children[0])["text"] == "dummy":
                    self.delete(children[0])
                    self.populate_node(node_id, path)
        except (IndexError, KeyError, OSError):
            pass

    def on_double_click(self, event):
        try:
            node_id = self.focus()
            node = self.item(node_id)
            if not node.get("values"):
                return
            path = node["values"][0]
            if os.path.isfile(path):
                self.master.master.open_file(path)
        except (IndexError, KeyError, OSError, AttributeError):
            pass
