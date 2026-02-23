"""Navigation module - Code navigation for NanoEditor."""
from navigation.goto_definition import GotoDefinition, setup_goto_definition_bindings
from navigation.project_context import ProjectContext
from navigation.project_search import ProjectSearchWindow

__all__ = ['GotoDefinition', 'setup_goto_definition_bindings', 'ProjectContext', 'ProjectSearchWindow']
