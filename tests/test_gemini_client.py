"""Tests for Gemini client."""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestGeminiClient(unittest.TestCase):
    """Test Gemini client initialization."""
    
    def test_client_creation(self):
        """Test creating Gemini client."""
        from gemini_client import GeminiClient
        
        client = GeminiClient()
        self.assertIsNotNone(client)
    
    def test_client_has_generate_method(self):
        """Test client has generate_content method."""
        from gemini_client import GeminiClient
        
        client = GeminiClient()
        self.assertTrue(hasattr(client, 'generate_content'))


if __name__ == "__main__":
    unittest.main()
