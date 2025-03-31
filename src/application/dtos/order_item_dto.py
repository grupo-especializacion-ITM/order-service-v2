from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class OrderItemDTO:
    id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    name: str = ""
    quantity: int = 0
    unit_price: float = 0.0
    total_price: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None