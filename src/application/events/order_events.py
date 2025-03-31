from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime


@dataclass
class Event:
    """Base event class"""
    event_id: UUID
    event_type: str
    timestamp: datetime
    version: str = "1.0"


@dataclass
class OrderCreatedEvent(Event):
    """Event emitted when an order is created"""
    order_id: UUID
    customer_id: UUID
    items: List[Dict[str, Any]]
    total_amount: float
    status: str
    
    @staticmethod
    def create(order_id: UUID, customer_id: UUID, items: List[Dict[str, Any]], 
              total_amount: float, status: str) -> "OrderCreatedEvent":
        from uuid import uuid4
        
        return OrderCreatedEvent(
            event_id=uuid4(),
            event_type="order.created",
            timestamp=datetime.now(),
            order_id=order_id,
            customer_id=customer_id,
            items=items,
            total_amount=total_amount,
            status=status
        )


@dataclass
class OrderConfirmedEvent(Event):
    """Event emitted when an order is confirmed"""
    order_id: UUID
    customer_id: UUID
    total_amount: float
    
    @staticmethod
    def create(order_id: UUID, customer_id: UUID, total_amount: float) -> "OrderConfirmedEvent":
        from uuid import uuid4
        
        return OrderConfirmedEvent(
            event_id=uuid4(),
            event_type="order.confirmed",
            timestamp=datetime.now(),
            order_id=order_id,
            customer_id=customer_id,
            total_amount=total_amount
        )


@dataclass
class OrderCancelledEvent(Event):
    """Event emitted when an order is cancelled"""
    order_id: UUID
    customer_id: UUID
    reason: Optional[str] = None
    
    @staticmethod
    def create(order_id: UUID, customer_id: UUID, reason: Optional[str] = None) -> "OrderCancelledEvent":
        from uuid import uuid4
        
        return OrderCancelledEvent(
            event_id=uuid4(),
            event_type="order.cancelled",
            timestamp=datetime.now(),
            order_id=order_id,
            customer_id=customer_id,
            reason=reason
        )


@dataclass
class OrderStatusUpdatedEvent(Event):
    """Event emitted when an order status is updated"""
    order_id: UUID
    customer_id: UUID
    previous_status: str
    new_status: str
    
    @staticmethod
    def create(order_id: UUID, customer_id: UUID, 
              previous_status: str, new_status: str) -> "OrderStatusUpdatedEvent":
        from uuid import uuid4
        
        return OrderStatusUpdatedEvent(
            event_id=uuid4(),
            event_type="order.status_updated",
            timestamp=datetime.now(),
            order_id=order_id,
            customer_id=customer_id,
            previous_status=previous_status,
            new_status=new_status
        )