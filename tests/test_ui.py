"""
Unit tests for the UI module (Phase 4 Migration).
Validates that all UI module imports resolve correctly after migration.
"""
import sys
import os
import unittest

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUIModuleImports(unittest.TestCase):
    """Test that all UI module imports resolve correctly after migration."""


    def test_import_sidebar(self):
        """ui.sidebar should be importable."""
        from ui.sidebar import VSCodeSidebar
        self.assertTrue(callable(VSCodeSidebar))

    def test_import_file_tree(self):
        """ui.file_tree should be importable."""
        from ui.file_tree import VSCodeFileTree, VSCodeSections
        self.assertTrue(callable(VSCodeFileTree))
        self.assertIsNotNone(VSCodeSections)

    def test_import_ai_panel(self):
        """ui.ai_panel should be importable."""
        from ui.ai_panel import AIAssistantPanel
        self.assertTrue(callable(AIAssistantPanel))

    def test_import_gemini_panel(self):
        """ui.gemini_panel should be importable."""
        from ui.gemini_panel import GeminiPanel
        self.assertTrue(callable(GeminiPanel))

    def test_import_gemini_client(self):
        """ui.gemini_client should be importable."""
        from ui.gemini_client import GeminiClient
        self.assertTrue(callable(GeminiClient))

    def test_import_agent_panel(self):
        """ui.agent_panel should be importable."""
        from ui.agent_panel import AgentPanel
        self.assertTrue(callable(AgentPanel))

    def test_import_menu_bar(self):
        """ui.menu_bar should be importable."""
        from ui.menu_bar import ModernMenuBar
        self.assertTrue(callable(ModernMenuBar))

    def test_import_status_bar(self):
        """ui.status_bar should be importable."""
        from ui.status_bar import StatusBar
        self.assertTrue(callable(StatusBar))

    def test_import_visual_feedback(self):
        """ui.visual_feedback should be importable."""
        from ui.visual_feedback import VisualFeedback
        self.assertTrue(callable(VisualFeedback))

    def test_import_about_window(self):
        """ui.about_window should be importable."""
        from ui.about_window import AboutWindow
        self.assertTrue(callable(AboutWindow))

    def test_import_shortcuts_window(self):
        """ui.shortcuts_window should be importable."""
        from ui.shortcuts_window import ShortcutsWindow
        self.assertTrue(callable(ShortcutsWindow))

    def test_import_references_window(self):
        """ui.references_window should be importable."""
        from ui.references_window import ReferencesWindow
        self.assertTrue(callable(ReferencesWindow))

    def test_import_ai_menu(self):
        """ui.ai_menu should be importable."""
        from ui.ai_menu import AIActionDialog, AIResultDialog
        self.assertTrue(callable(AIActionDialog))
        self.assertTrue(callable(AIResultDialog))

    def test_import_ai_completion_popup(self):
        """ui.ai_completion_popup should be importable."""
        from ui.ai_completion_popup import AICompletionPopup
        self.assertTrue(callable(AICompletionPopup))



if __name__ == '__main__':
    unittest.main()
