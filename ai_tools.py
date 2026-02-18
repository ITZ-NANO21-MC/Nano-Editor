"""
AI Tools Registry
Defines the tools (functions) that the AI Agent can execute.
"""
import os
import subprocess
import json
from typing import Dict, Any, List, Callable, Optional
from config import config
from logger import logger

class ToolRegistry:
    """Registry for AI-callable tools."""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []
        
        # Register basic tools
        self.register_tool(
            name="fs_read_file",
            func=self.fs_read_file,
            description="Read the contents of a file.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file"}
                },
                "required": ["path"]
            }
        )
        
        self.register_tool(
            name="fs_list_dir",
            func=self.fs_list_dir,
            description="List contents of a directory.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the directory"}
                },
                "required": ["path"]
            }
        )
        
        self.register_tool(
            name="fs_write_file",
            func=self.fs_write_file,
            description="Write content to a file. Overwrites if exists.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file"},
                    "content": {"type": "string", "description": "Text content to write"}
                },
                "required": ["path", "content"]
            }
        )
        
        self.register_tool(
            name="terminal_run",
            func=self.terminal_run,
            description="Run a shell command and get output.",
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"]
            }
        )

    def register_tool(self, name: str, func: Callable, description: str, parameters: Dict[str, Any]):
        """Register a new tool with its JSON schema."""
        self._tools[name] = func
        
        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self._schemas.append(schema)
        logger.info(f"Tool registered: {name}")

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get the list of tool schemas for the AI model."""
        return self._schemas

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool by name with arguments."""
        if name not in self._tools:
            return f"❌ Error: Tool '{name}' not found."
        
        try:
            logger.info(f"Executing tool: {name} with args: {arguments}")
            return self._tools[name](**arguments)
        except Exception as e:
            logger.error(f"Tool execution error ({name}): {e}")
            return f"❌ Error executing {name}: {str(e)}"

    # --- Tool Implementations ---

    def fs_read_file(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                return f"❌ Error: File not found: {path}"
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"❌ Error reading file: {e}"

    def fs_list_dir(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                return f"❌ Error: Directory not found: {path}"
            items = os.listdir(path)
            # Add type (file/dir) to output
            output = []
            for item in items:
                full_path = os.path.join(path, item)
                type_str = "<DIR>" if os.path.isdir(full_path) else "<FILE>"
                output.append(f"{type_str} {item}")
            return "\n".join(output)
        except Exception as e:
            return f"❌ Error listing directory: {e}"

    def fs_write_file(self, path: str, content: str) -> str:
        try:
            # Basic safety check (optional: prevent writing outside project)
            # For now, we assume the AI is trusted or monitored
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ file written: {path}"
        except Exception as e:
            return f"❌ Error writing file: {e}"

    def terminal_run(self, command: str) -> str:
        try:
            # TODO: Integrate with TerminalPanel for real-time output
            # For now, use subprocess
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            output = ""
            if stdout:
                output += f"STDOUT:\n{stdout}\n"
            if stderr:
                output += f"STDERR:\n{stderr}\n"
            if not output:
                output = "(No output)"
                
            return output
        except subprocess.TimeoutExpired:
            return "❌ Error: Command timed out (30s limit)."
        except Exception as e:
            return f"❌ Error running command: {e}"
