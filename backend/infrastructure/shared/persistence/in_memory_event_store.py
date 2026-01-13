import logging
import threading
from typing import Dict, List
from datetime import datetime

from ....domain.shared.repositories.event_store import EventStore
from ....domain.shared.entities.pipeline_event import PipelineEvent

logger = logging.getLogger(__name__)


class InMemoryEventStore(EventStore):
    """
    In-memory implementation of the EventStore with thread-safety.

    Thread-safe using threading.Lock to prevent race conditions.
    """
    
    def __init__(self):
        # Structure: {deal_id: [PipelineEvent, ...]}
        self._events: Dict[str, List[PipelineEvent]] = {}
        # Lock for thread-safe operations
        self._lock = threading.Lock()
        logger.info("InMemoryEventStore initialized (in-memory, thread-safe)")
    
    def append_event(self, deal_id: str, event: PipelineEvent) -> int:
        """
        Adds an event in a thread-safe way and returns the assigned event_id.
        """
        with self._lock:
            # Initialize list if it does not exist
            if deal_id not in self._events:
                self._events[deal_id] = []
            
            # Assign incremental ID
            event_id = len(self._events[deal_id]) + 1
            event.id = event_id
            
            # Add event
            self._events[deal_id].append(event)
            
            logger.debug(f"Event appended for deal {deal_id}: {event.type.value} - {event.message}")
            return event_id
    
    def get_events(self, deal_id: str, since_event_id: int = 0) -> List[PipelineEvent]:
        """
        Retrieves events in a thread-safe way.
        """
        with self._lock:
            if deal_id not in self._events:
                return []
            
            # Filter events with ID > since_event_id
            events = [
                event for event in self._events[deal_id]
                if event.id > since_event_id
            ]
            
            return events

