import threading
from typing import Callable, Optional
from config import config
from logger import logger
from ai_utils import process_ai_code_output
from ai_client import AIClient


class AIAssistant:
    """Handles AI-powered code assistance features using unified AIClient."""

    def __init__(self) -> None:
        self.timeout: int = config.get_int('AI_TIMEOUT', 60)
        self.ai_client = AIClient()
    def _get_model(self) -> str:
        """Get currently configured AI model."""
        return config.get('AI_MODEL', 'gemini/gemini-2.0-flash')

    def _run_ai_completion(self, prompt: str, callback: Callable[[str], None]) -> None:
        """Execute AI completion in background thread using LiteLLM client."""
        def target():
            model = self._get_model()
            logger.debug(f"Async AI Request [{model}]: Starting...")
            try:
                self.ai_client.generate_content(prompt, model, callback)
                logger.debug(f"Async AI Request [{model}]: Completed")
            except Exception as e:
                logger.error(f"Async AI Request [{model}] Failed: {e}")
                callback(f"Error: {str(e)}")

        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def complete_code_sync(self, prompt: str) -> str:
        """Execute AI completion synchronously (blocking, for use in worker threads)."""
        model = self._get_model()
        logger.debug(f"Sync AI Request [{model}]: Starting...")
        result = self.ai_client.generate_content(prompt, model)
        logger.debug(f"Sync AI Request [{model}]: Completed")
        return result

    def complete_code(self, code: str, cursor_line: int, callback: Callable[[str], None], project_context: str = "") -> None:
        """Generate code completion suggestions."""
        prompt = f"""{project_context}

Complete this code. Return ONLY the completion, no explanations:

{code}

Complete from line {cursor_line}. Provide the next 1-3 lines of code."""
        self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def explain_code(self, code: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Explain selected code."""
        prompt = f"""{project_context}

Explain this code concisely:

```
{code}
```

Provide a brief explanation of what it does."""
        self._run_ai_completion(prompt, callback)

    def generate_code(self, description: str, language: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Generate code from description."""
        prompt = f"""{project_context}

Generate {language} code for: {description}

Return ONLY the code, no explanations or markdown."""
        self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def refactor_code(self, code: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Refactor and improve code."""
        prompt = f"""{project_context}

Refactor this code to improve readability and efficiency. Return ONLY the refactored code:

```
{code}
```"""
        self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def fix_errors(self, code: str, error_msg: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Fix code errors."""
        prompt = f"""{project_context}

Fix this code error. Return ONLY the corrected code:

Code:
```
{code}
```

Error: {error_msg}"""
        self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def generate_docstring(self, code: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Generate documentation for code."""
        prompt = f"""{project_context}

Generate a docstring for this function/class. Return ONLY the docstring:

```
{code}
```"""
        self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def optimize_code(self, code: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Suggest optimizations."""
        prompt = f"""{project_context}

Analyze this code and suggest optimizations:

```
{code}
```

Provide specific suggestions."""
        self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def translate_code(self, code: str, from_lang: str, to_lang: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Translate code between languages."""
        prompt = f"""{project_context}

Translate this {from_lang} code to {to_lang}. Return ONLY the translated code:

```
{code}
```"""
        self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))
