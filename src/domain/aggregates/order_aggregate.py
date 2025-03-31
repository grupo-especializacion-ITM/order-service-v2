from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.entities.customer import Customer
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.value_objects.order_total import OrderTotal


@dataclass
class OrderAggregate:
    order: Order
    customer: Customer
    
    @classmethod
    def create_new_order(
        cls,
        customer: Customer,
        items: List[OrderItem],
        delivery_address: Optional[DeliveryAddress] = None,
        notes: Optional[str] = None
    ) -> "OrderAggregate":
        """Create a new order aggregate"""
        order = Order.create(
            customer_id=customer.id,
            items=items,
            delivery_address=delivery_address,
            notes=notes
        )
        
        return cls(order=order, customer=customer)
    
    def confirm_order(self) -> None:
        """Confirm the order"""
        if not self.order.items:
            raise ValueError("Cannot confirm an order without items")
        
        if not self.order.delivery_address:
            raise ValueError("Cannot confirm an order without a delivery address")
        
        self.order.update_status(OrderStatus.CONFIRMED)
    
    def cancel_order(self) -> None:
        """Cancel the order"""
        self.order.cancel()
    
    def update_order_status(self, status: OrderStatus) -> None:
        """Update the order status"""
        self.order.update_status(status)
    
    def add_item(self, item: OrderItem) -> None:
        """Add an item to the order"""
        self.order.add_item(item)
    
    def remove_item(self, item_id: UUID) -> None:
        """Remove an item from the order"""
        self.order.remove_item(item_id)
    
    def get_total(self) -> OrderTotal:
        """Get the order total"""
        return self.order.total