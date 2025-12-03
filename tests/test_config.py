"""Tests for config module."""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config


class TestConfig(unittest.TestCase):
    """Test configuration loading."""
    
    def test_config_get_default(self):
        """Test getting config with default value."""
        config = Config()
        value = config.get("NONEXISTENT_KEY", "default_value")
        self.assertEqual(value, "default_value")
    
    def test_config_get_int(self):
        """Test getting integer config."""
        config = Config()
        value = config.get_int("EDITOR_FONT_SIZE", 14)
        self.assertIsInstance(value, int)
        self.assertGreaterEqual(value, 10)
    
    def test_config_get_bool(self):
        """Test getting boolean config."""
        config = Config()
        value = config.get_bool("AUTOCOMPLETE_ENABLED", True)
        self.assertIsInstance(value, bool)


if __name__ == "__main__":
    unittest.main()
