from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.domain.entities.order import Order, OrderStatus


class OrderQueryPort(ABC):
    """Port for querying orders"""
    
    @abstractmethod
    async def get_order_by_id(self, order_id: UUID) -> Order:
        """Get an order by its ID"""
        pass
    
    @abstractmethod
    async def get_orders_by_customer_id(self, customer_id: UUID) -> List[Order]:
        """Get all orders from a customer"""
        pass
    
    @abstractmethod
    async def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get all orders with a specific status"""
        pass
    
    @abstractmethod
    async def get_orders_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get all orders within a date range, optionally filtered by status"""
        pass
