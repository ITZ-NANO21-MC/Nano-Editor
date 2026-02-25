"""
Unit tests for the Core module (Phase 5 Migration).
Validates that all Core module imports resolve correctly after migration.
"""
import sys
import os
import unittest

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCoreModuleImports(unittest.TestCase):
    """Test that all Core module imports resolve correctly after migration."""



    def test_import_editor_view(self):
        """core.editor_view should be importable."""
        from core.editor_view import App
        self.assertTrue(callable(App))

    def test_import_text_area(self):
        """core.text_area should be importable."""
        from core.text_area import CodeEditor
        self.assertTrue(callable(CodeEditor))

    def test_import_tab_manager(self):
        """core.tab_manager should be importable."""
        from core.tab_manager import TabManager, EditorTab
        self.assertTrue(callable(TabManager))
        self.assertTrue(callable(EditorTab))

    def test_import_syntax_highlighter(self):
        """core.syntax_highlighter should be importable."""
        from core.syntax_highlighter import SyntaxHighlighter
        self.assertTrue(callable(SyntaxHighlighter))

    def test_import_async_highlighter(self):
        """core.async_highlighter should be importable."""
        from core.async_highlighter import AsyncHighlighter
        self.assertTrue(callable(AsyncHighlighter))

    def test_import_completion_popup(self):
        """core.completion_popup should be importable."""
        from core.completion_popup import CompletionPopup
        self.assertTrue(callable(CompletionPopup))

    def test_import_find_replace(self):
        """core.find_replace should be importable."""
        from core.find_replace import FindReplaceWindow
        self.assertTrue(callable(FindReplaceWindow))

    def test_import_file_handler(self):
        """core.file_handler should be importable."""
        from core.file_handler import FileHandler
        self.assertTrue(callable(FileHandler))

    def test_import_line_numbers(self):
        """core.line_numbers should be importable."""
        from core.line_numbers import LineNumbers
        self.assertTrue(callable(LineNumbers))





if __name__ == '__main__':
    unittest.main()
