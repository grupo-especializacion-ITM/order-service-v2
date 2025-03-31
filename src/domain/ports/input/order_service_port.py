from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.value_objects.delivery_address import DeliveryAddress


class OrderServicePort(ABC):
    """Port for order service operations"""
    
    @abstractmethod
    async def create_order(
        self,
        customer_id: UUID,
        items: List[OrderItem],
        delivery_address: DeliveryAddress,
        notes: Optional[str] = None
    ) -> Order:
        """Create a new order"""
        pass
    
    @abstractmethod
    async def add_item_to_order(self, order_id: UUID, item: OrderItem) -> Order:
        """Add an item to an order"""
        pass
    
    @abstractmethod
    async def remove_item_from_order(self, order_id: UUID, item_id: UUID) -> Order:
        """Remove an item from an order"""
        pass
    
    @abstractmethod
    async def update_order_status(self, order_id: UUID, status: OrderStatus) -> Order:
        """Update the status of an order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: UUID) -> Order:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def confirm_order(self, order_id: UUID) -> Order:
        """Confirm an order"""
        pass
