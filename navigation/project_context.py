"""
Módulo para recopilar y formatear el contexto del proyecto para la IA.

Este módulo se encarga de reunir información relevante del entorno del editor,
como la estructura de archivos y el contenido de las pestañas abiertas,
para proporcionarla como contexto a las solicitudes del asistente de IA.
"""

from tab_manager import TabManager
from ui.file_tree import VSCodeFileTree
from config import config
import os

class ProjectContext:
    """
    Recopila y formatea el contexto del proyecto para el asistente de IA.

    Esta clase implementa una estrategia de priorización para asegurar que
    la información más relevante se incluya dentro de un límite de tokens
    configurable.
    """
    def __init__(self, tab_manager: TabManager, file_tree: VSCodeFileTree, project_root: str):
        """
        Inicializa el recolector de contexto.

        Args:
            tab_manager: La instancia del gestor de pestañas para acceder a los archivos abiertos.
            file_tree: La instancia del árbol de archivos para obtener la estructura del proyecto.
            project_root: La ruta raíz del proyecto.
        """
        self.tab_manager = tab_manager
        self.file_tree = file_tree
        self.project_root = project_root
        self.max_tokens = config.get_int('AI_CONTEXT_TOKEN_LIMIT', 8000)

    def _estimate_tokens(self, text: str) -> int:
        """
        Estima el número de tokens en un texto.

        Usa la aproximación de que 1 token equivale a 4 caracteres.

        Args:
            text: El texto a medir.

        Returns:
            El número estimado de tokens.
        """
        return len(text) // 4

    def _get_project_structure(self, max_depth: int = 2) -> str:
        """
        Generates a text representation of the project structure using file system traverse.
        Ignores common ignored directories.
        """
        structure = []
        ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.env', 'dist', 'build', '.vscode', '.idea'}
        ignore_files = {'.DS_Store', 'package-lock.json', 'yarn.lock'}
        
        start_dir = self.project_root
        start_depth = start_dir.rstrip(os.sep).count(os.sep)
        
        for root, dirs, files in os.walk(start_dir):
            # Calculate current depth
            depth = root.rstrip(os.sep).count(os.sep) - start_depth
            if depth > max_depth:
                dirs[:] = [] # Stop descending
                continue
                
            # Filter ignored directories in-place
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
            
            indent = "  " * depth
            folder_name = os.path.basename(root) or os.path.basename(start_dir)
            
            if depth == 0:
                structure.append(f"{folder_name}/")
            else:
                structure.append(f"{indent}{folder_name}/")
                
            sub_indent = "  " * (depth + 1)
            for f in sorted(files):
                if f not in ignore_files and not f.startswith('.'):
                    structure.append(f"{sub_indent}{f}")
                    
        return "\n".join(structure)

    def _get_key_files_content(self, max_chars: int = 2000) -> str:
        """
        Retrieves content of key configuration files (README, requirements, package.json).
        """
        key_files = ['README.md', 'requirements.txt', 'package.json', 'pyproject.toml', 'Cargo.toml', 'go.mod']
        content_parts = []
        
        for filename in key_files:
            filepath = os.path.join(self.project_root, filename)
            if os.path.exists(filepath) and os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(max_chars)
                        if len(content) == max_chars:
                            content += "\n...(truncated)"
                        content_parts.append(f"## Key File: {filename}\n```\n{content}\n```")
                except Exception:
                    pass
                    
        return "\n".join(content_parts)

    def gather_context_for_ai(self) -> str:
        """
        Reúne y formatea el contexto del proyecto respetando el límite de tokens.
        
        Prioridad:
        1. Estructura de archivos (FS real).
        2. Archivo activo.
        3. Archivos clave (README, configs).
        4. Otros archivos abiertos.
        """
        context_parts = []
        used_tokens = 0

        # Prioridad 1: Estructura del Proyecto
        structure_str = self._get_project_structure(max_depth=3)
        structure_tokens = self._estimate_tokens(structure_str)
        if used_tokens + structure_tokens < self.max_tokens:
            context_parts.append(f"# Project Structure\n```\n{structure_str}\n```")
            used_tokens += structure_tokens

        # Prioridad 2: Archivo Activo
        current_tab = self.tab_manager.get_current_tab()
        current_file_path = current_tab.file_path if current_tab else None
        
        if current_tab and current_file_path:
            content = current_tab.content
            content_tokens = self._estimate_tokens(content)
            
            # Allow taking up to 50% of remaining tokens for current file
            limit = (self.max_tokens - used_tokens)
            if content_tokens > limit:
                char_limit = limit * 4
                content = content[:char_limit] + "\n...(truncated)"
                content_tokens = limit
                
            if content_tokens > 0:
                context_parts.append(f"\n# Active File: {os.path.basename(current_file_path)}\n```\n{content}\n```")
                used_tokens += content_tokens

        # Prioridad 3: Archivos Clave (si cabe)
        if used_tokens < self.max_tokens * 0.8: # Reserve some space
            key_files_str = self._get_key_files_content(max_chars=1000)
            key_files_tokens = self._estimate_tokens(key_files_str)
            if used_tokens + key_files_tokens < self.max_tokens:
                context_parts.append(f"\n{key_files_str}")
                used_tokens += key_files_tokens

        # Prioridad 4: Otros Archivos Abiertos
        for tab in self.tab_manager.tabs:
            if tab == current_tab or not tab.file_path:
                continue
            
            if used_tokens >= self.max_tokens:
                break

            content = tab.content
            content_tokens = self._estimate_tokens(content)
            
            if used_tokens + content_tokens > self.max_tokens:
                # Add tiny summary if full content doesn't fit? No, just skip or truncate heavily
                break 

            context_parts.append(f"## Open File: {os.path.basename(tab.file_path)}\n```\n{content}\n```")
            used_tokens += content_tokens
            
        if not context_parts:
            return ""

        return "\n".join(context_parts)
