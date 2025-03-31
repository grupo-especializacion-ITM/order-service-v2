from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.domain.entities.order import Order, OrderStatus


class OrderRepositoryPort(ABC):
    """Port for order repository operations"""
    
    @abstractmethod
    async def save(self, order: Order) -> Order:
        """Save an order to the repository"""
        pass
    
    @abstractmethod
    async def find_by_id(self, order_id: UUID) -> Optional[Order]:
        """Find an order by its ID"""
        pass
    
    @abstractmethod
    async def find_by_customer_id(self, customer_id: UUID) -> List[Order]:
        """Find all orders for a customer"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Find all orders with a specific status"""
        pass
    
    @abstractmethod
    async def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Find all orders within a date range, optionally filtered by status"""
        pass
    
    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Update an existing order"""
        pass
    
    @abstractmethod
    async def delete(self, order_id: UUID) -> None:
        """Delete an order"""
        pass