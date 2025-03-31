from dataclasses import dataclass
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime


@dataclass
class DeliveryAddressDTO:
    street: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = ""
    apartment: Optional[str] = None
    instructions: Optional[str] = None


@dataclass
class OrderTotalDTO:
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0


@dataclass
class OrderDTO:
    id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    items: List[Dict] = None
    status: str = "CREATED"
    delivery_address: Optional[DeliveryAddressDTO] = None
    total: Optional[OrderTotalDTO] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.items is None:
            self.items = []