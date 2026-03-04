import os
import subprocess
from typing import List, Dict, Optional, Tuple
from logger import logger

class GitError(Exception):
    """Custom exception for Git related errors."""
    pass

class GitManager:
    """Wrapper for executing Git commands programmatically."""
    
    def __init__(self, repo_path: str):
        """Initialize GitManager with the repository path.
        
        Args:
            repo_path: The absolute path to the git repository.
        """
        self.repo_path = repo_path
    
    def _run_git_command(self, cmd: List[str]) -> Tuple[bool, str]:
        """Execute a git command in the repository path.
        
        Args:
            cmd: List of strings forming the git command (e.g., ['status', '-s']).
            
        Returns:
            A tuple (success (bool), output (str)). If not success, output contains stderr.
        """
        try:
            full_cmd = ['git'] + cmd
            result = subprocess.run(
                full_cmd, 
                cwd=self.repo_path, 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        except FileNotFoundError:
            return False, "Git executable not found."
        except Exception as e:
            return False, str(e)

    def is_git_repo(self) -> bool:
        """Check if the current path is a valid git repository."""
        success, _ = self._run_git_command(['rev-parse', '--is-inside-work-tree'])
        return success

    def get_status(self) -> List[Dict[str, str]]:
        """Get the git status.
        
        Returns:
            List of dicts: [{'file': 'filepath', 'status': 'status_code'}]
            Example status codes: ' M' (modified), 'A ' (added), '??' (untracked)
        """
        success, output = self._run_git_command(['status', '--porcelain'])
        if not success:
            logger.error(f"Failed to get git status: {output}")
            return []
            
        status_list = []
        if not output:
            return status_list
            
        for line in output.split('\n'):
            if len(line) >= 3:
                # The format is XY PATH. We keep X and Y as a 2-char string.
                status_code = line[0:2]
                file_path = line[2:].strip().strip('"')
                status_list.append({
                    'file': file_path,
                    'status': status_code
                })
        return status_list

    def get_current_branch(self) -> Optional[str]:
        """Get the name of the current branch."""
        success, output = self._run_git_command(['branch', '--show-current'])
        if success:
            return output if output else None
        
        # Fallback for older git versions or detached HEAD
        success, output = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        return output if success else None

    def add_file(self, filepath: str) -> bool:
        """Add a specific file to staging (git add)."""
        success, output = self._run_git_command(['add', filepath])
        if not success:
            logger.error(f"Failed to add file {filepath}: {output}")
        return success

    def add_all(self) -> bool:
        """Add all modified and untracked files to staging (git add .)."""
        success, output = self._run_git_command(['add', '.'])
        if not success:
            logger.error(f"Failed to add all files: {output}")
        return success

    def commit(self, message: str) -> bool:
        """Commit staged changes.
        
        Args:
            message: The commit message.
        """
        success, output = self._run_git_command(['commit', '-m', message])
        if not success:
            logger.error(f"Failed to commit: {output}")
        return success

    def get_diff(self, filepath: str) -> str:
        """Get the diff for a specific file (unstaged changes)."""
        success, output = self._run_git_command(['diff', filepath])
        if success:
            return output
        return ""

    def get_staged_diff(self, filepath: str) -> str:
        """Get the diff for a specific file (staged changes)."""
        success, output = self._run_git_command(['diff', '--cached', filepath])
        if success:
            return output
        return ""

    def get_branches(self) -> List[str]:
        """Get a list of all local branches."""
        success, output = self._run_git_command(['branch', '--format=%(refname:short)'])
        if success and output:
            return [b.strip() for b in output.split('\n') if b.strip()]
        return []

    def create_branch(self, name: str) -> bool:
        """Create a new branch."""
        success, output = self._run_git_command(['branch', name])
        if not success:
            logger.error(f"Failed to create branch {name}: {output}")
        return success

    def checkout_branch(self, name: str) -> bool:
        """Switch to an existing branch."""
        success, output = self._run_git_command(['checkout', name])
        if not success:
            logger.error(f"Failed to checkout branch {name}: {output}")
        return success

    def delete_branch(self, name: str, force: bool = False) -> bool:
        """Delete a branch.
        
        Args:
            name: Name of branch to delete
            force: Use -D (force) instead of -d
        """
        flag = '-D' if force else '-d'
        success, output = self._run_git_command(['branch', flag, name])
        if not success:
            logger.error(f"Failed to delete branch {name}: {output}")
        return success

    def merge_branch(self, name: str) -> Tuple[bool, str]:
        """Merge a branch into the current one.
        
        Returns:
            Tuple of (success, output message). Success is False if there are conflicts.
        """
        try:
            full_cmd = ['git', 'merge', name]
            result = subprocess.run(
                full_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            # git merge outputs CONFLICT info to stdout even when failing
            combined_output = (result.stdout + result.stderr).strip()
            
            if result.returncode == 0:
                return True, "Merge successful."
            else:
                if "CONFLICT" in combined_output:
                    return False, "Merge conflict detected. Please resolve conflicts."
                logger.error(f"Failed to merge {name}: {combined_output}")
                return False, combined_output
        except FileNotFoundError:
            return False, "Git executable not found."
        except Exception as e:
            return False, str(e)


    def get_conflicted_files(self) -> List[str]:
        """Get a list of files with merge conflicts."""
        success, output = self._run_git_command(['diff', '--name-only', '--diff-filter=U'])
        if success and output:
             return [f.strip() for f in output.split('\n') if f.strip()]
        return []
