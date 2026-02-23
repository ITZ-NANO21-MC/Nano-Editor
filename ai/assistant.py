import threading
from typing import Callable, Optional
from config import config
from logger import logger
from ai.utils import process_ai_code_output
from ai.client import AIClient
import ai.prompts as ai_prompts


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

    def _run_ai_stream(self, prompt: str, callback: Callable[[Optional[str]], None]) -> None:
        """Execute AI completion in background thread with streaming."""
        def target():
            model = self._get_model()
            logger.debug(f"Async AI Stream [{model}]: Starting...")
            try:
                for chunk in self.ai_client.stream_content(prompt, model):
                    callback(chunk)
                callback(None) # Signal completion
                logger.debug(f"Async AI Stream [{model}]: Completed")
            except Exception as e:
                logger.error(f"Async AI Stream [{model}] Failed: {e}")
                callback(f"\n[Error: {str(e)}]")
                callback(None)

        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def complete_code_sync(self, prompt: str) -> str:
        """Execute AI completion synchronously (blocking, for use in worker threads)."""
        model = self._get_model()
        logger.debug(f"Sync AI Request [{model}]: Starting...")
        result = self.ai_client.generate_content(prompt, model)
        logger.debug(f"Sync AI Request [{model}]: Completed")
        return result

    def complete_code(self, code: str, cursor_line: int, callback: Callable[[str], None], project_context: str = "", stream: bool = False) -> None:
        """Generate code completion suggestions."""
        prompt = ai_prompts.get_completion_prompt(code, cursor_line, project_context)
        if stream:
            self._run_ai_stream(prompt, callback)
        else:
            self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def explain_code(self, code: str, callback: Callable[[str], None], project_context: str = "", stream: bool = False) -> None:
        """Explain selected code."""
        prompt = ai_prompts.get_explanation_prompt(code, project_context)
        if stream:
            self._run_ai_stream(prompt, callback)
        else:
            self._run_ai_completion(prompt, callback)

    def generate_code(self, description: str, language: str, callback: Callable[[str], None], project_context: str = "", stream: bool = False) -> None:
        """Generate code from description."""
        prompt = ai_prompts.get_generation_prompt(description, language, project_context)
        if stream:
            self._run_ai_stream(prompt, callback)
        else:
            self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def refactor_code(self, code: str, callback: Callable[[str], None], project_context: str = "", stream: bool = False) -> None:
        """Refactor and improve code."""
        prompt = ai_prompts.get_refactoring_prompt(code, project_context)
        if stream:
            self._run_ai_stream(prompt, callback)
        else:
            self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def fix_errors(self, code: str, error_msg: str, callback: Callable[[str], None], project_context: str = "", stream: bool = False) -> None:
        """Fix code errors."""
        prompt = ai_prompts.get_fix_error_prompt(code, error_msg, project_context)
        if stream:
            self._run_ai_stream(prompt, callback)
        else:
            self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def generate_docstring(self, code: str, callback: Callable[[str], None], project_context: str = "", stream: bool = False) -> None:
        """Generate documentation for code."""
        prompt = ai_prompts.get_docstring_prompt(code, project_context)
        if stream:
            self._run_ai_stream(prompt, callback)
        else:
            self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def optimize_code(self, code: str, callback: Callable[[str], None], project_context: str = "", stream: bool = False) -> None:
        """Suggest optimizations."""
        prompt = ai_prompts.get_optimization_prompt(code, project_context)
        if stream:
            self._run_ai_stream(prompt, callback)
        else:
            self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))

    def translate_code(self, code: str, from_lang: str, to_lang: str, callback: Callable[[str], None], project_context: str = "", stream: bool = False) -> None:
        """Translate code between languages."""
        prompt = ai_prompts.get_translation_prompt(code, from_lang, to_lang, project_context)
        if stream:
            self._run_ai_stream(prompt, callback)
        else:
            self._run_ai_completion(prompt, lambda response: callback(process_ai_code_output(response)))
