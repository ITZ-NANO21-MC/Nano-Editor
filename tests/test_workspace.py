import pytest
import os
import json
import tempfile
from unittest.mock import MagicMock
from core.workspace.workspace_manager import WorkspaceManager
from core.tasks.task_runner import TaskRunner

@pytest.fixture
def workspace_manager():
    return WorkspaceManager()

@pytest.fixture
def mock_app(workspace_manager):
    app = MagicMock()
    app.workspace_manager = workspace_manager
    return app

def test_workspace_add_remove_folder(workspace_manager):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test add valid
        assert workspace_manager.add_folder(temp_dir) is True
        assert len(workspace_manager.get_folders()) == 1
        
        # Test add invalid
        assert workspace_manager.add_folder("/path/does/not/exist/999") is False
        
        # Test add duplicate
        assert workspace_manager.add_folder(temp_dir) is False
        assert len(workspace_manager.get_folders()) == 1
        
        # Test remove valid
        assert workspace_manager.remove_folder(temp_dir) is True
        assert len(workspace_manager.get_folders()) == 0

def test_workspace_save_load(workspace_manager):
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_manager.add_folder(temp_dir)
        workspace_file = os.path.join(temp_dir, "test.nano-workspace")
        
        # Test Save
        assert workspace_manager.save_workspace(workspace_file) is True
        assert os.path.exists(workspace_file)
        
        # Test Load
        new_manager = WorkspaceManager()
        assert new_manager.load_workspace(workspace_file) is True
        assert len(new_manager.get_folders()) == 1
        assert new_manager.get_folders()[0] == os.path.abspath(temp_dir)

def test_task_runner_load_tasks(mock_app):
    runner = TaskRunner(mock_app)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        nano_dir = os.path.join(temp_dir, ".nano")
        os.makedirs(nano_dir)
        tasks_file = os.path.join(nano_dir, "tasks.json")
        
        test_tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Test Task",
                    "type": "shell",
                    "command": "echo 'hello'"
                }
            ]
        }
        
        with open(tasks_file, "w") as f:
            json.dump(test_tasks, f)
            
        assert runner.load_tasks(temp_dir) is True
        assert len(runner.tasks) == 1
        assert "Test Task" in runner.tasks

def test_task_runner_execute(mock_app):
    runner = TaskRunner(mock_app)
    runner.tasks = {
        "Echo": {
            "label": "Echo",
            "command": "echo",
            "args": ["Hello World"]
        }
    }
    
    assert runner.execute_task("Echo") is True
    # Verify proper quote escaping
    mock_app.terminal.send_input.assert_called_with("echo 'Hello World'")
    
    assert runner.execute_task("Unknown") is False
