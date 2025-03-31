from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class CustomerDTO:
    id: Optional[UUID] = None
    name: str = ""
    email: str = ""
    phone: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None