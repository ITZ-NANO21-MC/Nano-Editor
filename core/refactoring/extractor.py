"""Extractor: Extracts selected code blocks into new functions.

Uses Python's `ast` module to analyze variables entering and exiting the
selected block, generating a proper function signature.
"""
import ast
import textwrap
import builtins
from typing import Optional, Set
from logger import logger


class ExtractionResult:
    """Result of an extract-method operation."""
    def __init__(self):
        self.function_name: str = ""
        self.function_def: str = ""
        self.call_statement: str = ""
        self.returns: list = []


class VariableExtractionResult:
    """Result of an extract-variable operation."""
    def __init__(self):
        self.var_name: str = ""
        self.assignment_statement: str = ""
        self.modified_code: str = ""



class Extractor:
    """Handles extraction of code blocks into functions."""

    def extract_method(self, full_code: str, start_line: int, end_line: int,
                       function_name: str = "extracted_function") -> Optional[ExtractionResult]:
        """Extract lines [start_line, end_line] into a new function.

        Args:
            full_code: The complete source code.
            start_line: 1-indexed start line of the selection.
            end_line: 1-indexed end line of the selection.
            function_name: The name for the new function.

        Returns:
            ExtractionResult with the function definition and call statement.
        """
        lines = full_code.splitlines(keepends=True)

        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            logger.error(f"Invalid line range: {start_line}-{end_line}")
            return None

        # Extract the selected block
        selected_lines = lines[start_line - 1:end_line]
        selected_code = ''.join(selected_lines)

        # Detect indentation level of the first selected line
        first_line = selected_lines[0]
        indent = len(first_line) - len(first_line.lstrip())
        indent_str = first_line[:indent]

        # Dedent the selected block for analysis
        dedented = textwrap.dedent(selected_code)

        # Analyze variables
        try:
            selected_names = self._get_names(dedented)
        except SyntaxError:
            # If the selection isn't valid Python on its own, wrap analysis
            selected_names = self._get_names_fallback(dedented)

        # Analyze context: variables defined BEFORE the selection
        before_code = ''.join(lines[:start_line - 1])
        after_code = ''.join(lines[end_line:])

        before_names = self._get_defined_names(before_code)
        after_used = self._get_used_names(after_code)
        builtin_names = set(dir(builtins))

        # Parameters: variables used in selection that are defined before (ignoring builtins)
        params = sorted((selected_names['used'] & before_names) - builtin_names)

        # Returns: variables assigned in selection that are used after
        returns = sorted((selected_names['assigned'] & after_used) - builtin_names)

        # Build result
        result = ExtractionResult()
        result.function_name = function_name
        result.params = params
        result.returns = returns

        # Build function definition
        param_str = ', '.join(params)
        func_lines = [f"def {function_name}({param_str}):"]

        for line in dedented.splitlines():
            func_lines.append(f"    {line}" if line.strip() else "")

        if returns:
            return_str = ', '.join(returns)
            func_lines.append(f"    return {return_str}")

        result.function_def = '\n'.join(func_lines)

        # Build call statement
        call_args = ', '.join(params)
        if returns:
            return_vars = ', '.join(returns)
            result.call_statement = f"{indent_str}{return_vars} = {function_name}({call_args})"
        else:
            result.call_statement = f"{indent_str}{function_name}({call_args})"

        return result

    def _get_names(self, code: str) -> dict:
        """Parse code and extract used/assigned variable names."""
        used = set()
        assigned = set()
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):
                        assigned.add(node.id)
                    elif isinstance(node.ctx, ast.Load):
                        used.add(node.id)
        except SyntaxError:
            pass
        return {'used': used, 'assigned': assigned}

    def _get_names_fallback(self, code: str) -> dict:
        """Fallback name extraction for incomplete code blocks."""
        # Wrap in a function so it's parseable
        wrapped = f"def _wrapper():\n" + textwrap.indent(code, "    ")
        return self._get_names(wrapped)

    def _get_defined_names(self, code: str) -> Set[str]:
        """Get all names that are assigned/defined in the code."""
        try:
            tree = ast.parse(code)
            names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    names.add(node.id)
                elif isinstance(node, ast.FunctionDef):
                    names.add(node.name)
                    for arg in node.args.args:
                        names.add(arg.arg)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        names.add(alias.asname or alias.name)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        names.add(alias.asname or alias.name)
            return names
        except SyntaxError:
            return set()

    def _get_used_names(self, code: str) -> Set[str]:
        """Get all names that are used (loaded) in the code."""
        try:
            tree = ast.parse(code)
            names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    names.add(node.id)
            return names
        except SyntaxError:
            return set()

    def extract_variable(self, full_code: str, start_line: int, end_line: int,
                         start_col: int, end_col: int, var_name: str = "new_var") -> Optional['VariableExtractionResult']:
        """Extract a selected expression into a new variable."""
        lines = full_code.splitlines(keepends=True)
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            logger.error(f"Invalid line range: {start_line}-{end_line}")
            return None

        if start_line == end_line:
            raw_expression = lines[start_line - 1][start_col:end_col]
        else:
            first = lines[start_line - 1][start_col:]
            mid = "".join(lines[start_line:end_line - 1])
            last = lines[end_line - 1][:end_col]
            raw_expression = first + mid + last

        expression = raw_expression.strip()
        if not expression:
            return None

        try:
            ast.parse(expression, mode='eval')
        except SyntaxError:
            logger.error(f"Selection '{expression}' is not a valid Python expression.")
            return None

        target_line = lines[start_line - 1]
        indent = len(target_line) - len(target_line.lstrip())
        indent_str = target_line[:indent]

        result = VariableExtractionResult()
        result.var_name = var_name
        result.assignment_statement = f"{indent_str}{var_name} = {expression}\n"

        if start_line == end_line:
            new_line = lines[start_line - 1][:start_col] + var_name + lines[start_line - 1][end_col:]
            lines[start_line - 1] = new_line
        else:
            lines[start_line - 1] = lines[start_line - 1][:start_col] + var_name + lines[end_line - 1][end_col:]
            for i in range(start_line, end_line):
                lines[i] = ""

        result.modified_code = "".join(lines)
        return result
