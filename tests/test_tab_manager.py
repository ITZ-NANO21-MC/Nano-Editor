"""Tests for tab manager."""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestEditorTab(unittest.TestCase):
    """Test EditorTab class."""
    
    def test_tab_creation(self):
        """Test creating a tab."""
        from tab_manager import EditorTab
        
        tab = EditorTab()
        self.assertIsNone(tab.file_path)
        self.assertEqual(tab.content, "")
        self.assertFalse(tab.modified)
    
    def test_tab_with_file(self):
        """Test creating tab with file path."""
        from tab_manager import EditorTab
        
        tab = EditorTab("/path/to/file.py")
        self.assertEqual(tab.file_path, "/path/to/file.py")
    
    def test_tab_title_untitled(self):
        """Test untitled tab title."""
        from tab_manager import EditorTab
        
        tab = EditorTab()
        self.assertEqual(tab.get_title(), "Untitled")
    
    def test_tab_title_modified(self):
        """Test modified tab title."""
        from tab_manager import EditorTab
        
        tab = EditorTab()
        tab.modified = True
        self.assertEqual(tab.get_title(), "Untitled*")
    
    def test_tab_title_with_file(self):
        """Test tab title with file."""
        from tab_manager import EditorTab
        
        tab = EditorTab("/path/to/test.py")
        self.assertEqual(tab.get_title(), "test.py")
    
    def test_tab_title_with_file_modified(self):
        """Test modified tab title with file."""
        from tab_manager import EditorTab
        
        tab = EditorTab("/path/to/test.py")
        tab.modified = True
        self.assertEqual(tab.get_title(), "*test.py")


if __name__ == "__main__":
    unittest.main()
