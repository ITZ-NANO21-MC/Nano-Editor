"""
Centralized storage for AI prompts.
This allows for easier management, versioning, and potential localization of prompts.
"""

# Common strict instructions to append to all prompts
STRICT_INSTRUCTIONS = """
IMPORTANT OUTPUT RULES:
1. Return ONLY the requested content (code or text).
2. DO NOT usage Markdown code blocks (```).
3. DO NOT return JSON.
4. DO NOT add conversational text like "Here is the code".
5. Start your response directly with the content.
"""

def get_completion_prompt(code: str, cursor_line: int, project_context: str = "") -> str:
    return f"""{project_context}

Complete this code.
{code}

Complete from line {cursor_line}. Provide the next 1-3 lines of code.

{STRICT_INSTRUCTIONS}"""

def get_explanation_prompt(code: str, project_context: str = "") -> str:
    return f"""{project_context}

Explain this code concisely in plain text.

Code:
{code}

{STRICT_INSTRUCTIONS}
Exclude rule 2 (you can use inline code styles if needed, but no blocks)."""

def get_generation_prompt(description: str, language: str, project_context: str = "") -> str:
    return f"""{project_context}

Generate {language} code for: {description}

{STRICT_INSTRUCTIONS}"""

def get_refactoring_prompt(code: str, project_context: str = "") -> str:
    return f"""{project_context}

Refactor this code to improve readability and efficiency.

Code:
{code}

{STRICT_INSTRUCTIONS}"""

def get_fix_error_prompt(code: str, error_msg: str, project_context: str = "") -> str:
    return f"""{project_context}

Fix this code error.

Code:
{code}

Error: {error_msg}

{STRICT_INSTRUCTIONS}"""

def get_docstring_prompt(code: str, project_context: str = "") -> str:
    return f"""{project_context}

Generate a docstring for this function/class.

Code:
{code}

{STRICT_INSTRUCTIONS}"""

def get_optimization_prompt(code: str, project_context: str = "") -> str:
    return f"""{project_context}

Analyze this code and suggest optimizations in plain text.

Code:
{code}

{STRICT_INSTRUCTIONS}
Exclude rule 2 (you can use inline code styles). Use bullet points."""

def get_translation_prompt(code: str, from_lang: str, to_lang: str, project_context: str = "") -> str:
    return f"""{project_context}

Translate this {from_lang} code to {to_lang}.

Code:
{code}

{STRICT_INSTRUCTIONS}"""
