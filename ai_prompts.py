"""
Centralized storage for AI prompts.
This allows for easier management, versioning, and potential localization of prompts.
"""

def get_completion_prompt(code: str, cursor_line: int, project_context: str = "") -> str:
    return f"""{project_context}

Complete this code. Return ONLY the completion, no explanations:

{code}

Complete from line {cursor_line}. Provide the next 1-3 lines of code."""

def get_explanation_prompt(code: str, project_context: str = "") -> str:
    return f"""{project_context}

Explain this code concisely:

```
{code}
```

Provide a brief explanation of what it does."""

def get_generation_prompt(description: str, language: str, project_context: str = "") -> str:
    return f"""{project_context}

Generate {language} code for: {description}

Return ONLY the code, no explanations or markdown."""

def get_refactoring_prompt(code: str, project_context: str = "") -> str:
    return f"""{project_context}

Refactor this code to improve readability and efficiency. Return ONLY the refactored code:

```
{code}
```"""

def get_fix_error_prompt(code: str, error_msg: str, project_context: str = "") -> str:
    return f"""{project_context}

Fix this code error. Return ONLY the corrected code:

Code:
```
{code}
```

Error: {error_msg}"""

def get_docstring_prompt(code: str, project_context: str = "") -> str:
    return f"""{project_context}

Generate a docstring for this function/class. Return ONLY the docstring:

```
{code}
```"""

def get_optimization_prompt(code: str, project_context: str = "") -> str:
    return f"""{project_context}

Analyze this code and suggest optimizations:

```
{code}
```

Provide specific suggestions."""

def get_translation_prompt(code: str, from_lang: str, to_lang: str, project_context: str = "") -> str:
    return f"""{project_context}

Translate this {from_lang} code to {to_lang}. Return ONLY the translated code:

```
{code}
```"""
