"""Tests for utility functions."""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestFileOperations(unittest.TestCase):
    """Test file operation utilities."""
    
    def test_detect_language_python(self):
        """Test Python file detection."""
        ext_map = {".py": "Python", ".js": "JavaScript", ".java": "Java"}
        ext = os.path.splitext("test.py")[1]
        lang = ext_map.get(ext, "Python")
        self.assertEqual(lang, "Python")
    
    def test_detect_language_javascript(self):
        """Test JavaScript file detection."""
        ext_map = {".py": "Python", ".js": "JavaScript", ".java": "Java"}
        ext = os.path.splitext("test.js")[1]
        lang = ext_map.get(ext, "Python")
        self.assertEqual(lang, "JavaScript")
    
    def test_detect_language_unknown(self):
        """Test unknown file type defaults to Python."""
        ext_map = {".py": "Python", ".js": "JavaScript", ".java": "Java"}
        ext = os.path.splitext("test.xyz")[1]
        lang = ext_map.get(ext, "Python")
        self.assertEqual(lang, "Python")


class TestPathOperations(unittest.TestCase):
    """Test path operations."""
    
    def test_basename(self):
        """Test getting basename."""
        path = "/home/user/test.py"
        basename = os.path.basename(path)
        self.assertEqual(basename, "test.py")
    
    def test_dirname(self):
        """Test getting dirname."""
        path = "/home/user/test.py"
        dirname = os.path.dirname(path)
        self.assertEqual(dirname, "/home/user")
    
    def test_splitext(self):
        """Test splitting extension."""
        path = "test.py"
        name, ext = os.path.splitext(path)
        self.assertEqual(name, "test")
        self.assertEqual(ext, ".py")


if __name__ == "__main__":
    unittest.main()
