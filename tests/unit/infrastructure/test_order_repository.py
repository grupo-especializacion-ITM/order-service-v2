import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, call

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.value_objects.order_total import OrderTotal
from src.infrastructure.db.models.order_model import OrderModel, OrderItemModel, CustomerModel
from src.infrastructure.adapters.output.repositories.order_repository import OrderRepository


@pytest.fixture
def order_id():
    return uuid.uuid4()


@pytest.fixture
def customer_id():
    return uuid.uuid4()


@pytest.fixture
def item_id():
    return uuid.uuid4()


@pytest.fixture
def product_id():
    return uuid.uuid4()


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.delete = AsyncMock()
    return session


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
def order_item(item_id, product_id):
    return OrderItem(
        id=item_id,
        product_id=product_id,
        name="Test Product",
        quantity=2,
        unit_price=10.0,
        total_price=20.0,
        notes="Test notes",
        created_at=datetime.now()
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
        notes="Test order notes",
        created_at=datetime.now()
    )


@pytest.fixture
def order_model(order_id, customer_id):
    return OrderModel(
        id=order_id,
        customer_id=customer_id,
        status=OrderStatus.CREATED.value,
        notes="Test order notes",
        created_at=datetime.now(),
        delivery_address={
            "street": "123 Main St",
            "city": "Test City",
            "state": "Test State",
            "postal_code": "12345",
            "country": "Test Country"
        },
        total={
            "subtotal": 20.0,
            "tax": 2.0,
            "total": 22.0
        }
    )


@pytest.fixture
def order_item_model(order_id, item_id, product_id):
    return OrderItemModel(
        id=item_id,
        order_id=order_id,
        product_id=product_id,
        name="Test Product",
        quantity=2,
        unit_price=10.0,
        total_price=20.0,
        notes="Test notes",
        created_at=datetime.now()
    )


@pytest.fixture
def order_repository(mock_session):
    return OrderRepository(mock_session)


@pytest.mark.asyncio
async def test_save_order(order_repository, mock_session, order):
    # Setup
    # Execute
    result = await order_repository.save(order)
    
    # Assert
    assert result == order
    mock_session.add.assert_called()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_id(order_repository, mock_session, order_model, order_item_model, order_id):
    
    # Setup
    order_model.items = [order_item_model]
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = order_model
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await order_repository.find_by_id(order_id)
    
    # Assert
    assert result is not None
    assert result.id == order_id
    assert len(result.items) == 1
    assert result.status == OrderStatus.CREATED
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_id_not_found(order_repository, mock_session, order_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await order_repository.find_by_id(order_id)
    
    # Assert
    assert result is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_customer_id(order_repository, mock_session, order_model, order_item_model, customer_id):
    # Setup
    order_model.items = [order_item_model]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [order_model]
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await order_repository.find_by_customer_id(customer_id)
    
    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0].customer_id == customer_id
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_status(order_repository, mock_session, order_model, order_item_model):
    # Setup
    order_model.items = [order_item_model]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [order_model]
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await order_repository.find_by_status(OrderStatus.CREATED)
    
    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0].status == OrderStatus.CREATED
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_date_range(order_repository, mock_session, order_model, order_item_model):
    # Setup
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=1)
    order_model.items = [order_item_model]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [order_model]
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await order_repository.find_by_date_range(start_date, end_date)
    
    # Assert
    assert result is not None
    assert len(result) == 1
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_date_range_with_status(order_repository, mock_session, order_model, order_item_model):
    # Setup
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=1)
    status = OrderStatus.CREATED
    order_model.items = [order_item_model]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [order_model]
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await order_repository.find_by_date_range(start_date, end_date, status)
    
    # Assert
    assert result is not None
    assert len(result) == 1
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update(order_repository, mock_session, order, order_model, order_item_model, order_id):
    # Setup
    order_model.items = [order_item_model]
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = order_model
    mock_session.execute.return_value = mock_result
    
    # Execute
    result = await order_repository.update(order)
    
    # Assert
    assert result == order
    assert mock_session.execute.call_count >= 1
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(order_repository, mock_session, order, order_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Execute and Assert
    with pytest.raises(ValueError):
        await order_repository.update(order)
    
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete(order_repository, mock_session, order_model, order_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = order_model
    mock_session.execute.return_value = mock_result
    
    # Execute
    await order_repository.delete(order_id)
    
    # Assert
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_order_not_found(order_repository, mock_session, order_id):
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result

    await order_repository.delete(order_id)

    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_not_found(order_repository, mock_session, order_id):
    # Setup
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Execute
    await order_repository.delete(order_id)
    
    # Assert
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_model_to_entity_conversion(order_repository, order_model, order_item_model):
    # Setup
    order_model.items = [order_item_model]
    
    # Execute
    result = order_repository._model_to_entity(order_model)
    
    # Assert
    assert result is not None
    assert result.id == order_model.id
    assert result.customer_id == order_model.customer_id
    assert result.status == OrderStatus(order_model.status)
    assert len(result.items) == 1
    assert result.items[0].id == order_item_model.id
    assert result.items[0].name == order_item_model.name
    assert result.delivery_address is not None
    assert result.delivery_address.street == "123 Main St"
    assert result.total is not None
    assert result.total.subtotal == 20.0
    assert result.total.tax == 2.0
    assert result.total.total == 22.0