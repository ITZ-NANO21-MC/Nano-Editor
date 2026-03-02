"""Unit tests for Refactoring Tools (Renamer and Extractor)."""
import pytest
import os
import tempfile
from core.refactoring.renamer import Renamer
from core.refactoring.extractor import Extractor, ExtractionResult


# ── Renamer Tests ──────────────────────────────────────────

@pytest.fixture
def renamer():
    return Renamer()


def test_rename_variable(renamer):
    """Test renaming a simple variable."""
    code = "my_var = 10\nprint(my_var)\n"
    result = renamer.apply_rename(code, line=1, column=0, new_name="new_var")
    assert result is not None
    assert "new_var" in result
    assert "my_var" not in result


def test_rename_function(renamer):
    """Test renaming a function definition and its calls."""
    code = "def greet():\n    pass\n\ngreet()\n"
    result = renamer.apply_rename(code, line=1, column=4, new_name="say_hello")
    assert result is not None
    assert "def say_hello():" in result
    assert "say_hello()" in result
    assert "greet" not in result


def test_rename_compute_changes(renamer):
    """Test computing changes without applying."""
    code = "x = 5\nprint(x)\ny = x + 1\n"
    result = renamer.compute_rename(code, line=1, column=0, new_name="value")
    assert result is not None
    assert result.total_replacements >= 1


def test_rename_invalid_position(renamer):
    """Renaming at an invalid position should return None."""
    code = "# just a comment\n"
    result = renamer.apply_rename(code, line=1, column=0, new_name="new_name")
    # Comment positions can't be renamed
    assert result is None


# ── Extractor Tests ────────────────────────────────────────

@pytest.fixture
def extractor():
    return Extractor()


def test_extract_simple_block(extractor):
    """Test extracting a simple block of code."""
    code = (
        "x = 10\n"
        "y = 20\n"
        "result = x + y\n"
        "print(result)\n"
    )
    result = extractor.extract_method(code, start_line=3, end_line=3, function_name="compute")
    assert result is not None
    assert result.function_name == "compute"
    assert "def compute(" in result.function_def
    assert "x" in result.params  # x is used from before
    assert "y" in result.params  # y is used from before


def test_extract_with_return(extractor):
    """Extraction should detect variables used after the selection."""
    code = (
        "a = 5\n"
        "b = 10\n"
        "total = a + b\n"
        "print(total)\n"
    )
    result = extractor.extract_method(code, start_line=3, end_line=3, function_name="add")
    assert result is not None
    # 'total' is used after the selection (line 4), so it should be returned
    assert "total" in result.returns
    assert "return total" in result.function_def


def test_extract_invalid_range(extractor):
    """Invalid line ranges should return None."""
    code = "x = 1\n"
    assert extractor.extract_method(code, start_line=0, end_line=1) is None
    assert extractor.extract_method(code, start_line=1, end_line=5) is None
    assert extractor.extract_method(code, start_line=3, end_line=1) is None


def test_extract_call_statement(extractor):
    """The generated call statement should be correct."""
    code = (
        "data = [1, 2, 3]\n"
        "total = sum(data)\n"
        "average = total / len(data)\n"
        "print(average)\n"
    )
    result = extractor.extract_method(code, start_line=2, end_line=3, function_name="calc_stats")
    assert result is not None
    assert "calc_stats(" in result.call_statement
