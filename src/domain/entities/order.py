from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from enum import Enum

from src.domain.entities.order_item import OrderItem
from src.domain.entities.customer import Customer
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.value_objects.order_total import OrderTotal


class OrderStatus(Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    id: UUID
    customer_id: UUID
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.CREATED
    delivery_address: Optional[DeliveryAddress] = None
    total: OrderTotal = field(default_factory=lambda: OrderTotal(0, 0, 0))
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    @staticmethod
    def create(customer_id: UUID, items: List[OrderItem] = None, 
              delivery_address: Optional[DeliveryAddress] = None,
              notes: Optional[str] = None) -> "Order":
        items = items or []
        
        # Calculate subtotal
        subtotal = sum(item.total_price for item in items)
        
        # Apply taxes (example: 10%)
        tax = subtotal * 0.10
        
        # Calculate total
        total = OrderTotal(
            subtotal=subtotal,
            tax=tax,
            total=subtotal + tax
        )
        
        return Order(
            id=uuid4(),
            customer_id=customer_id,
            items=items,
            delivery_address=delivery_address,
            total=total,
            notes=notes
        )
    
    def add_item(self, item: OrderItem) -> None:
        """Add an item to the order and recalculate totals"""
        if self.status != OrderStatus.CREATED and self.status != OrderStatus.PENDING:
            raise ValueError("Cannot add items to an order that is not in CREATED or PENDING status")
        
        self.items.append(item)
        self._recalculate_total()
    
    def remove_item(self, item_id: UUID) -> None:
        """Remove an item from the order and recalculate totals"""
        if self.status != OrderStatus.CREATED and self.status != OrderStatus.PENDING:
            raise ValueError("Cannot remove items from an order that is not in CREATED or PENDING status")
        
        self.items = [item for item in self.items if item.id != item_id]
        self._recalculate_total()
    
    def update_status(self, status: OrderStatus) -> None:
        """Update the order status"""
        self.status = status
        self.updated_at = datetime.now()
    
    def cancel(self) -> None:
        """Cancel the order"""
        if self.status == OrderStatus.DELIVERED:
            raise ValueError("Cannot cancel an order that has already been delivered")
        
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def _recalculate_total(self) -> None:
        """Recalculate the order total"""
        subtotal = sum(item.total_price for item in self.items)
        tax = subtotal * 0.10  # Example tax rate: 10%
        
        self.total = OrderTotal(
            subtotal=subtotal,
            tax=tax,
            total=subtotal + tax
        )