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
    """Test the streaming functionality of the Gemini client using LiteLLM mocks."""

    @patch('ai.client.config')
    @patch('ai.client.litellm.completion')
    def test_streaming_success(self, mock_completion, mock_config):
        """Test a successful streaming response."""
        mock_config.get.side_effect = lambda k, d=None: "fake_key" if k == "GEMINI_API_KEY" else ("gemini/gemini-2.0-flash" if k == "AI_MODEL" else d)
        
        mock_chunk1 = MagicMock()
        mock_chunk1.choices[0].delta.content = "Hello "
        mock_chunk2 = MagicMock()
        mock_chunk2.choices[0].delta.content = "World"
        
        mock_completion.return_value = [mock_chunk1, mock_chunk2]

        client = GeminiClient()
        query = "say hello"
        response_generator = client.run_gemini_stream(query)
        result = "".join(list(response_generator))

        self.assertEqual(result, "Hello World")
        mock_completion.assert_called_once()

    @patch('ai.client.config')
    @patch('ai.client.litellm.completion')
    def test_streaming_api_error(self, mock_completion, mock_config):
        """Test an API error during streaming."""
        mock_config.get.side_effect = lambda k, d=None: "fake_key" if k == "GEMINI_API_KEY" else ("gemini/gemini-2.0-flash" if k == "AI_MODEL" else d)
        
        mock_completion.side_effect = Exception("API Failure")

        client = GeminiClient()
        query = "test"
        response_generator = client.run_gemini_stream(query)
        result = next(response_generator)

        self.assertIn("API Failure", result)

    @patch('ai.client.config')
    @patch('ai.client.litellm.completion')
    def test_streaming_no_api_key(self, mock_completion, mock_config):
        """Test that an error is yielded if the API key is missing."""
        mock_config.get.side_effect = lambda k, d=None: None if k == "GEMINI_API_KEY" else ("gemini/gemini-2.0-flash" if k == "AI_MODEL" else d)
        mock_completion.side_effect = Exception("AuthenticationError: Missing API Key")

        client = GeminiClient()
        query = "test"
        response_generator = client.run_gemini_stream(query)
        result = next(response_generator)
        self.assertIn("AuthenticationError", result)

if __name__ == "__main__":
    unittest.main()
