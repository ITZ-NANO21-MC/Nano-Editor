"""Core module - Editor core components for NanoEditor."""
from core.editor_view import App
from core.text_area import CodeEditor
from core.tab_manager import TabManager, EditorTab
from core.syntax_highlighter import SyntaxHighlighter

__all__ = ['App', 'CodeEditor', 'TabManager', 'EditorTab', 'SyntaxHighlighter']
