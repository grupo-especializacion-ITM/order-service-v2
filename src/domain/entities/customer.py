from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime


@dataclass
class Customer:
    id: UUID
    name: str
    email: str
    phone: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @staticmethod
    def create(name: str, email: str, phone: str) -> "Customer":
        return Customer(
            id=uuid4(),
            name=name,
            email=email,
            phone=phone,
            created_at=datetime.now()
        )
