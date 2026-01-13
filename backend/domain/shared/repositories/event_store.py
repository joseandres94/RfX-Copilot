from abc import ABC, abstractmethod
from typing import List
from ..entities.pipeline_event import PipelineEvent


class EventStore(ABC):
    """
    Interface for the pipeline event store.
    
    Allows adding and querying events generated during the execution
    of a deal's pipeline.
    """
    
    @abstractmethod
    def append_event(self, deal_id: str, event: PipelineEvent) -> int:
        """
        Adds an event to the store and returns the assigned event_id.
        
        Args:
            deal_id: Deal ID
            event: Event to add

        Returns:
            Event ID (incremental per deal)
        """
        pass
    
    @abstractmethod
    def get_events(self, deal_id: str, since_event_id: int = 0) -> List[PipelineEvent]:
        """
        Retrieves the events of a deal, optionally since a specific event_id.
        
        Args:
            deal_id: Deal ID
            since_event_id: Retrieve events with ID greater than this value
            
        Returns:
            List of events ordered by ID
        """
        pass

