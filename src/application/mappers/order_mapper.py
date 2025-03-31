from typing import List, Optional
from uuid import UUID

from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.entities.customer import Customer
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.value_objects.order_total import OrderTotal
from src.application.dtos.order_dto import OrderDTO, DeliveryAddressDTO, OrderTotalDTO
from src.application.dtos.order_item_dto import OrderItemDTO
from src.application.dtos.customer_dto import CustomerDTO


class OrderMapper:
    @staticmethod
    def to_entity(order_dto: OrderDTO) -> Order:
        """
        Map OrderDTO to Order entity
        """
        # Map items
        items = []
        if order_dto.items:
            for item_dict in order_dto.items:
                item = OrderItem(
                    id=item_dict.get("id") or UUID(item_dict.get("id")) if item_dict.get("id") else None,
                    product_id=UUID(item_dict.get("product_id")),
                    name=item_dict.get("name"),
                    quantity=item_dict.get("quantity"),
                    unit_price=item_dict.get("unit_price"),
                    total_price=item_dict.get("total_price", item_dict.get("quantity", 0) * item_dict.get("unit_price", 0)),
                    notes=item_dict.get("notes"),
                    created_at=item_dict.get("created_at")
                )
                items.append(item)
        
        # Map delivery address
        delivery_address = None
        if order_dto.delivery_address:
            delivery_address = DeliveryAddress(
                street=order_dto.delivery_address.street,
                city=order_dto.delivery_address.city,
                state=order_dto.delivery_address.state,
                postal_code=order_dto.delivery_address.postal_code,
                country=order_dto.delivery_address.country,
                apartment=order_dto.delivery_address.apartment,
                instructions=order_dto.delivery_address.instructions
            )
        
        # Map total
        total = OrderTotal(
            subtotal=order_dto.total.subtotal if order_dto.total else 0,
            tax=order_dto.total.tax if order_dto.total else 0,
            total=order_dto.total.total if order_dto.total else 0
        ) if order_dto.total else None
        
        # Create order
        return Order(
            id=order_dto.id if order_dto.id else UUID(),
            customer_id=order_dto.customer_id,
            items=items,
            status=OrderStatus(order_dto.status) if order_dto.status else OrderStatus.CREATED,
            delivery_address=delivery_address,
            total=total,
            notes=order_dto.notes,
            created_at=order_dto.created_at,
            updated_at=order_dto.updated_at
        )
    
    @staticmethod
    def to_dto(order: Order) -> OrderDTO:
        """
        Map Order entity to OrderDTO
        """
        # Map items
        items = []
        for item in order.items:
            item_dict = {
                "id": str(item.id),
                "product_id": str(item.product_id),
                "name": item.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "notes": item.notes,
                "created_at": item.created_at.isoformat() if item.created_at else None
            }
            items.append(item_dict)
        
        # Map delivery address
        delivery_address = None
        if order.delivery_address:
            delivery_address = DeliveryAddressDTO(
                street=order.delivery_address.street,
                city=order.delivery_address.city,
                state=order.delivery_address.state,
                postal_code=order.delivery_address.postal_code,
                country=order.delivery_address.country,
                apartment=order.delivery_address.apartment,
                instructions=order.delivery_address.instructions
            )
        
        # Map total
        total = OrderTotalDTO(
            subtotal=order.total.subtotal,
            tax=order.total.tax,
            total=order.total.total
        ) if order.total else None
        
        # Create DTO
        return OrderDTO(
            id=order.id,
            customer_id=order.customer_id,
            items=items,
            status=order.status.value,
            delivery_address=delivery_address,
            total=total,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    
    @staticmethod
    def customer_to_dto(customer: Customer) -> CustomerDTO:
        """
        Map Customer entity to CustomerDTO
        """
        return CustomerDTO(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            created_at=customer.created_at,
            updated_at=customer.updated_at
        )
    
    @staticmethod
    def customer_to_entity(customer_dto: CustomerDTO) -> Customer:
        """
        Map CustomerDTO to Customer entity
        """
        return Customer(
            id=customer_dto.id if customer_dto.id else UUID(),
            name=customer_dto.name,
            email=customer_dto.email,
            phone=customer_dto.phone,
            created_at=customer_dto.created_at if customer_dto.created_at else None,
            updated_at=customer_dto.updated_at
        )
    
    @staticmethod
    def order_item_to_dto(order_item: OrderItem) -> OrderItemDTO:
        """
        Map OrderItem entity to OrderItemDTO
        """
        return OrderItemDTO(
            id=order_item.id,
            product_id=order_item.product_id,
            name=order_item.name,
            quantity=order_item.quantity,
            unit_price=order_item.unit_price,
            total_price=order_item.total_price,
            notes=order_item.notes,
            created_at=order_item.created_at
        )
    
    @staticmethod
    def order_item_to_entity(order_item_dto: OrderItemDTO) -> OrderItem:
        """
        Map OrderItemDTO to OrderItem entity
        """
        return OrderItem(
            id=order_item_dto.id if order_item_dto.id else UUID(),
            product_id=order_item_dto.product_id,
            name=order_item_dto.name,
            quantity=order_item_dto.quantity,
            unit_price=order_item_dto.unit_price,
            total_price=order_item_dto.total_price if order_item_dto.total_price else (order_item_dto.quantity * order_item_dto.unit_price),
            notes=order_item_dto.notes,
            created_at=order_item_dto.created_at if order_item_dto.created_at else None
        )