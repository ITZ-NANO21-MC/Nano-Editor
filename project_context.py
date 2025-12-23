"""
Módulo para recopilar y formatear el contexto del proyecto para la IA.

Este módulo se encarga de reunir información relevante del entorno del editor,
como la estructura de archivos y el contenido de las pestañas abiertas,
para proporcionarla como contexto a las solicitudes del asistente de IA.
"""

from tab_manager import TabManager
from file_tree_vscode import VSCodeFileTree
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

    def _get_file_tree_structure(self) -> str:
        """
        Genera una representación en formato de texto del árbol de archivos.

        Returns:
            Una cadena de texto que representa la estructura de directorios y archivos.
        """
        structure = []
        
        def traverse(item_id, prefix=""):
            item_text = self.file_tree.tree.item(item_id, "text")
            structure.append(f"{prefix}- {item_text}")
            
            children = self.file_tree.tree.get_children(item_id)
            for i, child_id in enumerate(children):
                is_last = i == len(children) - 1
                new_prefix = prefix + ("    " if "└" in prefix else "│   ")
                traverse(child_id, new_prefix)

        # Iniciar el recorrido desde la raíz del Treeview
        root_items = self.file_tree.tree.get_children()
        for item_id in root_items:
            traverse(item_id)
            
        return "\n".join(structure)

    def gather_context_for_ai(self) -> str:
        """
        Reúne y formatea el contexto del proyecto respetando el límite de tokens.

        El contexto se construye siguiendo un orden de prioridad:
        1. Estructura del árbol de archivos.
        2. Contenido del archivo activo.
        3. Contenido de otras pestañas abiertas.

        Returns:
            Una cadena de texto formateada con el contexto del proyecto para la IA.
        """
        context_parts = []
        used_tokens = 0

        # Prioridad 1: Estructura de archivos
        file_tree_str = self._get_file_tree_structure()
        file_tree_tokens = self._estimate_tokens(file_tree_str)
        if used_tokens + file_tree_tokens < self.max_tokens:
            context_parts.append(f"# Estructura del Proyecto\n```\n{file_tree_str}\n```")
            used_tokens += file_tree_tokens

        # Prioridad 2: Archivo activo
        current_tab = self.tab_manager.get_current_tab()
        if current_tab and current_tab.file_path:
            content = current_tab.content
            content_tokens = self._estimate_tokens(content)
            
            # Truncar si es necesario, aunque se prioriza completo
            if used_tokens + content_tokens > self.max_tokens:
                available_chars = (self.max_tokens - used_tokens) * 4
                content = content[:available_chars]
                content_tokens = self._estimate_tokens(content)

            if content_tokens > 0:
                context_parts.append(f"\n# Archivo Activo: {os.path.basename(current_tab.file_path)}\n```\n{content}\n```")
                used_tokens += content_tokens

        # Prioridad 3: Otros archivos abiertos
        other_files_parts = []
        for tab in self.tab_manager.tabs:
            if tab == current_tab or not tab.file_path:
                continue
            
            if used_tokens >= self.max_tokens:
                break

            content = tab.content
            content_tokens = self._estimate_tokens(content)
            
            if used_tokens + content_tokens > self.max_tokens:
                available_chars = (self.max_tokens - used_tokens) * 4
                content = content[:available_chars]
                content_tokens = self._estimate_tokens(content)

            if content_tokens > 0:
                other_files_parts.append(f"## Archivo Abierto: {os.path.basename(tab.file_path)}\n```\n{content}\n```")
                used_tokens += content_tokens
        
        if other_files_parts:
            context_parts.append("\n# Otros Archivos Abiertos\n" + "\n".join(other_files_parts))
            
        if not context_parts:
            return ""

        # Ensamblar el contexto final
        header = (
            "CONTEXTO DEL PROYECTO\n"
            "=====================\n"
            "A continuación se proporciona el contexto del proyecto actual. Úsalo para "
            "dar una respuesta más precisa y relevante.\n\n"
        )
        final_context = header + "\n".join(context_parts)
        
        # Pie de página para separar del prompt del usuario
        final_context += "\n\n=====================\nFIN DEL CONTEXTO\n"
        
        return final_context
