"""Unit tests for BreakpointManager."""
import pytest
from core.debugger.breakpoint_manager import BreakpointManager


@pytest.fixture
def bp_manager():
    """Fresh BreakpointManager instance."""
    return BreakpointManager()


def test_add_breakpoint(bp_manager):
    """Test adding a breakpoint."""
    assert bp_manager.add_breakpoint("test.py", 10) is True
    assert bp_manager.has_breakpoint("test.py", 10) is True


def test_add_duplicate_breakpoint(bp_manager):
    """Adding the same breakpoint twice should return False."""
    bp_manager.add_breakpoint("test.py", 5)
    assert bp_manager.add_breakpoint("test.py", 5) is False


def test_add_invalid_line(bp_manager):
    """Adding a breakpoint at line 0 or negative should fail."""
    assert bp_manager.add_breakpoint("test.py", 0) is False
    assert bp_manager.add_breakpoint("test.py", -1) is False


def test_remove_breakpoint(bp_manager):
    """Test removing an existing breakpoint."""
    bp_manager.add_breakpoint("test.py", 10)
    assert bp_manager.remove_breakpoint("test.py", 10) is True
    assert bp_manager.has_breakpoint("test.py", 10) is False


def test_remove_nonexistent(bp_manager):
    """Removing a breakpoint that doesn't exist should return False."""
    assert bp_manager.remove_breakpoint("test.py", 99) is False


def test_toggle_breakpoint(bp_manager):
    """Toggle should add if absent and remove if present."""
    # First toggle: add
    assert bp_manager.toggle_breakpoint("test.py", 7) is True
    assert bp_manager.has_breakpoint("test.py", 7) is True

    # Second toggle: remove
    assert bp_manager.toggle_breakpoint("test.py", 7) is False
    assert bp_manager.has_breakpoint("test.py", 7) is False


def test_get_breakpoints_sorted(bp_manager):
    """Breakpoints should be returned in sorted order."""
    bp_manager.add_breakpoint("test.py", 20)
    bp_manager.add_breakpoint("test.py", 5)
    bp_manager.add_breakpoint("test.py", 12)
    assert bp_manager.get_breakpoints("test.py") == [5, 12, 20]


def test_get_breakpoints_empty_file(bp_manager):
    """Getting breakpoints for a file with none should return empty list."""
    assert bp_manager.get_breakpoints("nonexistent.py") == []


def test_multiple_files(bp_manager):
    """Test breakpoints across multiple files."""
    bp_manager.add_breakpoint("a.py", 1)
    bp_manager.add_breakpoint("b.py", 2)
    bp_manager.add_breakpoint("a.py", 3)

    assert bp_manager.get_breakpoints("a.py") == [1, 3]
    assert bp_manager.get_breakpoints("b.py") == [2]


def test_clear_file(bp_manager):
    """Clearing breakpoints for one file shouldn't affect others."""
    bp_manager.add_breakpoint("a.py", 1)
    bp_manager.add_breakpoint("a.py", 5)
    bp_manager.add_breakpoint("b.py", 10)

    assert bp_manager.clear_file("a.py") == 2
    assert bp_manager.get_breakpoints("a.py") == []
    assert bp_manager.get_breakpoints("b.py") == [10]


def test_clear_all(bp_manager):
    """Clear all should remove everything."""
    bp_manager.add_breakpoint("a.py", 1)
    bp_manager.add_breakpoint("b.py", 2)

    assert bp_manager.clear_all() == 2
    assert bp_manager.get_all_breakpoints() == {}


def test_get_all_breakpoints(bp_manager):
    """Test aggregated breakpoint retrieval."""
    bp_manager.add_breakpoint("x.py", 10)
    bp_manager.add_breakpoint("y.py", 3)
    bp_manager.add_breakpoint("x.py", 2)

    result = bp_manager.get_all_breakpoints()
    assert result == {"x.py": [2, 10], "y.py": [3]}


def test_listener_called(bp_manager):
    """Test that listeners are notified on add/remove."""
    events = []
    bp_manager.add_listener(lambda fp, ln, added: events.append((fp, ln, added)))

    bp_manager.add_breakpoint("test.py", 5)
    bp_manager.remove_breakpoint("test.py", 5)

    assert events == [
        ("test.py", 5, True),
        ("test.py", 5, False),
    ]
