# Tests for OrderTotal value object
import pytest
from src.domain.value_objects.delivery_address import DeliveryAddress
from src.domain.value_objects.order_total import OrderTotal


def test_order_total_create():
    """Test creating an order total"""
    total = OrderTotal(subtotal=100.0, tax=10.0, total=110.0)
    assert total.subtotal == 100.0
    assert total.tax == 10.0
    assert total.total == 110.0


def test_order_total_str_representation():
    """Test string representation of order total"""
    total = OrderTotal(subtotal=100.0, tax=10.0, total=110.0)
    str_repr = str(total)
    assert "Total: $110.00" in str_repr
    assert "Subtotal: $100.00" in str_repr
    assert "Tax: $10.00" in str_repr


def test_order_total_immutability():
    """Test that order total is immutable"""
    total = OrderTotal(subtotal=100.0, tax=10.0, total=110.0)
    with pytest.raises(Exception):  # Either AttributeError or dataclasses.FrozenInstanceError
        total.subtotal = 200.0


# Tests for DeliveryAddress value object
def test_delivery_address_create():
    """Test creating a delivery address"""
    address = DeliveryAddress(
        street="123 Main St",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Test Country"
    )
    
    assert address.street == "123 Main St"
    assert address.city == "Test City"
    assert address.state == "Test State"
    assert address.postal_code == "12345"
    assert address.country == "Test Country"
    assert address.apartment is None
    assert address.instructions is None


def test_delivery_address_create_with_optional_fields():
    """Test creating a delivery address with optional fields"""
    address = DeliveryAddress(
        street="123 Main St",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Test Country",
        apartment="Apt 4B",
        instructions="Leave at front door"
    )
    
    assert address.apartment == "Apt 4B"
    assert address.instructions == "Leave at front door"


def test_delivery_address_str_representation():
    """Test string representation of delivery address"""
    address = DeliveryAddress(
        street="123 Main St",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Test Country"
    )
    
    str_repr = str(address)
    assert "123 Main St" in str_repr
    assert "Test City" in str_repr
    assert "Test State" in str_repr
    assert "12345" in str_repr
    assert "Test Country" in str_repr


def test_delivery_address_str_representation_with_apartment():
    """Test string representation of delivery address with apartment"""
    address = DeliveryAddress(
        street="123 Main St",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Test Country",
        apartment="Apt 4B"
    )
    
    str_repr = str(address)
    assert "Apt 4B" in str_repr


def test_delivery_address_immutability():
    """Test that delivery address is immutable"""
    address = DeliveryAddress(
        street="123 Main St",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Test Country"
    )
    
    with pytest.raises(Exception):  # Either AttributeError or dataclasses.FrozenInstanceError
        address.street = "456 New St"