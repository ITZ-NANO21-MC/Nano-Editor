from enum import Enum
from typing import Callable, Optional, Dict, Any

class PermissionLevel(Enum):
    PARANOID = 1    # Ask permission for ALL tool calls
    SAFE = 2        # Ask permission for potentially dangerous tools (write, delete, execute shell)
    AUTONOMOUS = 3  # Never ask for permission, run automatically

class AISecurityManager:
    """Manages permissions and human-in-the-loop approvals for the AI Agent."""
    
    def __init__(self, level: PermissionLevel = PermissionLevel.SAFE):
        self.level = level
        
        # Define which tools are considered safe/unsafe
        # Read-only tools are usually safe. Write/Execute tools are unsafe.
        self.unsafe_tools = {
            "write_file",
            "terminal_run",
            "create_file",
            "delete_file",
            "replace_file_content"
        }
        
    def requires_approval(self, tool_name: str, tool_args: Dict[str, Any]) -> bool:
        """Determines if a specific tool call requires human approval."""
        if self.level == PermissionLevel.AUTONOMOUS:
            return False
            
        if self.level == PermissionLevel.PARANOID:
            return True
            
        if self.level == PermissionLevel.SAFE:
            # If the tool is in our predefined list of unsafe tools, require approval
            if tool_name in self.unsafe_tools:
                # We could add more granular checks here based on tool_args
                # e.g., allow writing to temp files but not system files
                return True
            return False
            
        return True # Default to secure
