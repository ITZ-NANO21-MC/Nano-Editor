"""AI Assistant for code generation and analysis using Gemini API."""
import subprocess
import threading
import os
from typing import Callable, Optional
from config import config
from logger import logger


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
                    import google.generativeai as genai
                    
                    api_key = config.get('GEMINI_API_KEY')
                    if not api_key:
                        logger.error("GEMINI_API_KEY not configured")
                        callback("Error: GEMINI_API_KEY not configured\n\nCreate .env file with:\nGEMINI_API_KEY=your-api-key")
                        return
                    
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(self.model_name)
                    response = model.generate_content(prompt)
                    logger.debug(f"AI response received: {len(response.text)} chars")
                    callback(response.text)
                    return
                    
                except ImportError:
                    logger.error("google-generativeai not installed")
                    callback("Error: google-generativeai not installed\nInstall with: pip install google-generativeai")
                    return
                except Exception as e:
                    logger.error(f"AI API error: {e}")
                    callback(f"API Error: {str(e)}\n\nTry: pip install --upgrade google-generativeai")
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
    
    def complete_code(self, code: str, cursor_line: int, callback: Callable[[str], None]) -> None:
        """Generate code completion suggestions."""
        prompt = f"""Complete this code. Return ONLY the completion, no explanations:

{code}

Complete from line {cursor_line}. Provide the next 1-3 lines of code."""
        self._run_gemini_command(prompt, callback)
    
    def explain_code(self, code: str, callback: Callable[[str], None]) -> None:
        """Explain selected code."""
        prompt = f"""Explain this code concisely:

```
{code}
```

Provide a brief explanation of what it does."""
        self._run_gemini_command(prompt, callback)
    
    def generate_code(self, description: str, language: str, callback: Callable[[str], None]) -> None:
        """Generate code from description."""
        prompt = f"""Generate {language} code for: {description}

Return ONLY the code, no explanations or markdown."""
        self._run_gemini_command(prompt, callback)
    
    def refactor_code(self, code: str, callback: Callable[[str], None]) -> None:
        """Refactor and improve code."""
        prompt = f"""Refactor this code to improve readability and efficiency. Return ONLY the refactored code:

```
{code}
```"""
        self._run_gemini_command(prompt, callback)
    
    def fix_errors(self, code: str, error_msg: str, callback: Callable[[str], None]) -> None:
        """Fix code errors."""
        prompt = f"""Fix this code error. Return ONLY the corrected code:

Code:
```
{code}
```

Error: {error_msg}"""
        self._run_gemini_command(prompt, callback)
    
    def generate_docstring(self, code: str, callback: Callable[[str], None]) -> None:
        """Generate documentation for code."""
        prompt = f"""Generate a docstring for this function/class. Return ONLY the docstring:

```
{code}
```"""
        self._run_gemini_command(prompt, callback)
    
    def optimize_code(self, code: str, callback: Callable[[str], None]) -> None:
        """Suggest optimizations."""
        prompt = f"""Analyze this code and suggest optimizations:

```
{code}
```

Provide specific suggestions."""
        self._run_gemini_command(prompt, callback)
    
    def translate_code(self, code: str, from_lang: str, to_lang: str, callback: Callable[[str], None]) -> None:
        """Translate code between languages."""
        prompt = f"""Translate this {from_lang} code to {to_lang}. Return ONLY the translated code:

```
{code}
```"""
        self._run_gemini_command(prompt, callback)
