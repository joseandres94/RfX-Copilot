from abc import ABC, abstractmethod
from typing import Optional
from ..entities.deal import Deal


class DealRepository(ABC):
    """
    Interface for the Deal repository.
    
    Allows persisting and retrieving deal information independently
    from the underlying implementation (file, database, etc.).
    """
    
    @abstractmethod
    def save(self, deal: Deal) -> None:
        """Save or update a deal"""
        pass
    
    @abstractmethod
    def get(self, deal_id: str) -> Optional[Deal]:
        """Retrieve a deal by its ID"""
        pass

