"""Unit tests for Refactoring Tools (Renamer and Extractor)."""
import pytest
import os
import tempfile
from core.refactoring.renamer import Renamer
from core.refactoring.extractor import Extractor, ExtractionResult, VariableExtractionResult
from core.refactoring.mover import Mover, MoveResult


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

def test_extract_variable(extractor):
    """Test extracting an expression into a variable."""
    code = (
        "x = 10\n"
        "result = x + 20\n"
        "print(result)\n"
    )
    # Extract "x + 20" from line 2 (columns 9 to 15)
    result = extractor.extract_variable(code, start_line=2, end_line=2, start_col=9, end_col=15, var_name="addition")
    assert result is not None
    assert result.var_name == "addition"
    assert "addition = x + 20" in result.assignment_statement
    assert "result = addition" in result.modified_code

def test_extract_variable_invalid_expression(extractor):
    """Extraction should fail if the selection is not a valid expression."""
    code = "if x == 10:\n    pass\n"
    # Select "if x == 1"
    result = extractor.extract_variable(code, start_line=1, end_line=1, start_col=0, end_col=10, var_name="invalid")
    assert result is None

# ── Mover Tests ────────────────────────────────────────

@pytest.fixture
def mover():
    return Mover()

def test_move_to_file_success(mover):
    """Test moving a class to another file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = os.path.join(tmpdir, "source.py")
        target_path = os.path.join(tmpdir, "target.py")
        
        source_code = (
            "import os\n\n"
            "class MyClass:\n"
            "    def method(self):\n"
            "        pass\n\n"
            "def other_func():\n"
            "    pass\n"
        )
        with open(source_path, 'w') as f:
            f.write(source_code)
            
        result = mover.move_to_file(tmpdir, source_path, target_path, start_line=3, end_line=5)
        
        assert result is not None
        assert result.symbol_name == "MyClass"
        assert "class MyClass" not in result.source_file_content
        assert "def other_func" in result.source_file_content
        assert "class MyClass" in result.target_file_content

def test_move_to_file_invalid_block(mover):
    """Moving a block that is not a class or function should fail."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = os.path.join(tmpdir, "source.py")
        target_path = os.path.join(tmpdir, "target.py")
        
        source_code = "x = 10\ny = 20\n"
        with open(source_path, 'w') as f:
            f.write(source_code)
            
        result = mover.move_to_file(tmpdir, source_path, target_path, start_line=1, end_line=2)
        assert result is None
