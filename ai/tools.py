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
            name="list_dir",
            func=self.list_dir,
            description="List contents of a directory. Returns both files and subdirectories.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the directory"}
                },
                "required": ["path"]
            }
        )
        
        self.register_tool(
            name="grep_search",
            func=self.grep_search,
            description="Search for a text pattern or regex within a directory. Useful for finding function definitions or usages.",
            parameters={
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Absolute path to search within"},
                    "query": {"type": "string", "description": "Text or regex pattern to search for"}
                },
                "required": ["directory", "query"]
            }
        )
        
        self.register_tool(
            name="replace_file_content",
            func=self.replace_file_content,
            description="Replace a specific block of text in a file with new content. The target text must exactly match the file's content.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file"},
                    "target_text": {"type": "string", "description": "Exact text block to replace. Must include exact spacing."},
                    "replacement_text": {"type": "string", "description": "New text to insert"}
                },
                "required": ["path", "target_text", "replacement_text"]
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
        """Register a new tool with its JSON schema. Replaces if already exists."""
        self._tools[name] = func
        
        # Remove existing schema with same name to avoid duplicates
        self._schemas = [s for s in self._schemas if s.get("function", {}).get("name") != name]
        
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

    def _resolve_path(self, path: str) -> str:
        """Resolve relative paths to absolute using CWD."""
        if not os.path.isabs(path):
            return os.path.abspath(path)
        return path

    def fs_read_file(self, path: str) -> str:
        try:
            path = self._resolve_path(path)
            if not os.path.exists(path):
                return f"❌ Error: File not found: {path}"
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"❌ Error reading file: {e}"

    def list_dir(self, path: str) -> str:
        try:
            path = self._resolve_path(path)
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

    def grep_search(self, directory: str, query: str) -> str:
        try:
            directory = self._resolve_path(directory)
            if not os.path.isdir(directory):
                return f"❌ Error: Not a valid directory: {directory}"
            
            # Simple python-based recursive search
            results = []
            import re
            pattern = re.compile(query)
            
            for root, _, files in os.walk(directory):
                # Ignore common hidden/binary folders
                if any(x in root for x in [".git", "__pycache__", "venv", "env", "node_modules"]):
                    continue
                    
                for file in files:
                    if file.endswith((".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".png", ".jpg")):
                        continue
                        
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for i, line in enumerate(f, 1):
                                if pattern.search(line) or query in line:
                                    rel_path = os.path.relpath(file_path, directory)
                                    results.append(f"{rel_path}:{i}:{line.strip()}")
                                    if len(results) >= 50:  # Cap at 50 to avoid flooding
                                        results.append("... (more results truncated) ...")
                                        return "\n".join(results)
                    except UnicodeDecodeError:
                        pass # binary file
                    except Exception:
                        pass
                        
            if not results:
                return "No matches found."
            return "\n".join(results)
        except Exception as e:
            return f"❌ Error performing search: {e}"

    def replace_file_content(self, path: str, target_text: str, replacement_text: str) -> str:
        try:
            path = self._resolve_path(path)
            if not os.path.exists(path):
                return f"❌ Error: File not found: {path}"
                
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if target_text not in content:
                # Try handling newline differences (CRLF vs LF)
                normalized_content = content.replace('\\r\\n', '\\n')
                normalized_target = target_text.replace('\\r\\n', '\\n')
                
                if normalized_target not in normalized_content:
                    return "❌ Error: target_text exactly as provided was not found in the file. Ensure exact spacing and indentation."
                else:
                    target_text = normalized_target
                    content = normalized_content
                    
            if content.count(target_text) > 1:
                 return "❌ Error: target_text appears multiple times. Provide more context to make it unique."
                
            new_content = content.replace(target_text, replacement_text)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return f"✅ Block replaced successfully in {path}"
        except Exception as e:
            return f"❌ Error replacing content: {e}"

    def fs_write_file(self, path: str, content: str) -> str:
        try:
            path = self._resolve_path(path)
            parent_dir = os.path.dirname(path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
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
