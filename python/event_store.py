"""
Simple in-memory event store for MCP server resumability.
In production, this should be replaced with a persistent storage solution.
"""

from typing import Any, Dict, List, Optional


class InMemoryEventStore:
    """Simple in-memory event store for development and testing."""
    
    def __init__(self):
        self.events: Dict[str, List[Any]] = {}
    
    async def store_event(self, stream_id: str, message: Any) -> str:
        """Store an event and return its ID."""
        if stream_id not in self.events:
            self.events[stream_id] = []
        
        self.events[stream_id].append(message)
        return str(len(self.events[stream_id]) - 1)
    
    async def replay_events_after(
        self, 
        last_event_id: str, 
        callback_context: Dict[str, Any]
    ) -> str:
        """Replay events after the given event ID."""
        send_func = callback_context.get('send')
        if not send_func:
            return ""
        
        for stream_id, events in self.events.items():
            start_index = int(last_event_id) + 1 if last_event_id else 0
            for i in range(start_index, len(events)):
                await send_func(str(i), events[i])
            return stream_id
        
        return ""
    
    async def get_events(self, session_id: str) -> List[Any]:
        """Get all events for a session."""
        return self.events.get(session_id, [])
    
    async def clear(self, session_id: str) -> None:
        """Clear events for a session."""
        if session_id in self.events:
            del self.events[session_id]
    
    # Legacy compatibility methods
    async def append(self, session_id: str, event: Any) -> str:
        """Legacy method for compatibility."""
        return await self.store_event(session_id, event)