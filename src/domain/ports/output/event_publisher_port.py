from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.domain.entities.order import Order


class EventPublisherPort(ABC):
    """Port for publishing events"""
    
    @abstractmethod
    async def publish_order_created(self, order: Order) -> None:
        """Publish an order created event"""
        pass
    
    @abstractmethod
    async def publish_order_confirmed(self, order: Order) -> None:
        """Publish an order confirmed event"""
        pass
    
    @abstractmethod
    async def publish_order_cancelled(self, order: Order) -> None:
        """Publish an order cancelled event"""
        pass
    
    @abstractmethod
    async def publish_order_status_updated(self, order: Order, previous_status: str) -> None:
        """Publish an order status updated event"""
        pass
    
    @abstractmethod
    async def publish_event(self, event_type: str, payload: Dict[str, Any], topic: Optional[str] = None) -> None:
        """Publish a generic event"""
        pass