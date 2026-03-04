"""Unit tests for GitManager class."""
import os
import tempfile
import subprocess
import shutil
import pytest
from core.git.git_manager import GitManager

@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=temp_dir, check=True, capture_output=True)
        # Configure local git user to avoid commit errors on CI/anonymous environments
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, check=True)
        
        # Create an initial file and commit
        init_file = os.path.join(temp_dir, "init.txt")
        with open(init_file, 'w') as f:
            f.write("Initial commit.")
        
        subprocess.run(['git', 'add', 'init.txt'], cwd=temp_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=temp_dir, check=True)
        
        yield temp_dir
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

@pytest.fixture
def non_git_dir():
    """Create a temporary directory that is not a git repo."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_is_git_repo(temp_git_repo, non_git_dir):
    """Test repository detection."""
    manager_valid = GitManager(temp_git_repo)
    assert manager_valid.is_git_repo() is True
    
    manager_invalid = GitManager(non_git_dir)
    assert manager_invalid.is_git_repo() is False

def test_get_current_branch(temp_git_repo):
    """Test getting current branch name."""
    manager = GitManager(temp_git_repo)
    branch = manager.get_current_branch()
    assert branch in ['master', 'main'] # Depends on git default config

def test_get_status_clean(temp_git_repo):
    """Test status string parsing on clean repo."""
    manager = GitManager(temp_git_repo)
    status = manager.get_status()
    assert len(status) == 0

def test_get_status_untracked(temp_git_repo):
    """Test status string parsing with an untracked file."""
    manager = GitManager(temp_git_repo)
    
    # Create a new file
    new_file = os.path.join(temp_git_repo, "new_file.py")
    with open(new_file, 'w') as f:
        f.write("print('Hello')")
        
    status = manager.get_status()
    assert len(status) == 1
    assert status[0]['file'] == 'new_file.py'
    assert status[0]['status'] == '??'

def test_get_status_modified(temp_git_repo):
    """Test status parsing with a modified tracked file."""
    manager = GitManager(temp_git_repo)
    
    # Modify the initial file
    init_file = os.path.join(temp_git_repo, "init.txt")
    with open(init_file, 'a') as f:
        f.write("\nAppended text.")
        
    status = manager.get_status()
    assert len(status) == 1
    assert status[0]['file'] == 'init.txt'
    assert status[0]['status'].strip() == 'M'

def test_add_and_commit(temp_git_repo):
    """Test git add and commit functionality."""
    manager = GitManager(temp_git_repo)
    
    # Create untracked file
    new_file = os.path.join(temp_git_repo, "feat.txt")
    with open(new_file, 'w') as f:
        f.write("New feature")
        
    # Check status -> ??
    assert any(s['file'] == 'feat.txt' and s['status'] == '??' for s in manager.get_status())
    
    # Add file -> A
    assert manager.add_file('feat.txt') is True
    assert any(s['file'] == 'feat.txt' and s['status'].startswith('A') for s in manager.get_status())
    
    # Commit
    assert manager.commit("Add feat.txt") is True
    
    # Status should be clean
    assert len(manager.get_status()) == 0

def test_branching(temp_git_repo):
    """Test branch creation, listing, switching, and deletion."""
    manager = GitManager(temp_git_repo)
    
    # 1. Create a branch
    assert manager.create_branch("feature-x") is True
    
    # 2. List branches
    branches = manager.get_branches()
    assert "feature-x" in branches
    # default branch (main or master) should also be there
    
    # 3. Checkout branch
    assert manager.checkout_branch("feature-x") is True
    assert manager.get_current_branch() == "feature-x"
    
    # Can't delete current branch
    assert manager.delete_branch("feature-x") is False
    
    # Checkout master/main and delete
    default_branch = manager.get_branches()
    default_branch.remove("feature-x")
    assert manager.checkout_branch(default_branch[0]) is True
    assert manager.delete_branch("feature-x") is True
    assert "feature-x" not in manager.get_branches()

def test_merge_conflicts(temp_git_repo):
    """Test merging and getting conflicted files."""
    manager = GitManager(temp_git_repo)
    default_branch = manager.get_current_branch()
    
    # 1. Create and switch to new branch
    manager.create_branch("conflict-branch")
    manager.checkout_branch("conflict-branch")
    
    # 2. Modify file in new branch
    init_file = os.path.join(temp_git_repo, "init.txt")
    with open(init_file, 'w') as f:
        f.write("Changed in conflict-branch")
    manager.add_all()
    manager.commit("Branch change")
    
    # 3. Switch back to default and modify same file
    manager.checkout_branch(default_branch)
    with open(init_file, 'w') as f:
        f.write("Changed in default branch")
    manager.add_all()
    manager.commit("Default change")
    
    # 4. Attempt merge
    success, msg = manager.merge_branch("conflict-branch")
    assert success is False
    assert "conflict" in msg.lower()
    
    # 5. Check for conflicted files
    conflicted = manager.get_conflicted_files()
    assert len(conflicted) == 1
    assert conflicted[0] == "init.txt"

