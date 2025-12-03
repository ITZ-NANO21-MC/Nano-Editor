"""Simple event bus for decoupling components."""
from typing import Callable, Dict, List, Any, Optional

class EventBus:
    """Lightweight event bus using Observer pattern."""
    
    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event: str, callback: Callable[[Any], None]) -> None:
        """Subscribe to an event."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)
    
    def emit(self, event: str, data: Optional[Any] = None) -> None:
        """Emit an event to all subscribers."""
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    from logger import logger
                    logger.error(f"Event callback error: {e}")
    
    def unsubscribe(self, event: str, callback: Callable) -> None:
        """Unsubscribe from an event."""
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)

class Events:
    """Event name constants."""
    # File events
    FILE_OPENED = "file_opened"
    FILE_SAVED = "file_saved"
    FILE_CLOSED = "file_closed"
    
    # Tab events
    TAB_CHANGED = "tab_changed"
    TAB_CREATED = "tab_created"
    TAB_CLOSED = "tab_closed"
    
    # Theme events
    THEME_CHANGED = "theme_changed"
    
    # AI events
    AI_STARTED = "ai_started"
    AI_COMPLETED = "ai_completed"
    AI_ERROR = "ai_error"

# Global event bus instance
event_bus = EventBus()
