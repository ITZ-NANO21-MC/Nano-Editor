"""Task Runner for handling tasks.json configurations."""
import json
import os
import shlex
import threading
from typing import Dict, Any, Optional
from event_bus import event_bus, Events
from logger import logger


class TaskRunner:
    """Reads projects's tasks.json and executes them via Terminal."""
    
    def __init__(self, app):
        self.app = app
        self.tasks: Dict[str, Any] = {}
        # Subscribe to workspace changes to reload tasks
        event_bus.subscribe(Events.WORKSPACE_CHANGED, self._on_workspace_changed)
        
    def _on_workspace_changed(self, folders: list) -> None:
        """Reload tasks when workspace changes."""
        self.tasks.clear()
        if not folders:
            return
            
        # Prioritize the first root folder for tasks.json
        root_dir = folders[0]
        self.load_tasks(root_dir)
        
    def load_tasks(self, root_dir: str) -> bool:
        """Load tasks.json from the given workspace root directory."""
        tasks_file = os.path.join(root_dir, ".nano", "tasks.json")
        if not os.path.exists(tasks_file):
            return False
            
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if "tasks" in data and isinstance(data["tasks"], list):
                self.tasks.clear()
                for task in data["tasks"]:
                    if "label" in task and "command" in task:
                        self.tasks[task["label"]] = task
                logger.info(f"Loaded {len(self.tasks)} tasks from {tasks_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading tasks.json: {e}")
            return False

    def execute_task(self, task_label: str) -> bool:
        """Execute a task by its label through the terminal."""
        if task_label not in self.tasks:
            logger.warning(f"Task '{task_label}' not found.")
            return False
            
        task = self.tasks[task_label]
        command = task["command"]
        
        args = task.get("args", [])
        if args:
            safe_args = " ".join(shlex.quote(str(a)) for a in args)
            command = f"{command} {safe_args}"
            
        # Determine working directory
        cwd = task.get("options", {}).get("cwd", None)
        if cwd is None and hasattr(self.app, 'workspace_manager') and self.app.workspace_manager.folders:
            # Default to the first root folder
            cwd = self.app.workspace_manager.folders[0]
            
        logger.info(f"Executing task '{task_label}': {command}")
        
        # Ensure terminal is visible
        if hasattr(self.app, 'terminal'):
            self.app.terminal.grid()
            # Set working directory directly on the terminal
            if cwd and os.path.isdir(cwd):
                self.app.terminal.cwd = cwd
            # Execute the command
            self.app.terminal._execute_command(command)
            return True
        return False
        
    def get_task_labels(self) -> list:
        """Get a list of all available task labels."""
        return list(self.tasks.keys())
