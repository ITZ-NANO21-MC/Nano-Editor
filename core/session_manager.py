"""Session Manager: Save and restore editor state across restarts."""
import json
import os
from pathlib import Path
from logger import logger


class SessionManager:
    """Manages saving and restoring the editor session state."""
    
    SESSION_FILE = ".nano/session.json"
    GLOBAL_DIR = Path.home() / ".nano-editor"
    LAST_WORKSPACE_FILE = GLOBAL_DIR / "last_workspace.json"
    
    def __init__(self, app):
        self.app = app
        self.GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
    
    @property
    def session_path(self) -> Path:
        """Get the path to the session file, based on current workspace."""
        if hasattr(self.app, 'workspace_manager') and self.app.workspace_manager.folders:
            base = Path(self.app.workspace_manager.folders[0])
        else:
            base = self.GLOBAL_DIR
        
        path = base / self.SESSION_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _save_last_workspace(self):
        """Save the current workspace path globally so we can restore it on next launch."""
        try:
            workspace = None
            if hasattr(self.app, 'workspace_manager') and self.app.workspace_manager.folders:
                workspace = self.app.workspace_manager.folders[0]
            
            with open(self.LAST_WORKSPACE_FILE, 'w', encoding='utf-8') as f:
                json.dump({"last_workspace": workspace}, f)
        except Exception as e:
            logger.error(f"Failed to save last workspace: {e}")

    def _get_last_workspace(self) -> str:
        """Read the last workspace path from global config."""
        try:
            if self.LAST_WORKSPACE_FILE.exists():
                with open(self.LAST_WORKSPACE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                ws = data.get("last_workspace")
                if ws and os.path.isdir(ws):
                    return ws
        except Exception:
            pass
        return None

    def save_session(self):
        """Save complete editor session to JSON."""
        try:
            session = {
                "open_files": self._collect_open_files(),
                "ui": self._collect_ui_state()
            }
            
            with open(self.session_path, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
            
            self._save_last_workspace()
            logger.info(f"Session saved to {self.session_path}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def restore_session(self, initial=False):
        """Restore editor session from JSON.
        
        Args:
            initial: If True, check last_workspace.json to restore the 
                     previous workspace first (used only on startup).
        """
        # On startup, check if there was a previous workspace to restore
        if initial:
            last_ws = self._get_last_workspace()
            if last_ws:
                if hasattr(self.app, 'workspace_manager'):
                    current_folders = self.app.workspace_manager.folders
                    if not current_folders or current_folders[0] != last_ws:
                        self.app.workspace_manager.clear()
                        self.app.workspace_manager.add_folder(last_ws)
        
        path = self.session_path
        if not path.exists():
            logger.info("No session file found, starting fresh.")
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                session = json.load(f)
            
            self._restore_ui_state(session.get("ui", {}))
            self._restore_open_files(session.get("open_files", []))
            
            logger.info(f"Session restored from {path}")
        except Exception as e:
            logger.error(f"Failed to restore session: {e}")

    def _collect_open_files(self) -> list:
        """Collect info about all open tabs."""
        files = []
        if not hasattr(self.app, 'tab_manager'):
            return files
            
        tab_mgr = self.app.tab_manager
        current_idx = tab_mgr.current_tab_index
        
        for i, tab in enumerate(tab_mgr.tabs):
            if tab.file_path and os.path.isfile(tab.file_path):
                # Try to get live cursor position from editor
                cursor = tab.cursor_position
                scroll = tab.scroll_position
                
                if hasattr(tab_mgr, 'editor') and i == current_idx:
                    try:
                        cursor = tab_mgr.editor.index("insert")
                        scroll = tab_mgr.editor.yview()[0]
                    except Exception:
                        pass
                
                files.append({
                    "path": tab.file_path,
                    "cursor": str(cursor),
                    "scroll": float(scroll),
                    "active": i == current_idx
                })
        return files

    def _collect_ui_state(self) -> dict:
        """Collect UI configuration state."""
        ui = {}
        
        if hasattr(self.app, 'settings_panel'):
            sp = self.app.settings_panel
            ui["font_size"] = sp.font_size_var.get()
            ui["syntax_theme"] = sp.style_var.get()
            ui["show_terminal"] = sp.show_terminal_var.get()
            ui["show_ai"] = sp.show_ai_var.get()
            ui["provider"] = sp.provider_var.get()
            ui["model"] = sp.ai_model_var.get()
        
        if hasattr(self.app, 'sidebar') and hasattr(self.app.sidebar, 'current_view'):
            ui["sidebar_view"] = self.app.sidebar.current_view
        
        # Window geometry
        try:
            ui["window_geometry"] = self.app.geometry()
        except Exception:
            pass
        
        return ui

    def _restore_ui_state(self, ui: dict):
        """Restore UI configuration from session data."""
        if not ui:
            return
            
        if hasattr(self.app, 'settings_panel'):
            sp = self.app.settings_panel
            
            if "font_size" in ui:
                sp.font_size_var.set(ui["font_size"])
                self.app.update_font_size(ui["font_size"])
            
            if "syntax_theme" in ui:
                sp.style_var.set(ui["syntax_theme"])
                self.app.set_syntax_theme(ui["syntax_theme"])
            
            if "show_terminal" in ui:
                sp.show_terminal_var.set(ui["show_terminal"])
            
            if "show_ai" in ui:
                sp.show_ai_var.set(ui["show_ai"])
            
            # Apply panel visibility
            sp.update_panels()
        
        if "sidebar_view" in ui and hasattr(self.app, 'sidebar'):
            self.app.sidebar.switch_view(ui["sidebar_view"])
        
        if "window_geometry" in ui:
            try:
                self.app.geometry(ui["window_geometry"])
            except Exception:
                pass

    def _restore_open_files(self, files: list):
        """Restore previously open files."""
        if not files or not hasattr(self.app, 'open_file'):
            return
        
        active_path = None
        
        for file_info in files:
            path = file_info.get("path", "")
            if not path or not os.path.isfile(path):
                logger.warning(f"Session: skipping missing file {path}")
                continue
            
            try:
                self.app.open_file(path)
                
                # Restore cursor and scroll position
                cursor = file_info.get("cursor", "1.0")
                scroll = file_info.get("scroll", 0.0)
                
                if hasattr(self.app, 'tab_manager'):
                    tab = self.app.tab_manager.get_current_tab()
                    if tab:
                        tab.cursor_position = cursor
                        tab.scroll_position = scroll
                    
                    # Apply cursor/scroll to the live editor
                    if hasattr(self.app.tab_manager, 'editor') and self.app.tab_manager.editor:
                        editor = self.app.tab_manager.editor
                        try:
                            editor.mark_set("insert", cursor)
                            editor.see(cursor)
                            editor.yview_moveto(scroll)
                        except Exception:
                            pass
                
                if file_info.get("active", False):
                    active_path = path
                    
            except Exception as e:
                logger.warning(f"Session: failed to open {path}: {e}")
        
        # Switch to the previously active tab
        if active_path and hasattr(self.app, 'tab_manager'):
            for i, tab in enumerate(self.app.tab_manager.tabs):
                if tab.file_path == active_path:
                    self.app.tab_manager.switch_tab(i)
                    break
