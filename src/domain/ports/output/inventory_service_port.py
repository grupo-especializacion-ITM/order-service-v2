from abc import ABC, abstractmethod
from typing import Dict, List
from uuid import UUID

from src.domain.entities.order_item import OrderItem


class InventoryServicePort(ABC):
    """Port for inventory service operations"""
    
    @abstractmethod
    async def validate_items_availability(self, items: List[OrderItem]) -> Dict[UUID, bool]:
        """
        Validate the availability of items
        
        Returns a dictionary with item IDs as keys and boolean availability as values
        """
        pass