"""Gemini client refactored to use unified AIClient via LiteLLM."""
import threading
from typing import Callable, Optional
from config import config
from ai_client import AIClient


class GeminiClient:
    """Wrapper that maintains the legacy GeminiClient interface but uses AIClient."""
    
    def __init__(self) -> None:
        self.ai_client = AIClient()
        self.timeout: int = config.get_int('AI_TIMEOUT', 60)

    def run_gemini(self, query: str, callback: Callable[[str], None]) -> None:
        """Maintains legacy method name for compatibility."""
        model_to_use = config.get('AI_MODEL', 'gemini/gemini-2.0-flash')
        threading.Thread(
            target=lambda: self.ai_client.generate_content(query, model_to_use, callback),
            daemon=True
        ).start()

    def run_gemini_stream(self, query: str):
        """Maintains legacy method name for compatibility."""
        model_to_use = config.get('AI_MODEL', 'gemini/gemini-2.0-flash')
        return self.ai_client.stream_content(query, model_to_use)
