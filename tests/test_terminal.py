"""
Unit tests for the terminal module (Phase 1 Migration).
Validates that the terminal module structure, imports, and basic functionality work correctly.
"""
import sys
import os
import unittest

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTerminalModuleImports(unittest.TestCase):
    """Test that all terminal module imports resolve correctly after migration."""

    def test_import_terminal_panel(self):
        """terminal.panel.TerminalPanel should be importable."""
        from terminal.panel import TerminalPanel
        self.assertTrue(callable(TerminalPanel))

    def test_import_terminal_process(self):
        """terminal.process.TerminalProcess should be importable."""
        from terminal.process import TerminalProcess
        self.assertTrue(callable(TerminalProcess))


class TestTerminalProcessBasic(unittest.TestCase):
    """Test TerminalProcess basic functionality."""

    def test_instantiation(self):
        """TerminalProcess should instantiate with a queue."""
        import queue
        from terminal.process import TerminalProcess
        q = queue.Queue()
        tp = TerminalProcess(q)
        self.assertIsNotNone(tp)
        self.assertFalse(tp.running)

    def test_start_and_kill(self):
        """TerminalProcess should start a process and be killable."""
        import queue
        import time
        from terminal.process import TerminalProcess
        q = queue.Queue()
        tp = TerminalProcess(q)
        cwd = os.getcwd()
        shell = "/bin/bash" if os.path.exists("/bin/bash") else "/bin/sh"
        tp.start("echo hello", cwd, shell)
        time.sleep(0.5)
        tp.stop()
        time.sleep(0.3)
        self.assertFalse(tp.running)


class TestTerminalPanelImportConsistency(unittest.TestCase):
    """Test that editor_view_v3.py can still resolve TerminalPanel."""

    def test_editor_view_import_terminal(self):
        """editor_view_v3.py should be able to import TerminalPanel from new path."""
        # We can't fully import editor_view_v3 (needs tkinter), but we 
        # verify the import statement would resolve
        from terminal.panel import TerminalPanel
        self.assertEqual(TerminalPanel.__name__, 'TerminalPanel')


if __name__ == '__main__':
    unittest.main()
