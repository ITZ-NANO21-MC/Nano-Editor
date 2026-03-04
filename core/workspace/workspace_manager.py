"""Workspace Manager for Multi-folder projects."""
import json
import os
from typing import List, Optional
from event_bus import event_bus, Events
from logger import logger

class WorkspaceManager:
    """Manages workspace configuration and multiple root folders."""
    
    def __init__(self):
        self.folders: List[str] = []
        self.workspace_file: Optional[str] = None
        
    def add_folder(self, path: str) -> bool:
        """Add a folder to the workspace."""
        abs_path = os.path.abspath(path)
        if not os.path.isdir(abs_path):
            logger.error(f"Cannot add non-directory path: {abs_path}")
            return False
            
        if abs_path not in self.folders:
            self.folders.append(abs_path)
            self._notify_change()
            return True
        return False
        
    def remove_folder(self, path: str) -> bool:
        """Remove a folder from the workspace."""
        abs_path = os.path.abspath(path)
        if abs_path in self.folders:
            self.folders.remove(abs_path)
            self._notify_change()
            return True
        return False
        
    def get_folders(self) -> List[str]:
        """Return the list of current workspace folders."""
        return self.folders.copy()
        
    def clear(self):
        """Clear the current workspace."""
        self.folders.clear()
        self.workspace_file = None
        self._notify_change()
        
    def save_workspace(self, filepath: str) -> bool:
        """Save current workspace config to a JSON file."""
        data = {
            "folders": self.folders
        }
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            self.workspace_file = filepath
            logger.info(f"Workspace saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save workspace: {e}")
            return False
            
    def load_workspace(self, filepath: str) -> bool:
        """Load workspace config from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if "folders" in data:
                self.folders.clear()
                for path in data["folders"]:
                    if os.path.exists(path):
                        self.folders.append(path)
                self.workspace_file = filepath
                self._notify_change()
                logger.info(f"Workspace loaded from {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load workspace: {e}")
            return False
            
    def _notify_change(self):
        """Emit event when workspace folders change."""
        event_bus.emit(Events.WORKSPACE_CHANGED, self.folders)
