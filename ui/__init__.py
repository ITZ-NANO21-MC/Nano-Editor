"""UI module - User Interface components for NanoEditor."""
from ui.sidebar import VSCodeSidebar
from ui.file_tree import VSCodeFileTree
from ui.ai_panel import AIAssistantPanel
from ui.gemini_panel import GeminiPanel
from ui.gemini_client import GeminiClient
from ui.agent_panel import AgentPanel
from ui.status_bar import StatusBar
from ui.menu_bar import ModernMenuBar

__all__ = [
    'VSCodeSidebar', 'VSCodeFileTree', 'AIAssistantPanel',
    'GeminiPanel', 'GeminiClient', 'AgentPanel',
    'StatusBar', 'ModernMenuBar'
]
