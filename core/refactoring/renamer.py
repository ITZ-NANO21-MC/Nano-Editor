"""Renamer: Intelligent symbol renaming using Jedi.

Uses jedi.Script.rename() to find all references of a symbol and
compute the required text changes across multiple files.
"""
import os
from typing import List, Dict, Optional, Tuple
from logger import logger

try:
    import jedi
    HAS_JEDI = True
except ImportError:
    HAS_JEDI = False
    logger.warning("Jedi not available; rename functionality disabled.")


class RenameResult:
    """Holds the result of a rename operation."""
    def __init__(self):
        self.changes: Dict[str, List[Tuple[int, str, str]]] = {}
        # {file_path: [(line_number, old_text, new_text), ...]}
        self.total_replacements = 0
        self.files_affected = 0


class Renamer:
    """Handles intelligent symbol renaming via Jedi."""

    def __init__(self):
        if not HAS_JEDI:
            raise RuntimeError("Jedi is required for rename functionality.")

    def compute_rename(self, code: str, line: int, column: int,
                       new_name: str, file_path: str = "temp.py") -> Optional[RenameResult]:
        """Compute the changes needed to rename a symbol.

        Args:
            code: The full source code of the file.
            line: 1-indexed line number of the symbol.
            column: 0-indexed column offset of the symbol.
            new_name: The new name for the symbol.
            file_path: Path to the file (for cross-file analysis).

        Returns:
            A RenameResult with all needed changes, or None if rename is not possible.
        """
        try:
            script = jedi.Script(code, path=file_path)
            refactoring = script.rename(line=line, column=column, new_name=new_name)

            result = RenameResult()
            changed_files = refactoring.get_changed_files()

            for fpath, change in changed_files.items():
                fpath_str = str(fpath)
                new_code = change.get_new_code()

                # Read original file to compute line-by-line diffs
                if os.path.isfile(fpath_str):
                    with open(fpath_str, 'r', encoding='utf-8') as f:
                        original_lines = f.readlines()
                else:
                    original_lines = code.splitlines(keepends=True)

                new_lines = new_code.splitlines(keepends=True)
                file_changes = []

                for i, (old, new) in enumerate(zip(original_lines, new_lines)):
                    if old != new:
                        file_changes.append((i + 1, old.rstrip('\n'), new.rstrip('\n')))

                if file_changes:
                    result.changes[fpath_str] = file_changes
                    result.total_replacements += len(file_changes)

            result.files_affected = len(result.changes)
            return result

        except AttributeError:
            logger.warning("Jedi rename returned no results for this symbol.")
            return None
        except Exception as e:
            logger.error(f"Rename error: {e}")
            return None

    def apply_rename(self, code: str, line: int, column: int,
                     new_name: str, file_path: str = "temp.py") -> Optional[str]:
        """Apply a rename directly and return the new code for the current file.

        This is a convenience method for single-file renames.

        Returns:
            The new source code string, or None on failure.
        """
        try:
            script = jedi.Script(code, path=file_path)
            refactoring = script.rename(line=line, column=column, new_name=new_name)

            changed_files = refactoring.get_changed_files()
            for fpath, change in changed_files.items():
                if str(fpath) == file_path or str(fpath).endswith(os.path.basename(file_path)):
                    return change.get_new_code()

            return None
        except Exception as e:
            logger.error(f"Apply rename error: {e}")
            return None
