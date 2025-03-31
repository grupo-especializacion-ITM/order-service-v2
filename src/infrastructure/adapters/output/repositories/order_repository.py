from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.ports.output.order_repository_port import OrderRepositoryPort
from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.entities.customer import Customer
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.value_objects.order_total import OrderTotal
from src.infrastructure.db.models.order_model import OrderModel, OrderItemModel, CustomerModel


class OrderRepository(OrderRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, order: Order) -> Order:
        """Save an order to the repository"""
        # Create order model instance
        order_model = OrderModel(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            delivery_address=self._delivery_address_to_dict(order.delivery_address) if order.delivery_address else None,
            total=self._order_total_to_dict(order.total)
        )
        
        # Add order model to session
        self.session.add(order_model)
        
        # Create order items
        for item in order.items:
            order_item_model = OrderItemModel(
                id=item.id,
                order_id=order.id,
                product_id=item.product_id,
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                notes=item.notes,
                created_at=item.created_at
            )
            self.session.add(order_item_model)
        
        # Commit changes
        await self.session.commit()
        
        # Return the saved order
        return order
    
    async def find_by_id(self, order_id: UUID) -> Optional[Order]:
        """Find an order by its ID"""
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == order_id)
        )
        
        result = await self.session.execute(query)
        order_model = result.scalars().first()
        
        if not order_model:
            return None
        
        return self._model_to_entity(order_model)
    
    async def find_by_customer_id(self, customer_id: UUID) -> List[Order]:
        """Find all orders for a customer"""
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.customer_id == customer_id)
        )
        
        result = await self.session.execute(query)
        order_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in order_models]
    
    async def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Find all orders with a specific status"""
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.status == status.value)
        )
        
        result = await self.session.execute(query)
        order_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in order_models]
    
    async def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Find all orders within a date range, optionally filtered by status"""
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.created_at >= start_date)
            .where(OrderModel.created_at <= end_date)
        )
        
        if status:
            query = query.where(OrderModel.status == status.value)
        
        result = await self.session.execute(query)
        order_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in order_models]
    
    async def update(self, order: Order) -> Order:
        """Update an existing order"""
        # Fetch the existing order
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == order.id)
        )
        
        result = await self.session.execute(query)
        order_model = result.scalars().first()
        
        if not order_model:
            raise ValueError(f"Order with ID {order.id} not found")
        
        # Update the order fields
        order_model.status = order.status.value
        order_model.notes = order.notes
        order_model.updated_at = order.updated_at if order.updated_at else datetime.now()
        order_model.delivery_address = self._delivery_address_to_dict(order.delivery_address) if order.delivery_address else None
        order_model.total = self._order_total_to_dict(order.total)
        
        # Track existing item IDs
        existing_item_ids = {item.id for item in order_model.items}
        updated_item_ids = {item.id for item in order.items}
        
        # Items to add (in updated but not in existing)
        items_to_add = [item for item in order.items if item.id not in existing_item_ids]
        
        # Items to remove (in existing but not in updated)
        items_to_remove = [item for item in order_model.items if item.id not in updated_item_ids]
        
        # Items to update (in both)
        items_to_update = [item for item in order.items if item.id in existing_item_ids]
        
        # Remove items
        for item in items_to_remove:
            await self.session.delete(item)
        
        # Add new items
        for item in items_to_add:
            order_item_model = OrderItemModel(
                id=item.id,
                order_id=order.id,
                product_id=item.product_id,
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                notes=item.notes,
                created_at=item.created_at
            )
            self.session.add(order_item_model)
        
        # Update existing items
        for item in items_to_update:
            query = select(OrderItemModel).where(OrderItemModel.id == item.id)
            result = await self.session.execute(query)
            item_model = result.scalars().first()
            
            if item_model:
                item_model.name = item.name
                item_model.quantity = item.quantity
                item_model.unit_price = item.unit_price
                item_model.total_price = item.total_price
                item_model.notes = item.notes
        
        # Commit changes
        await self.session.commit()
        
        # Return the updated order
        return order
    
    async def delete(self, order_id: UUID) -> None:
        """Delete an order"""
        query = select(OrderModel).where(OrderModel.id == order_id)
        result = await self.session.execute(query)
        order_model = result.scalars().first()
        
        if order_model:
            await self.session.delete(order_model)
            await self.session.commit()
    
    def _model_to_entity(self, order_model: OrderModel) -> Order:
        """Convert a DB model to a domain entity"""
        # Convert items
        items = []
        for item_model in order_model.items:
            item = OrderItem(
                id=item_model.id,
                product_id=item_model.product_id,
                name=item_model.name,
                quantity=item_model.quantity,
                unit_price=item_model.unit_price,
                total_price=item_model.total_price,
                notes=item_model.notes,
                created_at=item_model.created_at
            )
            items.append(item)
        
        # Convert delivery address
        delivery_address = None
        if order_model.delivery_address:
            delivery_address = DeliveryAddress(
                street=order_model.delivery_address.get("street", ""),
                city=order_model.delivery_address.get("city", ""),
                state=order_model.delivery_address.get("state", ""),
                postal_code=order_model.delivery_address.get("postal_code", ""),
                country=order_model.delivery_address.get("country", ""),
                apartment=order_model.delivery_address.get("apartment"),
                instructions=order_model.delivery_address.get("instructions")
            )
        
        # Convert total
        total = OrderTotal(
            subtotal=order_model.total.get("subtotal", 0),
            tax=order_model.total.get("tax", 0),
            total=order_model.total.get("total", 0)
        )
        
        # Create order entity
        return Order(
            id=order_model.id,
            customer_id=order_model.customer_id,
            items=items,
            status=OrderStatus(order_model.status),
            delivery_address=delivery_address,
            total=total,
            notes=order_model.notes,
            created_at=order_model.created_at,
            updated_at=order_model.updated_at
        )
    
    def _delivery_address_to_dict(self, address: DeliveryAddress) -> Dict[str, Any]:
        """Convert a delivery address value object to a dictionary"""
        return {
            "street": address.street,
            "city": address.city,
            "state": address.state,
            "postal_code": address.postal_code,
            "country": address.country,
            "apartment": address.apartment,
            "instructions": address.instructions
        }
    
    def _order_total_to_dict(self, total: OrderTotal) -> Dict[str, float]:
        """Convert an order total value object to a dictionary"""
        return {
            "subtotal": total.subtotal,
            "tax": total.tax,
            "total": total.total
        }