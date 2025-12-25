"""Tests for Gemini client."""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gemini_client import GeminiClient

class TestGeminiClient(unittest.TestCase):
    """Test Gemini client initialization."""
    
    def test_client_creation(self):
        """Test creating Gemini client."""
        client = GeminiClient()
        self.assertIsNotNone(client)
    
    def test_client_has_run_methods(self):
        """Test client has the run_gemini and run_gemini_stream methods."""
        client = GeminiClient()
        self.assertTrue(hasattr(client, 'run_gemini'))
        self.assertTrue(hasattr(client, 'run_gemini_stream'))

class TestGeminiClientStreaming(unittest.TestCase):
    """Test the streaming functionality of the Gemini client using mocks."""

    def setUp(self):
        """Create a fake 'google.generativeai' module in sys.modules."""
        self.mock_genai_module = MagicMock()
        sys.modules['google.generativeai'] = self.mock_genai_module
        sys.modules['google'] = MagicMock(generativeai=self.mock_genai_module)

    def tearDown(self):
        """Remove the fake module after tests."""
        del sys.modules['google.generativeai']
        del sys.modules['google']

    @patch('gemini_client.config')
    def test_streaming_success(self, mock_config):
        """Test a successful streaming response."""
        mock_config.get.return_value = 'fake_api_key'
        
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Hello "
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "World"
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = [mock_chunk1, mock_chunk2]
        self.mock_genai_module.GenerativeModel.return_value = mock_model

        client = GeminiClient()
        query = "say hello"
        response_generator = client.run_gemini_stream(query)
        result = "".join(list(response_generator))

        self.assertEqual(result, "Hello World")
        mock_model.generate_content.assert_called_once_with(query, stream=True)

    @patch('gemini_client.config')
    def test_streaming_api_error(self, mock_config):
        """Test an API error during streaming."""
        mock_config.get.return_value = 'fake_api_key'
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Failure")
        self.mock_genai_module.GenerativeModel.return_value = mock_model

        client = GeminiClient()
        query = "test"
        response_generator = client.run_gemini_stream(query)
        result = next(response_generator)

        self.assertIn("Error: API Failure", result)

    @patch('gemini_client.config')
    def test_streaming_no_api_key(self, mock_config):
        """Test that an error is yielded if the API key is missing."""
        mock_config.get.return_value = None

        client = GeminiClient()
        query = "test"
        response_generator = client.run_gemini_stream(query)
        result = next(response_generator)
        
        self.assertIn("Error: GEMINI_API_KEY not configured", result)

if __name__ == "__main__":
    unittest.main()
