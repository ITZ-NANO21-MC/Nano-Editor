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

Optimize this code. Return the COMPLETE optimized version of the code.
Add short comments (using the language's comment syntax) next to each change explaining WHY it was optimized.
Do NOT return suggestions or explanations as separate text.
Do NOT use Markdown formatting (no **, no `, no ###).
Return ONLY the optimized code with inline comments.

Code:
{code}

{STRICT_INSTRUCTIONS}"""

def get_translation_prompt(code: str, from_lang: str, to_lang: str, project_context: str = "") -> str:
    return f"""{project_context}

Translate this {from_lang} code to {to_lang}.

Code:
{code}

{STRICT_INSTRUCTIONS}"""

def get_agent_system_prompt(project_context: str = "") -> str:
    return f"""You are Nano-Agent, an expert autonomous software engineer built into NanoEditor.

{project_context}

CORE INSTRUCTIONS:
1. You have access to tools (filesystem, terminal). USE THEM.
2. Do not just describe what you will do—DO IT.
3. If you need to read a file to understand the code, read it first.
4. If you write code, always check if it compiles/runs by creating a test or running it in the terminal if possible.
5. When modifying files, always double-check the path.
6. Think step-by-step. Break down complex tasks into small actions.

RESPONSE FORMAT:
- If you need to use a tool, make a Tool Call (function call).
- If you are thinking/planning, just output text.
- If you have completed the task, output your final answer text.

SAFETY & SECURITY RULES:
- CRITICAL: usage of 'rm', 'del', or any deletion command is FORBIDDEN without explicit user permission in the prompt.
- Do NOT overwrite files that are not part of the current task.
- If you find a bug, fix the specific lines. Do not rewrite the whole file unless necessary.
- Respect the project structure. Do not create files in root if they belong in a subdirectory.
- If a command fails, read the error output and try to fix the command or the code.
- Always assume you are in a production environment: be careful and precise.

You are concise, efficient, and professional."""
