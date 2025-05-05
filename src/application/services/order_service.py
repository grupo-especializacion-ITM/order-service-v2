from typing import List, Optional, Dict
from uuid import UUID

from src.domain.ports.input.order_service_port import OrderServicePort
from src.domain.ports.output.order_repository_port import OrderRepositoryPort
from src.domain.ports.output.inventory_service_port import InventoryServicePort
from src.domain.ports.output.event_publisher_port import EventPublisherPort
from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.exceptions.domain_exceptions import (
    OrderNotFoundException, 
    InvalidOrderStateException,
    InventoryValidationException,
    OrderCreationException
)
from src.application.events.order_events import (
    OrderCreatedEvent,
    OrderConfirmedEvent,
    OrderCancelledEvent,
    OrderStatusUpdatedEvent
)


class OrderService(OrderServicePort):
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        inventory_service: InventoryServicePort,
        event_publisher: EventPublisherPort
    ):
        self.order_repository = order_repository
        self.inventory_service = inventory_service
        self.event_publisher = event_publisher
    
    async def create_order(
        self,
        customer_id: UUID,
        items: List[OrderItem],
        delivery_address: DeliveryAddress,
        notes: Optional[str] = None
    ) -> Order:
        """Create a new order"""
        # Validate items availability
        if not items:
            raise OrderCreationException("Cannot create an order without items")
        
        availability = await self.inventory_service.validate_items_availability(items)
        
        # Check if all items are available
        unavailable_items = [str(item_id) for item_id, is_available in availability.items() if not is_available]
        if unavailable_items:
            raise InventoryValidationException(
                f"Some items are not available",
                {"unavailable_items": unavailable_items}
            )
        
        # Create the order
        order = Order.create(
            customer_id=customer_id,
            items=items,
            delivery_address=delivery_address,
            notes=notes
        )
        
        # Save the order
        saved_order = await self.order_repository.save(order)
        
        # Publish order created event
        items_data = [
            {
                "id": str(item.id),
                "product_id": str(item.product_id),
                "name": item.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            }
            for item in saved_order.items
        ]
        
        order_created_event = OrderCreatedEvent.create(
            order_id=str(saved_order.id),
            customer_id=str(saved_order.customer_id),
            items=items_data,
            total_amount=saved_order.total.total,
            status=saved_order.status.value
        )
        
        await self.event_publisher.publish_event(
            event_type=order_created_event.event_type,
            payload=order_created_event.__dict__
        )
        
        return saved_order
    
    async def add_item_to_order(self, order_id: UUID, item: OrderItem) -> Order:
        """Add an item to an order"""
        # Find the order
        order = await self.order_repository.find_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Order with ID {order_id} not found")
        
        # Check if order is in a valid state for modification
        if order.status != OrderStatus.CREATED and order.status != OrderStatus.PENDING:
            raise InvalidOrderStateException(
                f"Cannot add items to an order with status {order.status.value}"
            )
        
        # Validate item availability
        availability = await self.inventory_service.validate_items_availability([item])
        if not availability.get(item.product_id, False):
            raise InventoryValidationException(
                f"Item {item.name} is not available",
                {"unavailable_item": str(item.product_id)}
            )
        
        # Add the item
        order.add_item(item)
        
        # Update the order
        updated_order = await self.order_repository.update(order)
        
        return updated_order
    
    async def remove_item_from_order(self, order_id: UUID, item_id: UUID) -> Order:
        """Remove an item from an order"""
        # Find the order
        order = await self.order_repository.find_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Order with ID {order_id} not found")
        
        # Check if order is in a valid state for modification
        if order.status != OrderStatus.CREATED and order.status != OrderStatus.PENDING:
            raise InvalidOrderStateException(
                f"Cannot remove items from an order with status {order.status.value}"
            )
        
        # Remove the item
        order.remove_item(item_id)
        
        # Update the order
        updated_order = await self.order_repository.update(order)
        
        return updated_order
    
    async def update_order_status(self, order_id: UUID, status: OrderStatus) -> Order:
        """Update the status of an order"""
        # Find the order
        order = await self.order_repository.find_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Order with ID {order_id} not found")
        
        # Track previous status for the event
        previous_status = order.status.value
        
        # Update the status
        order.update_status(status)
        
        # Update the order
        updated_order = await self.order_repository.update(order)
        
        # Publish status updated event
        status_updated_event = OrderStatusUpdatedEvent.create(
            order_id=str(updated_order.id),
            customer_id=str(updated_order.customer_id),
            previous_status=previous_status,
            new_status=updated_order.status.value
        )
        
        await self.event_publisher.publish_event(
            event_type=status_updated_event.event_type,
            payload=status_updated_event.__dict__
        )
        
        return updated_order
    
    async def cancel_order(self, order_id: UUID) -> Order:
        """Cancel an order"""
        # Find the order
        order = await self.order_repository.find_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Order with ID {order_id} not found")
        
        # Track previous status for the event
        previous_status = order.status.value
        
        # Cancel the order
        order.cancel()
        
        # Update the order
        updated_order = await self.order_repository.update(order)
        
        # Publish cancelled event
        cancelled_event = OrderCancelledEvent.create(
            order_id=str(updated_order.id),
            customer_id=str(updated_order.customer_id)
        )
        
        await self.event_publisher.publish_event(
            event_type=cancelled_event.event_type,
            payload=cancelled_event.__dict__
        )
        
        return updated_order
    
    async def confirm_order(self, order_id: UUID) -> Order:
        """Confirm an order"""
        # Find the order
        order = await self.order_repository.find_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Order with ID {order_id} not found")
        
        # Validate items availability again
        availability = await self.inventory_service.validate_items_availability(order.items)
        
        # Check if all items are available
        unavailable_items = [str(item_id) for item_id, is_available in availability.items() if not is_available]
        if unavailable_items:
            raise InventoryValidationException(
                f"Some items are not available",
                {"unavailable_items": unavailable_items}
            )
        
        # Track previous status for the event
        previous_status = order.status.value
        
        # Set status to CONFIRMED
        order.update_status(OrderStatus.CONFIRMED)
        
        # Update the order
        updated_order = await self.order_repository.update(order)
        
        # Publish events
        status_updated_event = OrderStatusUpdatedEvent.create(
            order_id=str(updated_order.id),
            customer_id=str(updated_order.customer_id),
            previous_status=previous_status,
            new_status=updated_order.status.value
        )
        
        confirmed_event = OrderConfirmedEvent.create(
            order_id=str(updated_order.id),
            customer_id=str(updated_order.customer_id),
            total_amount=updated_order.total.total
        )
        
        await self.event_publisher.publish_event(
            event_type=status_updated_event.event_type,
            payload=status_updated_event.__dict__
        )
        
        await self.event_publisher.publish_event(
            event_type=confirmed_event.event_type,
            payload=confirmed_event.__dict__
        )
        
        return updated_order

