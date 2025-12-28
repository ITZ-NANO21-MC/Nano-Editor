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

                from google import genai
                
                api_key = config.get('GEMINI_API_KEY')
                if not api_key:
                    callback("Error: GEMINI_API_KEY not configured\n\nCreate .env file with:\nGEMINI_API_KEY=your-api-key")
                    return
                
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=query
                )
                if response.text:
                    callback(response.text)
                else:
                    callback("")
                
            except ImportError:
                callback("Error: google-genai not installed\n\nInstall with:\n./env/bin/pip install google-genai")
            except Exception as e:
                callback(f"Error: {str(e)}\n\nVerify your API key is correct")

        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def run_gemini_stream(self, query: str):
        """Runs Gemini API with streaming and yields response chunks."""
        try:

            from google import genai
            
            api_key = config.get('GEMINI_API_KEY')
            if not api_key:
                yield "Error: GEMINI_API_KEY not configured. Create a .env file with your key."
                return
            
            client = genai.Client(api_key=api_key)
            response_stream = client.models.generate_content_stream(
                model=self.model_name,
                contents=query
            )
            
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        
        except ImportError:
            yield "Error: google-genai not installed. Run: pip install google-genai"
        except Exception as e:
            yield f"Error: {str(e)}"
