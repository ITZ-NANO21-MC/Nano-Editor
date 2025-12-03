"""Gemini client using Python API instead of CLI."""
import threading
from typing import Callable, Optional
from config import config


class GeminiClient:
    def __init__(self) -> None:
        self.process: Optional[object] = None
        self.timeout: int = config.get_int('AI_TIMEOUT', 60)
        self.model_name: str = config.get('AI_MODEL', 'models/gemini-2.5-flash')

    def run_gemini(self, query: str, callback: Callable[[str], None]) -> None:
        def target() -> None:
            try:
                import google.generativeai as genai
                
                api_key = config.get('GEMINI_API_KEY')
                if not api_key:
                    callback("Error: GEMINI_API_KEY not configured\n\nCreate .env file with:\nGEMINI_API_KEY=your-api-key")
                    return
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(query)
                callback(response.text)
                
            except ImportError:
                callback("Error: google-generativeai not installed\n\nInstall with:\n./env/bin/pip install google-generativeai")
            except Exception as e:
                callback(f"Error: {str(e)}\n\nVerify your API key is correct")

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
