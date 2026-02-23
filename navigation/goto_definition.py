"""Goto definition functionality using Jedi."""
import jedi
import customtkinter
import tkinter


class GotoDefinition:
    """Handle goto definition for code navigation."""
    
    def __init__(self, text_widget, open_file_callback):
        self.text_widget = text_widget
        self.open_file_callback = open_file_callback
    
    def goto_definition(self):
        """Jump to definition of symbol under cursor."""
        try:
            # Get code and cursor position
            code = self.text_widget.get("1.0", "end-1c")
            cursor_pos = self.text_widget.index(customtkinter.INSERT)
            line, col = map(int, cursor_pos.split('.'))
            
            # Use Jedi to find definition
            script = jedi.Script(code)
            definitions = script.goto(line=line, column=col)
            
            if not definitions:
                # Try to find references if no definition
                definitions = script.get_references(line=line, column=col)
            
            if definitions:
                definition = definitions[0]
                
                # Check if definition is in another file
                if definition.module_path:
                    file_path = str(definition.module_path)
                    line_num = definition.line
                    
                    # Open file and jump to line
                    self.open_file_callback(file_path, line_num)
                else:
                    # Definition in current file
                    if definition.line:
                        self.jump_to_line(definition.line)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Goto definition error: {e}")
            return False
    
    def jump_to_line(self, line_num):
        """Jump to specific line in current file."""
        try:
            self.text_widget.mark_set(customtkinter.INSERT, f"{line_num}.0")
            self.text_widget.see(f"{line_num}.0")
            
            # Highlight the line briefly
            self.text_widget.tag_remove("highlight", "1.0", "end")
            self.text_widget.tag_add("highlight", f"{line_num}.0", f"{line_num}.end")
            self.text_widget.tag_config("highlight", background="#3B8ED0")
            
            # Remove highlight after 1 second
            self.text_widget.after(1000, lambda: self.text_widget.tag_remove("highlight", "1.0", "end"))
        except Exception:
            pass
    
    def find_symbol_references(self):
        """Find all references to symbol under cursor."""
        try:
            code = self.text_widget.get("1.0", "end-1c")
            cursor_pos = self.text_widget.index(customtkinter.INSERT)
            line, col = map(int, cursor_pos.split('.'))
            
            script = jedi.Script(code)
            references = script.get_references(line=line, column=col)
            
            return references
        except Exception:
            return []


def setup_goto_definition_bindings(text_widget, goto_handler):
    """Setup keyboard bindings for goto definition."""
    # Ctrl+Click or F12 to goto definition
    text_widget.bind("<Control-Button-1>", lambda e: goto_handler())
    text_widget.bind("<F12>", lambda e: goto_handler())
