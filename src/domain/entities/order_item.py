from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime


@dataclass
class OrderItem:
    id: UUID
    product_id: UUID
    name: str
    quantity: int
    unit_price: float
    total_price: float
    notes: Optional[str] = None
    created_at: datetime = datetime.now()

    @staticmethod
    def create(product_id: UUID, name: str, quantity: int, unit_price: float, notes: Optional[str] = None) -> "OrderItem":
        total_price = quantity * unit_price
        return OrderItem(
            id=uuid4(),
            product_id=product_id,
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            notes=notes
        )