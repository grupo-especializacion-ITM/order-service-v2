from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.domain.ports.input.order_query_port import OrderQueryPort
from src.domain.ports.output.order_repository_port import OrderRepositoryPort
from src.domain.entities.order import Order, OrderStatus
from src.domain.exceptions.domain_exceptions import OrderNotFoundException


class OrderQueryService(OrderQueryPort):
    def __init__(self, order_repository: OrderRepositoryPort):
        self.order_repository = order_repository
    
    async def get_order_by_id(self, order_id: UUID) -> Order:
        """Get an order by its ID"""
        order = await self.order_repository.find_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Order with ID {order_id} not found")
        
        return order
    
    async def get_orders_by_customer_id(self, customer_id: UUID) -> List[Order]:
        """Get all orders from a customer"""
        return await self.order_repository.find_by_customer_id(customer_id)
    
    async def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get all orders with a specific status"""
        return await self.order_repository.find_by_status(status)
    
    async def get_orders_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get all orders within a date range, optionally filtered by status"""
        return await self.order_repository.find_by_date_range(start_date, end_date, status)