"""AI-powered file operations for automatic code generation and modification."""
import os
import json
import datetime
from pathlib import Path
from typing import Callable, Optional
from ai.assistant import AIAssistant
from ai.utils import process_ai_code_output, clean_ai_json_response


class AIFileOperations:
    """Handle AI-powered file creation and modification."""
    
    def __init__(self, workspace_path: Optional[str] = None) -> None:
        self.ai: AIAssistant = AIAssistant()
        self.workspace: Path = Path(workspace_path) if workspace_path else Path.cwd()
    
    def create_file_from_description(self, description: str, filename: str, callback: Callable[[str], None]) -> None:
        """Create a new file based on description."""
        prompt = f"""Create a complete file for: {description}

Filename: {filename}
Language: {self._detect_language_from_filename(filename)}

Return ONLY the complete file content, no explanations."""
        
        def on_response(code):
            try:
                filepath = self.workspace / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(code)
                callback(f"✅ File created: {filepath}")
            except Exception as e:
                callback(f"❌ Error creating file: {e}")
        
        self.ai.generate_code(description, self._detect_language_from_filename(filename), on_response)
    
    def modify_file(self, filepath: str, instruction: str, callback: Callable[[str], None]) -> None:
        """Modify existing file based on instruction."""
        try:
            path = Path(filepath)
            if not path.exists():
                callback(f"❌ File not found: {filepath}")
                return
            
            current_content = path.read_text()
            
            prompt = f"""Modify this code according to instruction.

Current code:
```
{current_content}
```

Instruction: {instruction}

Return ONLY the complete modified code, no explanations."""
            
            def on_response(modified_code):
                try:
                    # Clean code
                    modified_code = process_ai_code_output(modified_code)
                    
                    # Backup original
                    backup_path = path.with_suffix(path.suffix + '.backup')
                    backup_path.write_text(current_content)
                    
                    # Write modified
                    path.write_text(modified_code)
                    callback(f"✅ File modified: {filepath}\n💾 Backup: {backup_path}")
                except Exception as e:
                    callback(f"❌ Error modifying file: {e}")
            
            self.ai._run_ai_completion(prompt, on_response)
            
        except Exception as e:
            callback(f"❌ Error: {e}")
    
    def add_function_to_file(self, filepath: str, function_description: str, callback: Callable[[str], None]) -> None:
        """Add a new function to existing file."""
        try:
            path = Path(filepath)
            if not path.exists():
                callback(f"❌ File not found: {filepath}")
                return
            
            current_content = path.read_text()
            language = self._detect_language_from_filename(filepath)
            
            prompt = f"""Add a new function to this {language} code.

Current code:
```
{current_content}
```

New function: {function_description}

Return the COMPLETE file with the new function added in the appropriate place."""
            
            def on_response(modified_code):
                try:
                    # Clean code
                    modified_code = process_ai_code_output(modified_code)
                    
                    backup_path = path.with_suffix(path.suffix + '.backup')
                    backup_path.write_text(current_content)
                    path.write_text(modified_code)
                    callback(f"✅ Function added to: {filepath}\n💾 Backup: {backup_path}")
                except Exception as e:
                    callback(f"❌ Error: {e}")
            
            self.ai._run_ai_completion(prompt, on_response)
            
        except Exception as e:
            callback(f"❌ Error: {e}")
    
    def create_project_structure(self, description: str, callback: Callable[[str], None]) -> None:
        """Create multiple files for a project."""
        prompt = f"""Create a project structure for: {description}

Return a JSON with this format:
{{
  "files": [
    {{"path": "main.py", "content": "# Main file\\n..."}},
    {{"path": "utils.py", "content": "# Utils\\n..."}}
  ]
}}

Return ONLY valid JSON."""
        
        # Determine folder name for the button action too
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"project_{timestamp}"
        
        self.ai._run_ai_completion(prompt, lambda resp: self.apply_project_structure_from_response(resp, lambda res, files: callback(res), folder_name=folder_name))
    
    def apply_project_structure_from_response(self, response: str, callback: Callable[[str, Optional[list]], None], folder_name: Optional[str] = None) -> None:
        """Parse AI response and create project files."""
        try:
            # Clean JSON response if wrapped in markdown
            cleaned_response = clean_ai_json_response(response)
            data = json.loads(cleaned_response)
            files = data.get('files', [])
            created = []
            
            # Base path for this project
            base_path = self.workspace
            if folder_name:
                base_path = self.workspace / folder_name
                base_path.mkdir(parents=True, exist_ok=True)
            
            for file_info in files:
                filepath = base_path / file_info['path']
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(file_info['content'])
                created.append(str(filepath))
            
            summary = f"✅ Created {len(created)} files"
            if folder_name:
                summary += f" in directory: {folder_name}"
            
            callback(f"{summary}:\n" + "\n".join(f"  - {f}" for f in created), files)
        except Exception as e:
            callback(f"❌ Error creating project: {e}", None)
    
    def _detect_language_from_filename(self, filename: str) -> str:
        """Detect programming language from filename."""
        ext_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.html': 'HTML',
            '.css': 'CSS',
            '.sh': 'Bash',
        }
        ext = Path(filename).suffix
        return ext_map.get(ext, 'Python')
