"""BreakpointManager: Manages breakpoints for file debugging sessions.

This module provides a clean data structure to add, remove, toggle, 
and query breakpoints by file. It is decoupled from the UI and can 
be tested independently.
"""
from typing import Dict, List, Set
from logger import logger


class BreakpointManager:
    """Manages breakpoints across multiple files."""

    def __init__(self):
        # {file_path: set(line_numbers)}
        self._breakpoints: Dict[str, Set[int]] = {}
        # Callbacks for UI notification
        self._listeners = []

    def add_listener(self, callback):
        """Register a callback to be notified on breakpoint changes.
        
        Callback signature: callback(file_path: str, line: int, added: bool)
        """
        self._listeners.append(callback)

    def _notify(self, file_path: str, line: int, added: bool):
        """Notify all listeners of a breakpoint change."""
        for cb in self._listeners:
            try:
                cb(file_path, line, added)
            except Exception as e:
                logger.error(f"Error in breakpoint listener: {e}")

    def add_breakpoint(self, file_path: str, line: int) -> bool:
        """Add a breakpoint at a specific line in a file.
        
        Returns True if the breakpoint was added, False if it already existed.
        """
        if line < 1:
            return False
            
        if file_path not in self._breakpoints:
            self._breakpoints[file_path] = set()

        if line in self._breakpoints[file_path]:
            return False  # Already exists

        self._breakpoints[file_path].add(line)
        logger.info(f"Breakpoint added: {file_path}:{line}")
        self._notify(file_path, line, added=True)
        return True

    def remove_breakpoint(self, file_path: str, line: int) -> bool:
        """Remove a breakpoint at a specific line.
        
        Returns True if removed, False if it didn't exist.
        """
        if file_path not in self._breakpoints:
            return False

        if line not in self._breakpoints[file_path]:
            return False

        self._breakpoints[file_path].discard(line)
        logger.info(f"Breakpoint removed: {file_path}:{line}")
        self._notify(file_path, line, added=False)

        # Clean up empty sets
        if not self._breakpoints[file_path]:
            del self._breakpoints[file_path]

        return True

    def toggle_breakpoint(self, file_path: str, line: int) -> bool:
        """Toggle a breakpoint: add if absent, remove if present.
        
        Returns True if the breakpoint is now active, False if removed.
        """
        if self.has_breakpoint(file_path, line):
            self.remove_breakpoint(file_path, line)
            return False
        else:
            self.add_breakpoint(file_path, line)
            return True

    def has_breakpoint(self, file_path: str, line: int) -> bool:
        """Check if a breakpoint exists at a specific location."""
        return file_path in self._breakpoints and line in self._breakpoints[file_path]

    def get_breakpoints(self, file_path: str) -> List[int]:
        """Get all breakpoint line numbers for a file, sorted."""
        if file_path not in self._breakpoints:
            return []
        return sorted(self._breakpoints[file_path])

    def get_all_breakpoints(self) -> Dict[str, List[int]]:
        """Get all breakpoints across all files."""
        return {fp: sorted(lines) for fp, lines in self._breakpoints.items()}

    def clear_file(self, file_path: str) -> int:
        """Remove all breakpoints for a specific file. Returns count removed."""
        if file_path not in self._breakpoints:
            return 0
        count = len(self._breakpoints[file_path])
        del self._breakpoints[file_path]
        logger.info(f"Cleared {count} breakpoints from {file_path}")
        return count

    def clear_all(self) -> int:
        """Remove all breakpoints from all files. Returns total count removed."""
        total = sum(len(lines) for lines in self._breakpoints.values())
        self._breakpoints.clear()
        logger.info(f"Cleared all {total} breakpoints")
        return total
