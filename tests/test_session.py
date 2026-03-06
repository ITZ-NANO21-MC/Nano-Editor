"""Unit tests for SessionManager."""
import json
import os
import tempfile
import shutil
import pytest


class MockTab:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.cursor_position = "1.0"
        self.scroll_position = 0.0
        self.content = ""
        self.modified = False


class MockTabManager:
    def __init__(self):
        self.tabs = []
        self.current_tab_index = 0
    
    def get_current_tab(self):
        if self.tabs:
            return self.tabs[self.current_tab_index]
        return None
    
    def switch_to_tab(self, index):
        self.current_tab_index = index


class MockSettingsPanel:
    def __init__(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        self.font_size_var = tk.IntVar(root, value=13)
        self.style_var = tk.StringVar(root, value="monokai")
        self.show_terminal_var = tk.BooleanVar(root, value=True)
        self.show_ai_var = tk.BooleanVar(root, value=True)
        self.provider_var = tk.StringVar(root, value="Gemini")
        self.ai_model_var = tk.StringVar(root, value="gemini-2.0-flash")
        self._root = root
    
    def update_panels(self):
        pass
    
    def destroy(self):
        self._root.destroy()


class MockWorkspaceManager:
    def __init__(self, folders=None):
        self.folders = folders or []


class MockSidebar:
    def __init__(self):
        self.current_view = "explorer"
    
    def switch_view(self, view):
        self.current_view = view


class MockApp:
    def __init__(self, workspace_dir):
        self.workspace_manager = MockWorkspaceManager([workspace_dir])
        self.tab_manager = MockTabManager()
        self.settings_panel = MockSettingsPanel()
        self.sidebar = MockSidebar()
        self._geometry = "1400x900"
        self._opened_files = []
    
    def geometry(self, value=None):
        if value:
            self._geometry = value
        return self._geometry
    
    def open_file(self, path):
        self._opened_files.append(path)
        tab = MockTab(path)
        self.tab_manager.tabs.append(tab)
    
    def update_font_size(self, size):
        pass
    
    def set_syntax_theme(self, theme):
        pass
    
    def destroy(self):
        self.settings_panel.destroy()


@pytest.fixture
def temp_workspace():
    """Create a temp workspace directory with sample files."""
    temp_dir = tempfile.mkdtemp()
    nano_dir = os.path.join(temp_dir, ".nano")
    os.makedirs(nano_dir, exist_ok=True)
    
    # Create sample files
    for name in ["file1.py", "file2.py", "file3.txt"]:
        with open(os.path.join(temp_dir, name), 'w') as f:
            f.write(f"# {name}\n")
    
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_save_and_restore_session(temp_workspace):
    """Test that a session can be saved and restored."""
    from core.session_manager import SessionManager
    
    # Setup mock app
    app = MockApp(temp_workspace)
    app.tab_manager.tabs = [
        MockTab(os.path.join(temp_workspace, "file1.py")),
        MockTab(os.path.join(temp_workspace, "file2.py")),
    ]
    app.tab_manager.tabs[0].cursor_position = "10.5"
    app.tab_manager.tabs[0].scroll_position = 0.25
    app.tab_manager.current_tab_index = 1  # file2.py is active
    app.settings_panel.font_size_var.set(16)
    app.settings_panel.style_var.set("friendly")
    
    # Save session
    sm = SessionManager(app)
    sm.save_session()
    
    # Verify session file was created
    session_path = sm.session_path
    assert session_path.exists()
    
    with open(session_path, 'r') as f:
        data = json.load(f)
    
    assert len(data["open_files"]) == 2
    assert data["open_files"][0]["cursor"] == "10.5"
    assert data["open_files"][0]["scroll"] == 0.25
    assert data["open_files"][1]["active"] is True
    assert data["ui"]["font_size"] == 16
    assert data["ui"]["syntax_theme"] == "friendly"
    
    # Restore into a fresh app
    app2 = MockApp(temp_workspace)
    sm2 = SessionManager(app2)
    sm2.restore_session()
    
    assert len(app2._opened_files) == 2
    assert app2._opened_files[0].endswith("file1.py")
    assert app2._opened_files[1].endswith("file2.py")
    
    app.destroy()
    app2.destroy()


def test_missing_files_are_skipped(temp_workspace):
    """Test that missing files are gracefully skipped."""
    from core.session_manager import SessionManager
    
    # Create a session with a file that doesn't exist
    nano_dir = os.path.join(temp_workspace, ".nano")
    session_data = {
        "open_files": [
            {"path": os.path.join(temp_workspace, "file1.py"), "cursor": "1.0", "scroll": 0.0, "active": True},
            {"path": os.path.join(temp_workspace, "nonexistent.py"), "cursor": "5.0", "scroll": 0.5, "active": False},
        ],
        "ui": {}
    }
    with open(os.path.join(nano_dir, "session.json"), 'w') as f:
        json.dump(session_data, f)
    
    app = MockApp(temp_workspace)
    sm = SessionManager(app)
    sm.restore_session()
    
    # Only file1.py should be opened
    assert len(app._opened_files) == 1
    assert app._opened_files[0].endswith("file1.py")
    
    app.destroy()


def test_no_session_file(temp_workspace):
    """Test graceful handling when no session file exists."""
    from core.session_manager import SessionManager
    
    app = MockApp(temp_workspace)
    sm = SessionManager(app)
    sm.restore_session()  # Should not crash
    
    assert len(app._opened_files) == 0
    app.destroy()
