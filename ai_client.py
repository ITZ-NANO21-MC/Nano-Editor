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

    def _handle_error(self, e: Exception, model: str) -> str:
        """Format friendly error messages from exceptions."""
        err_str = str(e)
        logger.error(f"AI Error ({model}): {err_str}")
        
        if "AuthenticationError" in str(type(e).__name__) or "401" in err_str:
            return f"🚫 Auth Error: Check your API Key for {model}."
        elif "RateLimitError" in str(type(e).__name__) or "429" in err_str:
            return f"⏳ Rate Limit: You are sending requests too fast to {model}."
        elif "NotFoundError" in str(type(e).__name__) or "404" in err_str:
            return f"❌ Model Not Found: {model} is not available."
        elif "Timeout" in str(type(e).__name__) or "timed out" in err_str.lower():
            return f"⏱️ Timeout: The request to {model} took too long (> {self.timeout}s)."
        elif "ServiceUnavailable" in str(type(e).__name__) or "503" in err_str:
            return f"🔌 Service Unavailable: {model} provider is down."
            
        return f"⚠️ Error: {err_str}"

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
            error_msg = self._handle_error(e, model)
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
            yield f"\n\n[{self._handle_error(e, model)}]"
