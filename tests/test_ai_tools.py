import os
import pytest
import tempfile
from ai.tools import ToolRegistry

@pytest.fixture
def tools():
    return ToolRegistry()

@pytest.fixture
def temp_workspace():
    with tempfile.TemporaryDirectory() as d:
        # Create some files
        with open(os.path.join(d, "file1.txt"), "w") as f:
            f.write("Hello World\nLine 2 is here\nfoo bar baz")
            
        with open(os.path.join(d, "file2.py"), "w") as f:
            f.write("def foo():\n    return 42\n")
            
        os.mkdir(os.path.join(d, "subdir"))
        with open(os.path.join(d, "subdir", "nested.txt"), "w") as f:
            f.write("nested level content with foo inside")
            
        yield d

def test_list_dir(tools, temp_workspace):
    res = tools.list_dir(temp_workspace)
    assert "file1.txt" in res
    assert "subdir" in res
    assert "<DIR>" in res
    assert "<FILE>" in res

def test_list_dir_not_found(tools):
    res = tools.list_dir("/non/existent/path/123999")
    assert "Error: Directory not found" in res

def test_grep_search(tools, temp_workspace):
    res = tools.grep_search(temp_workspace, "foo")
    # should find in file1.txt, file2.py, and nested.txt
    assert "file1.txt:3:foo bar baz" in res
    assert "file2.py:1:def foo():" in res
    assert "subdir/nested.txt:1:nested level content with foo inside" in res.replace('\\', '/')

def test_grep_search_regex(tools, temp_workspace):
    res = tools.grep_search(temp_workspace, "^def ")
    assert "file2.py:1:def foo():" in res
    assert "file1.txt" not in res

def test_replace_file_content(tools, temp_workspace):
    target_file = os.path.join(temp_workspace, "file2.py")
    
    # Successful replacement
    res = tools.replace_file_content(
        target_file, 
        target_text="    return 42\n", 
        replacement_text="    return 99\n"
    )
    assert "✅" in res
    
    with open(target_file, "r") as f:
        content = f.read()
    assert "return 99" in content
    assert "return 42" not in content

def test_replace_file_content_not_found(tools, temp_workspace):
    target_file = os.path.join(temp_workspace, "file1.txt")
    
    # Missing text
    res = tools.replace_file_content(target_file, "Line 3", "Line 4")
    assert "❌ Error" in res
    
    # Duplicate text (fails safe)
    with open(target_file, "a") as f:
        f.write("\nfoo")
    res = tools.replace_file_content(target_file, "foo", "bar") # "foo" appears twice now
    assert "❌ Error" in res
    assert "multiple times" in res
