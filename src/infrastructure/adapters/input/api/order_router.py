from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Body, Path, Query, status

from src.domain.ports.input.order_service_port import OrderServicePort
from src.infrastructure.adapters.input.api.order_controller import OrderController
from src.infrastructure.adapters.input.api.schemas import (
    OrderSchema, 
    OrderListResponse, 
    OrderCreateSchema,
    OrderStatusUpdateSchema,
    OrderItemCreateSchema,
    ErrorResponse
)
from src.infrastructure.config.settings import get_settings

settings = get_settings()

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/orders",
    tags=["Orders"]
)


@router.post(
    "", 
    response_model=OrderSchema, 
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Order created successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad request"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def create_order(
    order_data: OrderCreateSchema = Body(...),
    order_service: OrderServicePort = Depends(OrderController.get_order_service),
):
    """
    Create a new order.
    
    - **customer_id**: UUID of the customer
    - **items**: List of order items (product_id, name, quantity, unit_price, notes)
    - **delivery_address**: Delivery address details
    - **notes**: Optional notes for the order
    """
    return await OrderController.create_order(order_data.dict(), order_service)


@router.get(
    "/{order_id}", 
    response_model=OrderSchema,
    responses={
        status.HTTP_200_OK: {"description": "Order details retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Order not found"}
    }
)
async def get_order(
    order_id: UUID = Path(..., description="The ID of the order to get"),
    order_service: OrderServicePort = Depends(OrderController.get_order_query_service),
):
    """
    Get an order by ID.
    
    - **order_id**: UUID of the order to retrieve
    """
    return await OrderController.get_order(order_id, order_service)


@router.get(
    "", 
    response_model=List[OrderSchema],
    responses={
        status.HTTP_200_OK: {"description": "List of orders retrieved successfully"}
    }
)
async def get_customer_orders(
    customer_id: UUID = Query(..., description="Customer ID to filter orders"),
    order_service: OrderServicePort = Depends(OrderController.get_order_query_service)
):
    """
    Get all orders for a customer.
    
    - **customer_id**: UUID of the customer
    """
    return await OrderController.get_customer_orders(customer_id, order_service)


@router.patch(
    "/{order_id}/status", 
    response_model=OrderSchema,
    responses={
        status.HTTP_200_OK: {"description": "Order status updated successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Invalid status transition"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Order not found"}
    }
)
async def update_order_status(
    order_id: UUID = Path(..., description="The ID of the order to update"),
    status_data: OrderStatusUpdateSchema = Body(...),
    order_service: OrderServicePort = Depends(OrderController.get_order_service)
):
    """
    Update the status of an order.
    
    - **order_id**: UUID of the order to update
    - **status**: New status for the order (CREATED, PENDING, CONFIRMED, PREPARING, READY, DELIVERED, CANCELLED)
    """
    return await OrderController.update_order_status(order_id, status_data.dict(), order_service)


@router.post(
    "/{order_id}/confirm", 
    response_model=OrderSchema,
    responses={
        status.HTTP_200_OK: {"description": "Order confirmed successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Cannot confirm order"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Order not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Inventory validation failed"}
    }
)
async def confirm_order(
    order_id: UUID = Path(..., description="The ID of the order to confirm"),
    order_service: OrderServicePort = Depends(OrderController.get_order_service)
):
    """
    Confirm an order.
    
    - **order_id**: UUID of the order to confirm
    """
    return await OrderController.confirm_order(order_id, order_service)


@router.post(
    "/{order_id}/cancel", 
    response_model=OrderSchema,
    responses={
        status.HTTP_200_OK: {"description": "Order cancelled successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Cannot cancel order"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Order not found"}
    }
)
async def cancel_order(
    order_id: UUID = Path(..., description="The ID of the order to cancel"),
    order_service: OrderServicePort = Depends(OrderController.get_order_service)
):
    """
    Cancel an order.
    
    - **order_id**: UUID of the order to cancel
    """
    return await OrderController.cancel_order(order_id, order_service)


@router.post(
    "/{order_id}/items", 
    response_model=OrderSchema,
    responses={
        status.HTTP_200_OK: {"description": "Item added successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Cannot add item"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Order not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse, "description": "Inventory validation failed"}
    }
)
async def add_order_item(
    order_id: UUID = Path(..., description="The ID of the order"),
    item_data: OrderItemCreateSchema = Body(...),
    order_service: OrderServicePort = Depends(OrderController.get_order_service)
):
    """
    Add an item to an order.
    
    - **order_id**: UUID of the order
    - **item_data**: Item details (product_id, name, quantity, unit_price, notes)
    """
    return await OrderController.add_order_item(order_id, item_data.dict(), order_service)


@router.delete(
    "/{order_id}/items/{item_id}", 
    response_model=OrderSchema,
    responses={
        status.HTTP_200_OK: {"description": "Item removed successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Cannot remove item"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Order or item not found"}
    }
)
async def remove_order_item(
    order_id: UUID = Path(..., description="The ID of the order"),
    item_id: UUID = Path(..., description="The ID of the item to remove"),
    order_service: OrderServicePort = Depends(OrderController.get_order_service)
):
    """
    Remove an item from an order.
    
    - **order_id**: UUID of the order
    - **item_id**: UUID of the item to remove
    """
    return await OrderController.remove_order_item(order_id, item_id, order_service)