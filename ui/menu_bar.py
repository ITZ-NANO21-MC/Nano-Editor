"""Modern horizontal menu bar for NanoEditor."""
import customtkinter as ctk
import tkinter as tk

class ModernMenuBar(ctk.CTkFrame):
    """Modern horizontal menu bar."""
    def __init__(self, master, app):
        super().__init__(master, height=35, fg_color=("#E5E5E5", "#1E1E1E"))
        self.app = app
        self.pack_propagate(False)
        
        menus = [
            ("File", [
                ("New Tab (Ctrl+N)", lambda: app.tab_manager.new_tab()),
                ("Open File... (Ctrl+O)", app.open_file),
                ("Open Folder...", app.open_folder),
                None,
                ("Add Folder to Workspace...", app.add_folder_to_workspace),
                ("Open Workspace...", app.open_workspace),
                ("Save Workspace As...", app.save_workspace_as),
                ("Close Workspace", app.close_workspace),
                None,
                ("Save (Ctrl+S)", app.save_file),
                ("Save As...", app.save_file_as),
                None,
                ("Close Tab (Ctrl+W)", lambda: app.tab_manager.close_tab(app.tab_manager.current_tab_index)),
                None,
                ("Exit", app.quit)
            ]),
            ("Edit", [
                ("Find & Replace", app.open_find_replace_window),
                ("Search in Project", app.open_project_search),
                None,
                ("Goto Definition", app.handle_goto_definition),
                ("Find References", app.find_references)
            ]),
            ("Selection", [
                ("Select All (Ctrl+A)", lambda: app.select_all()),
                ("Copy (Ctrl+C)", lambda: app.copy_text()),
                ("Cut (Ctrl+X)", lambda: app.cut_text()),
                ("Paste (Ctrl+V)", lambda: app.paste_text())
            ]),
            ("View", [
                ("Toggle Terminal", app.toggle_terminal),
                ("Toggle AI Panel", app.toggle_gemini),
                ("Toggle File Tree", app.toggle_file_tree),
                None,
                ("Light Theme", lambda: app.set_theme("light")),
                ("Dark Theme", lambda: app.set_theme("dark"))
            ]),
            ("Go", [
                ("Goto Definition (F12)", app.handle_goto_definition),
                ("Find References", app.find_references)
            ]),
            ("Run", [
                ("Run Task...", app.show_task_runner),
                None,
                ("Run in Terminal", app.run_current_file),
                ("Clear Terminal", lambda: app.terminal.clear_terminal())
            ]),
            ("Terminal", [
                ("Show Terminal", lambda: app.terminal.grid()),
                ("Hide Terminal", lambda: app.terminal.grid_remove()),
                ("Clear", lambda: app.terminal.clear_terminal())
            ]),
            ("AI Assistant", [
                ("Explain Code", app.ai_explain_code),
                ("Generate Code...", app.ai_generate_code),
                None,
                ("Refactor Code", app.ai_refactor_code),
                ("Fix Errors...", app.ai_fix_errors),
                ("Optimize Code", app.ai_optimize_code),
                None,
                ("Generate Docstring", app.ai_generate_docstring),
                ("Translate Code...", app.ai_translate_code),
                ("Create Project...", app.ai_create_project),
                None,
                ("Create File...", app.ai_create_file),
                ("Modify Current File...", app.ai_modify_current_file),
                ("Add Function...", app.ai_add_function)
            ]),
            ("Help", [
                ("About", app.show_about),
                ("Shortcuts", app.show_shortcuts)
            ])
        ]
        
        # Diccionario para almacenar botones y sus menús
        self.menu_buttons = {}
        
        for label, items in menus:
            btn = ctk.CTkButton(
                self, text=label, width=60, height=28,
                fg_color="transparent", hover_color=("#D0D0D0", "#2D2D2D"),
                text_color=("#333333", "#CCCCCC"),
                corner_radius=4, font=("Segoe UI", 12)
            )
            btn.pack(side="left", padx=2, pady=3)
            
            # Almacenar referencia al botón y sus items
            self.menu_buttons[btn] = items
            
            # Vincular evento al botón específico
            btn.configure(command=lambda b=btn: self.show_dropdown(b))
    
    def show_dropdown(self, button):
        """Show dropdown menu at the specific button location."""
        # Obtener los items del menú para este botón
        items = self.menu_buttons.get(button)
        if not items:
            return
        
        # Calcular posición del botón en pantalla
        button_x = button.winfo_rootx()
        button_y = button.winfo_rooty() + button.winfo_height()
        
        # Crear menú desplegable
        menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 10))
        
        # Añadir items al menú
        for item in items:
            if item is None:
                menu.add_separator()
            else:
                label, command = item
                menu.add_command(label=label, command=command)
        
        try:
            # Mostrar menú en la posición correcta
            menu.tk_popup(button_x, button_y)
        finally:
            # Liberar foco del menú al cerrar
            menu.grab_release()
