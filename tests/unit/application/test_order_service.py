# tests/unit/application/test_order_service.py
import uuid
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.entities.customer import Customer
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.value_objects.order_total import OrderTotal
from src.domain.exceptions.domain_exceptions import (
    OrderNotFoundException,
    InventoryValidationException,
    InvalidOrderStateException
)
from src.application.services.order_service import OrderService


# Fixtures
@pytest.fixture
def order_id():
    return uuid.uuid4()


@pytest.fixture
def customer_id():
    return uuid.uuid4()


@pytest.fixture
def product_id():
    return uuid.uuid4()


@pytest.fixture
def order_item(product_id):
    return OrderItem(
        id=uuid.uuid4(),
        product_id=product_id,
        name="Test Product",
        quantity=2,
        unit_price=10.0,
        total_price=20.0,
        created_at=datetime.now()
    )


@pytest.fixture
def delivery_address():
    return DeliveryAddress(
        street="123 Main St",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Test Country"
    )


@pytest.fixture
def order(order_id, customer_id, order_item, delivery_address):
    return Order(
        id=order_id,
        customer_id=customer_id,
        items=[order_item],
        status=OrderStatus.CREATED,
        delivery_address=delivery_address,
        total=OrderTotal(subtotal=20.0, tax=2.0, total=22.0),
        created_at=datetime.now()
    )


@pytest.fixture
def order_repository():
    repository = AsyncMock()
    repository.save = AsyncMock()
    repository.find_by_id = AsyncMock()
    repository.update = AsyncMock()
    return repository


@pytest.fixture
def inventory_service():
    service = AsyncMock()
    service.validate_items_availability = AsyncMock()
    return service


@pytest.fixture
def event_publisher():
    publisher = AsyncMock()
    publisher.publish_event = AsyncMock()
    return publisher


@pytest.fixture
def order_service(order_repository, inventory_service):#, event_publisher
    return OrderService(
        order_repository=order_repository,
        inventory_service=inventory_service,
        #event_publisher=event_publisher
    )


# Tests
@pytest.mark.asyncio
async def test_create_order_success(# event_publisher
    order_service, customer_id, order_item, delivery_address,
    order_repository, inventory_service,
):
    # Setup
    items = [order_item]
    inventory_service.validate_items_availability.return_value = {order_item.product_id: True}
    order_repository.save.return_value = Order(
        id=uuid.uuid4(),
        customer_id=customer_id,
        items=items,
        status=OrderStatus.CREATED,
        delivery_address=delivery_address,
        total=OrderTotal(subtotal=20.0, tax=2.0, total=22.0),
        created_at=datetime.now()
    )
    
    # Execute
    result = await order_service.create_order(
        customer_id=customer_id,
        items=items,
        delivery_address=delivery_address
    )
    
    # Assert
    assert result is not None
    assert result.customer_id == customer_id
    assert len(result.items) == 1
    assert result.items[0].id == order_item.id
    assert result.status == OrderStatus.CREATED
    
    # Verify interactions
    inventory_service.validate_items_availability.assert_called_once_with(items)
    order_repository.save.assert_called_once()
    #event_publisher.publish_event.assert_called_once()


@pytest.mark.asyncio
async def test_create_order_inventory_unavailable(
    order_service, customer_id, order_item, delivery_address,
    inventory_service
):
    # Setup
    items = [order_item]
    inventory_service.validate_items_availability.return_value = {order_item.product_id: False}
    
    # Execute and Assert
    with pytest.raises(InventoryValidationException):
        await order_service.create_order(
            customer_id=customer_id,
            items=items,
            delivery_address=delivery_address
        )
    
    # Verify interactions
    inventory_service.validate_items_availability.assert_called_once_with(items)


@pytest.mark.asyncio
async def test_confirm_order_success(#, event_publisher
    order_service, order, order_id,
    order_repository, inventory_service
):
    # Setup
    order_repository.find_by_id.return_value = order
    inventory_service.validate_items_availability.return_value = {order.items[0].product_id: True}
    order_repository.update.return_value = Order(
        id=order.id,
        customer_id=order.customer_id,
        items=order.items,
        status=OrderStatus.CONFIRMED,
        delivery_address=order.delivery_address,
        total=order.total,
        created_at=order.created_at,
        updated_at=datetime.now()
    )
    
    # Execute
    result = await order_service.confirm_order(order_id)
    
    # Assert
    assert result is not None
    assert result.id == order_id
    assert result.status == OrderStatus.CONFIRMED
    
    # Verify interactions
    order_repository.find_by_id.assert_called_once_with(order_id)
    inventory_service.validate_items_availability.assert_called_once_with(order.items)
    order_repository.update.assert_called_once()
    #assert event_publisher.publish_event.call_count == 2  # Two events: status updated and order confirmed


@pytest.mark.asyncio
async def test_confirm_order_not_found(
    order_service, order_id, order_repository
):
    # Setup
    order_repository.find_by_id.return_value = None
    
    # Execute and Assert
    with pytest.raises(OrderNotFoundException):
        await order_service.confirm_order(order_id)
    
    # Verify interactions
    order_repository.find_by_id.assert_called_once_with(order_id)


@pytest.mark.asyncio
async def test_cancel_order_success(#, event_publisher
    order_service, order, order_id,
    order_repository
):
    # Setup
    order_repository.find_by_id.return_value = order
    cancelled_order = Order(
        id=order.id,
        customer_id=order.customer_id,
        items=order.items,
        status=OrderStatus.CANCELLED,
        delivery_address=order.delivery_address,
        total=order.total,
        created_at=order.created_at,
        updated_at=datetime.now()
    )
    order_repository.update.return_value = cancelled_order
    
    # Execute
    result = await order_service.cancel_order(order_id)
    
    # Assert
    assert result is not None
    assert result.id == order_id
    assert result.status == OrderStatus.CANCELLED
    
    # Verify interactions
    order_repository.find_by_id.assert_called_once_with(order_id)
    order_repository.update.assert_called_once()
    #event_publisher.publish_event.assert_called_once()