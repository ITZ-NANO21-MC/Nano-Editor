"""
Unit tests for the navigation module (Phase 2 Migration).
Validates that the navigation module structure, imports, and basic functionality work correctly.
"""
import sys
import os
import unittest

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNavigationModuleImports(unittest.TestCase):
    """Test that all navigation module imports resolve correctly after migration."""

    def test_import_navigation_package(self):
        """The navigation package itself should be importable."""
        import navigation
        self.assertTrue(hasattr(navigation, 'GotoDefinition'))
        self.assertTrue(hasattr(navigation, 'setup_goto_definition_bindings'))
        self.assertTrue(hasattr(navigation, 'ProjectContext'))
        self.assertTrue(hasattr(navigation, 'ProjectSearchWindow'))

    def test_import_goto_definition(self):
        """navigation.goto_definition should be importable."""
        from navigation.goto_definition import GotoDefinition, setup_goto_definition_bindings
        self.assertTrue(callable(GotoDefinition))
        self.assertTrue(callable(setup_goto_definition_bindings))

    def test_import_project_context(self):
        """navigation.project_context.ProjectContext should be importable."""
        from navigation.project_context import ProjectContext
        self.assertTrue(callable(ProjectContext))

    def test_import_project_search(self):
        """navigation.project_search.ProjectSearchWindow should be importable."""
        from navigation.project_search import ProjectSearchWindow
        self.assertTrue(callable(ProjectSearchWindow))

    def test_reexport_from_init(self):
        """Re-exports in navigation/__init__.py should work."""
        from navigation import GotoDefinition, ProjectContext, ProjectSearchWindow
        self.assertIsNotNone(GotoDefinition)
        self.assertIsNotNone(ProjectContext)
        self.assertIsNotNone(ProjectSearchWindow)


class TestProjectContextBasic(unittest.TestCase):
    """Test ProjectContext basic functionality."""

    def test_class_has_expected_methods(self):
        """ProjectContext should have key methods."""
        from navigation.project_context import ProjectContext
        self.assertTrue(hasattr(ProjectContext, 'gather_context_for_ai'))


class TestGotoDefinitionBasic(unittest.TestCase):
    """Test GotoDefinition basic functionality."""

    def test_class_has_expected_methods(self):
        """GotoDefinition should have expected methods."""
        from navigation.goto_definition import GotoDefinition
        self.assertTrue(hasattr(GotoDefinition, 'goto_definition'))
        self.assertTrue(hasattr(GotoDefinition, 'jump_to_line'))
        self.assertTrue(hasattr(GotoDefinition, 'find_symbol_references'))


if __name__ == '__main__':
    unittest.main()
