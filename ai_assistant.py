"""AI Assistant for code generation and analysis using Gemini API."""
import subprocess
import threading
import os
from typing import Callable, Optional
from config import config
from logger import logger
from ai_utils import process_ai_code_output


class AIAssistant:
    """Handles AI-powered code assistance features."""

    def __init__(self) -> None:
        self.timeout: int = config.get_int('AI_TIMEOUT', 60)
        self.current_process: Optional[subprocess.Popen] = None
        self.use_api: bool = True
        self.model_name: str = config.get('AI_MODEL', 'models/gemini-2.5-flash')

    def _run_gemini_command(self, prompt: str, callback: Callable[[str], None]) -> None:
        """Execute Gemini command in background thread."""
        def target():
            # Try Python API first
            if self.use_api:
                try:
                    from google import genai
                    from google.genai import types

                    api_key = config.get('GEMINI_API_KEY')
                    if not api_key:
                        logger.error("GEMINI_API_KEY not configured")
                        callback("Error: GEMINI_API_KEY not configured\n\nCreate .env file with:\nGEMINI_API_KEY=your-api-key")
                        return

                    client = genai.Client(api_key=api_key)
                    model_to_use = config.get('AI_MODEL', 'models/gemini-2.0-flash')
                    response = client.models.generate_content(
                        model=model_to_use,
                        contents=prompt
                    )
                    
                    if response.text:
                        logger.debug(f"AI response received: {len(response.text)} chars")
                        callback(response.text)
                    else:
                        callback("")
                    return

                except ImportError:
                    logger.error("google-genai not installed")
                    callback("Error: google-genai not installed\nInstall with: pip install google-genai")
                    return
                except Exception as e:
                    logger.error(f"AI API error: {e}")
                    callback(f"API Error: {str(e)}\n\nTry: pip install google-genai")
                    return

            # Fallback to CLI (deprecated)
            try:
                process = subprocess.Popen(
                    ['gemini', 'ask', prompt],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                try:
                    stdout, stderr = process.communicate(timeout=self.timeout)
                    if process.returncode == 0:
                        callback(stdout.strip())
                    else:
                        callback(f"CLI Error: {stderr}")
                except subprocess.TimeoutExpired:
                    process.kill()
                    callback("Error: Request timed out")
            except FileNotFoundError:
                callback("Error: Gemini CLI not found")
            except Exception as e:
                callback(f"Error: {e}")

        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def complete_code(self, code: str, cursor_line: int, callback: Callable[[str], None], project_context: str = "") -> None:
        """Generate code completion suggestions."""
        prompt = f"""{project_context}

Complete this code. Return ONLY the completion, no explanations:

{code}

Complete from line {cursor_line}. Provide the next 1-3 lines of code."""
        self._run_gemini_command(prompt, lambda response: callback(process_ai_code_output(response)))

    def explain_code(self, code: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Explain selected code."""
        prompt = f"""{project_context}

Explain this code concisely:

```
{code}
```

Provide a brief explanation of what it does."""
        self._run_gemini_command(prompt, callback)

    def generate_code(self, description: str, language: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Generate code from description."""
        prompt = f"""{project_context}

Generate {language} code for: {description}

Return ONLY the code, no explanations or markdown."""
        self._run_gemini_command(prompt, lambda response: callback(process_ai_code_output(response)))

    def refactor_code(self, code: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Refactor and improve code."""
        prompt = f"""{project_context}

Refactor this code to improve readability and efficiency. Return ONLY the refactored code:

```
{code}
```"""
        self._run_gemini_command(prompt, lambda response: callback(process_ai_code_output(response)))

    def fix_errors(self, code: str, error_msg: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Fix code errors."""
        prompt = f"""{project_context}

Fix this code error. Return ONLY the corrected code:

Code:
```
{code}
```

Error: {error_msg}"""
        self._run_gemini_command(prompt, lambda response: callback(process_ai_code_output(response)))

    def generate_docstring(self, code: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Generate documentation for code."""
        prompt = f"""{project_context}

Generate a docstring for this function/class. Return ONLY the docstring:

```
{code}
```"""
        self._run_gemini_command(prompt, lambda response: callback(process_ai_code_output(response)))

    def optimize_code(self, code: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Suggest optimizations."""
        prompt = f"""{project_context}

Analyze this code and suggest optimizations:

```
{code}
```

Provide specific suggestions."""
        self._run_gemini_command(prompt, lambda response: callback(process_ai_code_output(response)))

    def translate_code(self, code: str, from_lang: str, to_lang: str, callback: Callable[[str], None], project_context: str = "") -> None:
        """Translate code between languages."""
        prompt = f"""{project_context}

Translate this {from_lang} code to {to_lang}. Return ONLY the translated code:

```
{code}
```"""
        self._run_gemini_command(prompt, lambda response: callback(process_ai_code_output(response)))
