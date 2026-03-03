"""Mover: Moves classes or functions to other files.

Uses Python's `ast` module to analyze dependencies and updates imports.
"""
import ast
import os
from typing import Optional, List, Tuple
from logger import logger

class MoveResult:
    """Result of a move-to-file operation."""
    def __init__(self):
        self.source_file_content: str = ""
        self.target_file_content: str = ""
        self.symbol_name: str = ""
        self.files_to_update: List[Tuple[str, str]] = [] # (file_path, new_content)

class Mover:
    """Handles moving code blocks across files."""
    
    def move_to_file(self, project_root: str, source_file: str, 
                     target_file: str, start_line: int, end_line: int) -> Optional[MoveResult]:
        """Move a selected block (class/func) from source_file to target_file.
        
        Args:
            project_root: Root directory of the project.
            source_file: Absolute path of the source file.
            target_file: Absolute path of the target file.
            start_line: 1-indexed start line of the selection.
            end_line: 1-indexed end line of the selection.
            
        Returns:
            MoveResult with updated file contents, or None if failed.
        """
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except OSError as e:
            logger.error(f"Cannot read source file {source_file}: {e}")
            return None
            
        lines = source_code.splitlines(keepends=True)
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
             logger.error("Invalid line range.")
             return None
             
        # Extract the exact block
        block_lines = lines[start_line - 1:end_line]
        block_code = "".join(block_lines)
        
        # Try to parse to see what symbol it is
        try:
            tree = ast.parse(block_code)
        except SyntaxError:
             logger.error("Selected block is not valid standalone Python code to move.")
             return None
             
        symbol_name = None
        for node in tree.body:
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                 symbol_name = node.name
                 break
                 
        if not symbol_name:
             logger.error("No class or function definition found in selection.")
             return None
             
        # Prepare Target file
        target_code = ""
        if os.path.exists(target_file):
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    target_code = f.read()
            except OSError:
                pass
                
        # Simple string operations for now
        # Remove from source
        for i in range(start_line - 1, end_line):
             lines[i] = ""
        new_source_code = "".join(lines)
        
        # Add to target
        new_target_code = target_code
        if new_target_code and not new_target_code.endswith('\n\n'):
             if not new_target_code.endswith('\n'):
                  new_target_code += '\n\n'
             else:
                  new_target_code += '\n'
        new_target_code += block_code
        
        result = MoveResult()
        result.source_file_content = new_source_code
        result.target_file_content = new_target_code
        result.symbol_name = symbol_name
        
        # NOTE: Updating cross-file imports is highly complex. 
        # A full AST-based project scanner is needed.
        # For this PoC implementation, we update the immediate files only
        # and rely on the user or Jedi to fix broad project imports.
        
        return result
