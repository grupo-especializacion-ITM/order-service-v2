from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.ports.input.order_service_port import OrderServicePort
from src.domain.ports.input.order_query_port import OrderQueryPort
from src.domain.entities.order import OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.exceptions.domain_exceptions import (
    DomainException,
    OrderNotFoundException,
    InventoryValidationException
)
from src.application.services.order_service import OrderService
from src.application.services.order_query_service import OrderQueryService
from src.application.mappers.order_mapper import OrderMapper
from src.infrastructure.adapters.output.repositories.order_repository import OrderRepository
from src.infrastructure.adapters.output.services.inventory_service import InventoryService
#from src.infrastructure.adapters.output.messaging.kafka_event_publisher import KafkaEventPublisher
from src.infrastructure.db.session import get_db_session


class OrderController:
    """Controller for order-related API endpoints"""
    
    @staticmethod
    async def get_order_service(session: AsyncSession = Depends(get_db_session)) -> OrderServicePort:
        """Dependency for getting the order service"""
        order_repository = OrderRepository(session)
        inventory_service = InventoryService()
        #event_publisher = KafkaEventPublisher()
        
        return OrderService(
            order_repository=order_repository,
            inventory_service=inventory_service,
            #event_publisher=event_publisher
        )
    
    @staticmethod
    async def get_order_query_service(session: AsyncSession = Depends(get_db_session)) -> OrderQueryPort:
        """Dependency for getting the order query service"""
        order_repository = OrderRepository(session)
        
        return OrderQueryService(order_repository)
    
    @staticmethod
    async def create_order(
        order_data: Dict[str, Any],
        order_service: OrderServicePort = Depends(get_order_service)
    ) -> Dict[str, Any]:
        """Create a new order"""
        try:
            # Extract customer ID
            customer_id = order_data.get("customer_id")
            
            # Extract and create delivery address
            delivery_address_data = order_data.get("delivery_address")
            delivery_address = None
            if delivery_address_data:
                delivery_address = DeliveryAddress(
                    street=delivery_address_data.get("street"),
                    city=delivery_address_data.get("city"),
                    state=delivery_address_data.get("state"),
                    postal_code=delivery_address_data.get("postal_code"),
                    country=delivery_address_data.get("country"),
                    apartment=delivery_address_data.get("apartment"),
                    instructions=delivery_address_data.get("instructions")
                )
            
            # Extract and create order items
            items_data = order_data.get("items", [])
            items = []
            for item_data in items_data:
                item = OrderItem.create(
                    product_id=item_data.get("product_id"),
                    name=item_data.get("name"),
                    quantity=item_data.get("quantity"),
                    unit_price=item_data.get("unit_price"),
                    notes=item_data.get("notes")
                )
                items.append(item)
            
            # Create the order
            order = await order_service.create_order(
                customer_id=customer_id,
                items=items,
                delivery_address=delivery_address,
                notes=order_data.get("notes")
            )
            
            # Convert to DTO for response
            return OrderMapper.to_dto(order).__dict__
            
        except InventoryValidationException as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": e.message, "details": e.details}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def get_order(
        order_id: UUID,
        order_query_service: OrderQueryPort = Depends(get_order_query_service)
    ) -> Dict[str, Any]:
        """Get an order by ID"""
        try:
            order = await order_query_service.get_order_by_id(order_id)
            return OrderMapper.to_dto(order).__dict__
            
        except OrderNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def get_customer_orders(
        customer_id: UUID,
        order_query_service: OrderQueryPort = Depends(get_order_query_service)
    ) -> List[Dict[str, Any]]:
        """Get all orders for a customer"""
        try:
            orders = await order_query_service.get_orders_by_customer_id(customer_id)
            return [OrderMapper.to_dto(order).__dict__ for order in orders]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def update_order_status(
        order_id: UUID,
        status_data: Dict[str, str],
        order_service: OrderServicePort = Depends(get_order_service)
    ) -> Dict[str, Any]:
        """Update the status of an order"""
        try:
            # Extract the new status
            status_str = status_data.get("status")
            if not status_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"message": "Status is required"}
                )
            
            try:
                order_status = OrderStatus(status_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"message": f"Invalid status: {status_str}"}
                )
            
            # Update the order status
            order = await order_service.update_order_status(order_id, order_status)
            
            return OrderMapper.to_dto(order).__dict__
            
        except OrderNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def confirm_order(
        order_id: UUID,
        order_service: OrderServicePort = Depends(get_order_service)
    ) -> Dict[str, Any]:
        """Confirm an order"""
        try:
            order = await order_service.confirm_order(order_id)
            return OrderMapper.to_dto(order).__dict__
            
        except OrderNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except InventoryValidationException as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": e.message, "details": e.details}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def cancel_order(
        order_id: UUID,
        order_service: OrderServicePort = Depends(get_order_service)
    ) -> Dict[str, Any]:
        """Cancel an order"""
        try:
            order = await order_service.cancel_order(order_id)
            return OrderMapper.to_dto(order).__dict__
            
        except OrderNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def add_order_item(
        order_id: UUID,
        item_data: Dict[str, Any],
        order_service: OrderServicePort = Depends(get_order_service)
    ) -> Dict[str, Any]:
        """Add an item to an order"""
        try:
            # Create the order item
            item = OrderItem.create(
                product_id=UUID(item_data.get("product_id")),
                name=item_data.get("name"),
                quantity=item_data.get("quantity"),
                unit_price=item_data.get("unit_price"),
                notes=item_data.get("notes")
            )
            
            # Add the item to the order
            order = await order_service.add_item_to_order(order_id, item)
            
            return OrderMapper.to_dto(order).__dict__
            
        except OrderNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except InventoryValidationException as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": e.message, "details": e.details}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )
    
    @staticmethod
    async def remove_order_item(
        order_id: UUID,
        item_id: UUID,
        order_service: OrderServicePort = Depends(get_order_service)
    ) -> Dict[str, Any]:
        """Remove an item from an order"""
        try:
            order = await order_service.remove_item_from_order(order_id, item_id)
            return OrderMapper.to_dto(order).__dict__
            
        except OrderNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message}
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": e.message, "details": e.details}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": f"An error occurred: {str(e)}"}
            )