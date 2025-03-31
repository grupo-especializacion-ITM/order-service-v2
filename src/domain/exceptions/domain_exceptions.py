from typing import Any, Dict, Optional


class DomainException(Exception):
    """Base exception for all domain exceptions"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class OrderNotFoundException(DomainException):
    """Exception raised when an order is not found"""
    pass


class CustomerNotFoundException(DomainException):
    """Exception raised when a customer is not found"""
    pass


class InvalidOrderStateException(DomainException):
    """Exception raised when an operation cannot be performed due to invalid order state"""
    pass


class InventoryValidationException(DomainException):
    """Exception raised when inventory validation fails"""
    pass


class OrderCreationException(DomainException):
    """Exception raised when an order cannot be created"""
    pass


class OrderItemValidationException(DomainException):
    """Exception raised when order item validation fails"""
    pass