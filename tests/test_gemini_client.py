"""Tests for Gemini client."""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ui.gemini_client import GeminiClient

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
        """Create a fake 'google.genai' module in sys.modules."""
        self.mock_genai_module = MagicMock()
        self.mock_genai_module.types = MagicMock()
        sys.modules['google.genai'] = self.mock_genai_module
        sys.modules['google'] = MagicMock(genai=self.mock_genai_module)

    def tearDown(self):
        """Remove the fake module after tests."""
        del sys.modules['google.genai']
        del sys.modules['google']

    @patch('gemini_client.config')
    def test_streaming_success(self, mock_config):
        """Test a successful streaming response."""
        mock_config.get.return_value = 'fake_api_key'
        
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Hello "
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "World"
        
        # Mock Client().models.generate_content_stream
        mock_client = MagicMock()
        mock_client.models.generate_content_stream.return_value = [mock_chunk1, mock_chunk2]
        self.mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        query = "say hello"
        response_generator = client.run_gemini_stream(query)
        result = "".join(list(response_generator))

        self.assertEqual(result, "Hello World")
        self.mock_genai_module.Client.assert_called_with(api_key='fake_api_key')
        mock_client.models.generate_content_stream.assert_called_once()

    @patch('gemini_client.config')
    def test_streaming_api_error(self, mock_config):
        """Test an API error during streaming."""
        mock_config.get.return_value = 'fake_api_key'
        
        mock_client = MagicMock()
        mock_client.models.generate_content_stream.side_effect = Exception("API Failure")
        self.mock_genai_module.Client.return_value = mock_client

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
