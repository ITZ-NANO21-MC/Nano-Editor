import litellm
from typing import Callable, Optional, Generator
from config import config
from logger import logger

class AIClient:
    """Unified AI client using LiteLLM to support multiple providers."""
    
    def __init__(self) -> None:
        self.timeout: int = config.get_int('AI_TIMEOUT', 60)
        # Drop unsupported params for some providers
        litellm.drop_params = True

    def _get_api_key(self, model: str) -> Optional[str]:
        """Determine API key based on model provider."""
        if model.startswith("gemini/"):
            return config.get('GEMINI_API_KEY')
        elif model.startswith("openai/"):
            return config.get('OPENAI_API_KEY')
        elif model.startswith("claude/") or model.startswith("anthropic/"):
            return config.get('ANTHROPIC_API_KEY')
        elif model.startswith("deepseek/"):
            return config.get('DEEPSEEK_API_KEY')
        # Add more providers as needed
        return None

    def generate_content(self, prompt: str, model: str, callback: Optional[Callable[[str], None]] = None) -> str:
        """Generate content from prompt using LiteLLM."""
        api_key = self._get_api_key(model)
        
        try:
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                api_key=api_key,
                timeout=self.timeout
            )
            
            result = response.choices[0].message.content or ""
            if callback:
                callback(result)
            return result

        except Exception as e:
            error_msg = f"AI Error ({model}): {str(e)}"
            logger.error(error_msg)
            if callback:
                callback(error_msg)
            return error_msg

    def stream_content(self, prompt: str, model: str) -> Generator[str, None, None]:
        """Stream content from prompt using LiteLLM."""
        api_key = self._get_api_key(model)
        
        try:
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                api_key=api_key,
                stream=True,
                timeout=self.timeout
            )
            
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except Exception as e:
            yield f"\n[Stream Error: {str(e)}]"
