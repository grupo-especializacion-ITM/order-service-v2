# tests/unit/application/test_order_query_service.py
import uuid
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.value_objects.order_total import OrderTotal
from src.domain.exceptions.domain_exceptions import OrderNotFoundException
from src.application.services.order_query_service import OrderQueryService


# Fixtures
@pytest.fixture
def order_id():
    return uuid.uuid4()


@pytest.fixture
def customer_id():
    return uuid.uuid4()


@pytest.fixture
def order_item():
    return OrderItem(
        id=uuid.uuid4(),
        product_id=uuid.uuid4(),
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
        status=OrderStatus.CONFIRMED,
        delivery_address=delivery_address,
        total=OrderTotal(subtotal=20.0, tax=2.0, total=22.0),
        created_at=datetime.now()
    )


@pytest.fixture
def order_list(customer_id, order_item, delivery_address):
    return [
        Order(
            id=uuid.uuid4(),
            customer_id=customer_id,
            items=[order_item],
            status=OrderStatus.CREATED,
            delivery_address=delivery_address,
            total=OrderTotal(subtotal=20.0, tax=2.0, total=22.0),
            created_at=datetime.now() - timedelta(days=1)
        ),
        Order(
            id=uuid.uuid4(),
            customer_id=customer_id,
            items=[order_item],
            status=OrderStatus.CONFIRMED,
            delivery_address=delivery_address,
            total=OrderTotal(subtotal=20.0, tax=2.0, total=22.0),
            created_at=datetime.now()
        )
    ]


@pytest.fixture
def order_repository():
    repository = AsyncMock()
    repository.find_by_id = AsyncMock()
    repository.find_by_customer_id = AsyncMock()
    repository.find_by_status = AsyncMock()
    repository.find_by_date_range = AsyncMock()
    return repository


@pytest.fixture
def order_query_service(order_repository):
    return OrderQueryService(order_repository=order_repository)


# Tests
@pytest.mark.asyncio
async def test_get_order_by_id_success(
    order_query_service, order, order_id, order_repository
):
    # Setup

    order_repository.find_by_id.return_value = order
    
    # Execute
    result = await order_query_service.get_order_by_id(order_id)
    
    # Assert
    assert result is not None
    assert result.id == order_id
    assert result.status == OrderStatus.CONFIRMED
    
    # Verify interactions
    order_repository.find_by_id.assert_called_once_with(order_id)


@pytest.mark.asyncio
async def test_get_orders_by_date_range_with_status(
    order_query_service, order_list, order_repository
):
    # Setup
    start_date = datetime.now() - timedelta(days=2)
    end_date = datetime.now()
    status = OrderStatus.CONFIRMED
    filtered_orders = [order for order in order_list if order.status == status]
    order_repository.find_by_date_range.return_value = filtered_orders
    
    # Execute
    result = await order_query_service.get_orders_by_date_range(start_date, end_date, status)
    
    # Assert
    assert result is not None
    assert len(result) == len(filtered_orders)
    assert all(order.status == status for order in result)
    
    # Verify interactions
    order_repository.find_by_date_range.assert_called_once_with(start_date, end_date, status)


@pytest.mark.asyncio
async def test_get_orders_by_date_range_empty(
    order_query_service, order_repository
):
    # Setup
    start_date = datetime.now() - timedelta(days=2)
    end_date = datetime.now()
    order_repository.find_by_date_range.return_value = []
    
    # Execute
    result = await order_query_service.get_orders_by_date_range(start_date, end_date)
    
    # Assert
    assert result is not None
    assert len(result) == 0
    
    # Verify interactions
    order_repository.find_by_date_range.assert_called_once_with(start_date, end_date, None)


@pytest.mark.asyncio
async def test_get_order_by_id_not_found(
    order_query_service, order_id, order_repository
):
    # Setup
    order_repository.find_by_id.return_value = None
    
    # Execute and Assert
    with pytest.raises(OrderNotFoundException):
        await order_query_service.get_order_by_id(order_id)
    
    # Verify interactions
    order_repository.find_by_id.assert_called_once_with(order_id)


@pytest.mark.asyncio
async def test_get_orders_by_customer_id(
    order_query_service, customer_id, order_list, order_repository
):
    # Setup
    order_repository.find_by_customer_id.return_value = order_list
    
    # Execute
    result = await order_query_service.get_orders_by_customer_id(customer_id)
    
    # Assert
    assert result is not None
    assert len(result) == 2
    assert all(order.customer_id == customer_id for order in result)
    
    # Verify interactions
    order_repository.find_by_customer_id.assert_called_once_with(customer_id)


@pytest.mark.asyncio
async def test_get_orders_by_customer_id_empty(
    order_query_service, customer_id, order_repository
):
    # Setup
    order_repository.find_by_customer_id.return_value = []
    
    # Execute
    result = await order_query_service.get_orders_by_customer_id(customer_id)
    
    # Assert
    assert result is not None
    assert len(result) == 0
    
    # Verify interactions
    order_repository.find_by_customer_id.assert_called_once_with(customer_id)


@pytest.mark.asyncio
async def test_get_orders_by_status(
    order_query_service, order_list, order_repository
):
    # Setup
    status = OrderStatus.CONFIRMED
    filtered_orders = [order for order in order_list if order.status == status]
    order_repository.find_by_status.return_value = filtered_orders
    
    # Execute
    result = await order_query_service.get_orders_by_status(status)
    
    # Assert
    assert result is not None
    assert len(result) == len(filtered_orders)
    assert all(order.status == status for order in result)
    
    # Verify interactions
    order_repository.find_by_status.assert_called_once_with(status)


@pytest.mark.asyncio
async def test_get_orders_by_date_range(
    order_query_service, order_list, order_repository
):
    # Setup
    start_date = datetime.now() - timedelta(days=2)
    end_date = datetime.now()
    order_repository.find_by_date_range.return_value = order_list
    
    # Execute
    result = await order_query_service.get_orders_by_date_range(start_date, end_date)
    
    # Assert
    assert result is not None
    assert len(result) == 2
    
    # Verify interactions
    order_repository